
# Phoronix Test Suite
wget https://phoronix-test-suite.com/releases/phoronix-test-suite-10.8.4.tar.gz
tar zxf phoronix-test-suite-10.8.4.tar.gz
cd phoronix-test-suite
sudo ./install-sh

# Install the benchmark tests
sudo apt-get install -y  php-cli php-xml php-zip
sudo apt-get install -y expect
sudo apt install -y libopenblas-dev

phoronix-test-suite install pts/compress-7zip

expect_script=$(mktemp)

cat << EOF > $expect_script
#!/usr/bin/expect

set timeout -1

# Spawn the benchmark command
spawn phoronix-test-suite run pts/compress-7zip --auto-install

# Handle the prompts
expect {
    "Would you like to save these test results (Y/n):" {
        send "y\r"
        exp_continue
    }
    "Enter a name for the result file:" {
        send "7zip_benchmark_results.txt\r"
        exp_continue
    }
    "Enter a unique name to describe this test run / configuration:" {
        send "7zip_benchmark\r"
        exp_continue
    }
    "New Description:" {
        send "7zip\r"
        exp_continue
    }
    "Do you want to view the text results of the testing (Y/n):" {
        send "n\r"
        exp_continue
    }
    "Would you like to upload the results to OpenBenchmarking.org (y/n):" {
        send "n\r"
        exp_continue
    }
    eof
}
EOF

# executing 
chmod +x $expect_script
$expect_script
rm $expect_script

# moving to results dir
find -name "7zip_benchmark.log" -exec mv {} /home/ubuntu/benchmark_results/7zip_results.txt \;



# Create and execute the expect script for Phoronix Test Suite
expect_script=$(mktemp)

cat << EOF > $expect_script
#!/usr/bin/expect

set timeout -1

# Spawn the benchmark command
spawn phoronix-test-suite benchmark hpl --auto-install

# Handle the prompts
expect {
    "Would you like to save these test results (Y/n):" {
        send "y\r"
        exp_continue
    }
    "Enter a name for the result file:" {
        send "linpack_benchmark_results.txt\r"
        exp_continue
    }
    "Enter a unique name to describe this test run / configuration:" {
        send "linpack_benchmark\r"
        exp_continue
    }
    "New Description:" {
        send "linpack\r"
        exp_continue
    }
    "Do you want to view the text results of the testing (Y/n):" {
        send "n\r"
        exp_continue
    }
    "Would you like to upload the results to OpenBenchmarking.org (y/n):" {
        send "n\r"
        exp_continue
    }
    eof
}
EOF

# executing 
chmod +x $expect_script
$expect_script
rm $expect_script

find -name "linpack_benchmark.log" -exec mv {} /home/ubuntu/benchmark_results/linpack_results.txt \;



sudo apt install -y nodejs
sudo apt install -y npm 
sudo npm i pm2
mkdir server
cd server
npm init 
npm install express


cat <<EOL > index.js
const express = require('express');
const app = express();
const PORT = 4003;

app.get('/', (req, res) => {
  res.send('Hello world!');
});

app.listen(PORT, () => {
  console.log(\`Listening to port \${PORT}\`);
});
EOL

# Run the server
pm2 start index.js