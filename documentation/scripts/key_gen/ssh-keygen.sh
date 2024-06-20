#!/bin/bash

# Check for the correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <number_of_keys> <key_size>"
    exit 1
fi

# Assign arguments to variables
num_keys=$1
key_size=$2

# Loop to generate the specified number of keys
for ((i=1; i<=num_keys; i++))
do
    # Generate key pair using ssh-keygen
    ssh-keygen -t rsa -b $key_size -f "key_$i" -N "" -q > /dev/null
    if [ $? -ne 0 ]; then
        echo "Error generating key pair $i"
        exit 1
    fi

    echo "Generated key pair $i"
done

echo "Successfully generated $num_keys key pairs of size $key_size bits."
