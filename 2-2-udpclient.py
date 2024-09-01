import socket

target_host = "127.0.0.1"
target_port = 80

# AF_INET - ipv4 internet
# SOCK_DGRAM - user DATAGRAM protocol (udp) 
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# NOTE: this is needed but not in the book
client.bind((target_host, target_port))

# doesn't need to connect, can just send right away

client.sendto(b"AAABBBCCC",(target_host, target_port))

data, addr = client.recvfrom(4096)

print(data.decode())
client.close()