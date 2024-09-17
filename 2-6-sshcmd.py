import os
import paramiko


def ssh_command(ip, port, user, cmd, password, key_file):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
      client.connect(ip, port=port, username=user, password=password)
    elif key_file:
      client.connect(ip, port=port, username=user, key_filename=key_file)
    else:
      raise RuntimeError("Neither password or key file was provided")

    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print("--- Output ---")
        for line in output:
            print(line.strip())


if __name__ == "__main__":
    user = input("Username: ") or "ec2-user"
    password = input("Password (leave empty to use keyfile): ")
    if not password:
      key_file = input("Path to keyfile: ") or "./BlackHatPython.pem"

      if not os.path.exists(key_file):
        raise ValueError(f"Key file {key_file} does not exist")

    ip = input("Enter server IP: ") or "ec2-13-61-0-148.eu-north-1.compute.amazonaws.com"
    port = input('Port: ') or 22
    cmd = input('Command: ') or 'id'
    ssh_command(ip, port, user, cmd, password, key_file)
    