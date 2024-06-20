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
    # Generate private key
    openssl genpkey -algorithm RSA -out private_key_$i.pem -pkeyopt rsa_keygen_bits:$key_size
    if [ $? -ne 0 ]; then
        echo "Error generating private key $i"
        exit 1
    fi

    # Extract public key
    openssl rsa -pubout -in private_key_$i.pem -out public_key_$i.pem
    if [ $? -ne 0 ]; then
        echo "Error generating public key $i"
        exit 1
    fi

    echo "Generated key pair $i"
done

echo "Successfully generated $num_keys key pairs of size $key_size bits."
