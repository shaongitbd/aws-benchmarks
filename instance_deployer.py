import boto3
import time
import paramiko
import os
import concurrent.futures
import subprocess
import sys

# AWS Configuration
region_name = 'us-east-1'
ami_id = 'ami-0e86e20dae9224db8'  #  your AMI id
key_name = 'pc4'  # Name of the key pair (AWS) .Just the name 
key_filename = 'pc4.pem'  # Path to your private key file
benchmark_script_path = 'run_benchmarks.sh'
security_group_id = 'sg-03133dbe75651ae98' 
volume_size_gb = 100  # Root volume size




# boto3 configuration

ec2_client = boto3.client('ec2', region_name=region_name)

def create_instance(instance_type):
    response = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[security_group_id],
    
        BlockDeviceMappings=[{
            'DeviceName': '/dev/sda1',  
            'Ebs': {
                'VolumeSize': volume_size_gb,  
                'DeleteOnTermination': True,
                'VolumeType': 'gp2'  
            }
        }],
        MinCount=1,
        MaxCount=1,
    )
    instance_id = response['Instances'][0]['InstanceId']
    print(f'Created instance: {instance_id}')
    return instance_id

def get_instance_ip(instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(f"instance public ip: {public_ip}")
    return public_ip

def wait_for_instance(instance_id):
    print('waiting for instance to be fully initialized ...')
    while True:
        try:
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            instance = response['Reservations'][0]['Instances'][0]
            instance_state = instance['State']['Name']
            
            if instance_state == 'running':
                print('Instance is running.')
                break
            elif instance_state == 'pending':
                print('Instance is initializing. Waiting...')
            else:
                print(f'Instance state: {instance_state}. Waiting...')
        
        except Exception as e:
            print(f'Error in checking instance state: {e}')
        
        time.sleep(10)
    time.sleep(120)

def run_benchmark(instance_ip,key_filename,local_results_dir,remote_directory):
    retries = 5
    for attempt in range(retries):
        try:
            # SSH connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(instance_ip, username='ubuntu', key_filename=key_filename)

            sftp = ssh.open_sftp()
            if not os.path.exists(local_results_dir):
                os.makedirs(local_results_dir)

            # Upload benchmark script
            print("uploading benchmark script")
            sftp.put(benchmark_script_path, '/home/ubuntu/run_benchmarks.sh')

            # Run benchmark script
            stdin, stdout, stderr = ssh.exec_command('chmod +x /home/ubuntu/run_benchmarks.sh')
            stdin, stdout, stderr = ssh.exec_command('/home/ubuntu/run_benchmarks.sh')

            # Wait for bash scipt complete
            exit_status = stdout.channel.recv_exit_status()  

            if exit_status == 0:
                print('Benchmark script executed successfully.')
                
                
                
                # Download result to own computer
                result_files = sftp.listdir(remote_directory)
            
                for result_file in result_files:
                    if result_file.endswith('.txt') or result_file.endswith('.xml') or result_file.endswith('.json'):
                        sftp.get(f'{remote_directory}/{result_file}', f'{local_results_dir}/{result_file}')
                
                break  
            else:
                print(f'Benchmark script failed with exit status {exit_status}.')
                error_output = stderr.read().decode()
                print(f'Error output: {error_output}')

            sftp.close()
            ssh.close()

        except (paramiko.SSHException, paramiko.ssh_exception.NoValidConnectionsError) as e:
            print(f'Attempt {attempt + 1} failed: {e}')
            time.sleep(30) 
    else:
        print('All attempts to run the benchmark script failed.')

def terminate_instance(instance_id):
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(f'Terminating instance: {instance_id}')

def benchmark_instance(instance_type):
    print(f"Spawning instance: {instance_type}")
    remote_directory = f'/home/ubuntu/benchmark_results'
    local_results_dir = f'./{instance_type}_results'
    
    # Launch and run the benchmark on this instance
    instance_id = create_instance(instance_type=instance_type)
    wait_for_instance(instance_id)
    instance_ip = get_instance_ip(instance_id)
    run_benchmark(instance_ip, key_filename, local_results_dir=local_results_dir, remote_directory=remote_directory)
    terminate_instance(instance_id)
    
    print(f"Benchmarking for {instance_type} completed.")
    
    return instance_type





def main():
    print("AWS Benchmark Script. Author: shaongit@gmail.com")
    
    #instance_list = ["m6i.large","m6i.xlarge","m6i.2xlarge"]
    #instance_list = ["m6a.large","m6a.xlarge","m6a.2xlarge"]
    #instance_list = ["m5.large","m5.xlarge","m5.2xlarge"]
    instance_list = ["m4.large","m4.xlarge","m4.2xlarge"]
    #instance_list = ["a1.medium","a1.large","a1.xlarge","a1.2xlarge","m7g.4xlarge"]
    #instance_list = ["r8g.2xlarge","m7i-flex.4xlarge","m7g.4xlarge","m6i.4xlarge","m6a.4xlarge","m5.4xlarge","m4.4xlarge"]

    # Define the number of threads (e.g., 5) to run concurrently
    max_workers = 4

    # Using ThreadPoolExecutor to handle multiple threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map instance_list to the benchmark_instance function
        results = list(executor.map(benchmark_instance, instance_list))
    
    print("Benchmarking Script has ended... Please check the benchmarks.")

if __name__ == "__main__":
    main()