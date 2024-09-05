import argparse
import sys
import socket
import threading

# All ascii that can be represented by 1 character
HEX_FILTER = "".join(
    [
        chr(i) if len(repr(chr(i))) == 3 else "🔚" if i == 0x0A else "."
        for i in range(256)
    ]
)


def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode(errors='replace')

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i : i + length])

        printable = word.translate(HEX_FILTER)
        hex = " ".join([f"{ord(c):02X}" for c in word])
        hexwidth = length * 3
        results.append(f"{i:04x}  {hex:<{hexwidth}}  {printable}")
    if show:
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection: socket.socket):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    return buffer


def response_handler(buffer):
    return buffer


def proxy_handler(
    client_socket: socket.socket, remote_host, remote_port, receive_first: bool
):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print(f"[<==] Sending {len(remote_buffer)} bytes to localhost.")
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print(f"[==>] Received {len(local_buffer)} bytes from localhost.")
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f"[<==] Sending {len(remote_buffer)} bytes to localhost.")
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[***] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"Problem on bind: {e}")

        sys.exit(1)

    print(f"[***] Listening on {local_host}:{local_port}")
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print(f"[***] Received incoming connection from {addr[0]}:{addr[1]}")

        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first),
        )
        proxy_thread.start()


def main():
    parser = argparse.ArgumentParser(description="TCP Proxy")

    # Adding positional arguments
    parser.add_argument("localhost", type=str, help="The local host address")
    parser.add_argument("local_port", type=int, help="The local port number")
    parser.add_argument("remote_host", type=str, help="The remote host address")
    parser.add_argument("remote_port", type=int, help="The remote port number")
    parser.add_argument(
        "receive_first",
        type=bool,
        help="Receive data first before sending (True/False)",
    )

    args = parser.parse_args()
    server_loop(
        args.localhost,
        args.local_port,
        args.remote_host,
        args.remote_port,
        args.receive_first,
    )


if __name__ == "__main__":
    main()
