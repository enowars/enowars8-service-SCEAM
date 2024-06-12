import paramiko
from scp import SCPClient
import os
# TODO test


def create_ssh_client(address, username, password=None, key_filename=None):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if key_filename:
        ssh.connect(address, username=username, key_filename=key_filename)
    else:
        ssh.connect(address, username=username, password=password)
    return ssh


def download_files(ssh_client, file_paths, local_folder):
    with SCPClient(ssh_client.get_transport()) as scp:
        for file_path in file_paths:
            local_path = os.path.join(
                local_folder, os.path.basename(file_path))
            scp.get(file_path, local_path)


def main(addresses, file_paths, password=None, key_filename=None):
    for addr in addresses:
        username, address = addr.split('@')
        local_folder = os.path.join(os.getcwd(), address)
        os.makedirs(local_folder, exist_ok=True)

        print(f"Connecting to {address} as {username}")
        ssh_client = create_ssh_client(
            address, username, password, key_filename)
        try:
            download_files(ssh_client, file_paths, local_folder)
            print(f"Files downloaded to {local_folder}")
        except Exception as e:
            print(f"Error downloading files from {address}: {e}")
        finally:
            ssh_client.close()


if __name__ == "__main__":
    # Example usage
    addresses = ["user1@192.168.1.1", "user2@192.168.1.2"]
    file_paths = ["/remote/path/to/file1.txt", "/remote/path/to/file2.txt"]

    # Optionally, set password or key_filename for SSH authentication
    password = None
    # Set this if using key authentication
    key_filename = "/path/to/your/private/key"

    main(addresses, file_paths, password, key_filename)
