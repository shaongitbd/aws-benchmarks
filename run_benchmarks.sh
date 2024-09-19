#!/bin/bash

# Configuration
RESULTS_DIR="/home/ubuntu/benchmark_results"
GEEKBENCH_URL="https://cdn.geekbench.com/Geekbench-6.3.0-Linux.tar.gz"
GEEKBENCH_TAR="Geekbench-6.3.0-Linux.tar.gz"
GEEKBENCH_DIR="Geekbench-6.3.0-Linux"

# Create results directory
mkdir -p "${RESULTS_DIR}"

sudo apt-get update

# Creating 1 GB swap file
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Geekbench
echo "Downloading Geekbench..."
wget -O $GEEKBENCH_TAR $GEEKBENCH_URL
echo "Extracting Geekbench..."
tar -xzf $GEEKBENCH_TAR
cd $GEEKBENCH_DIR
./geekbench6 > "${RESULTS_DIR}/geekbench6_results.txt"



# Sysbench
echo "Starting Sysbench benchmark..."
sudo apt-get install -y sysbench
sysbench cpu --cpu-max-prime=20000 run > "${RESULTS_DIR}/sysbench_cpu_results.txt"
sysbench memory run > "${RESULTS_DIR}/sysbench_memory_results.txt"
echo "Sysbench benchmark completed."

# FIO
sudo apt install -y fio
fio --name=benchmark --ioengine=libaio --rw=randrw --rwmixread=70 --bs=4k --direct=1 --size=10G --numjobs=4 --runtime=300 --time_based --group_reporting --output="${RESULTS_DIR}/fio_results.txt"

echo "All benchmarks completed. Results saved in ${RESULTS_DIR}."

