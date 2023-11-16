import socket
import sys

def main():
    #====== get args for producer.py =======
    if len(sys.argv) != 3:
        print('Usage: python producer.py [Server_IP] [Server_PORT]')
        sys.exit(1)
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    #========================================
    
    # create producer_socket
    producer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        producer_socket.connect((server_ip, server_port))
        connection_message = producer_socket.recv(1024).decode()
        print(connection_message)
        while True:
            event = input()
            producer_socket.send(event.encode())
            print(f'{len(event)} events are created')
    except:
        # close socekt, inform that the socket is closed to the server
        producer_socket.send('closed'.encode())
        producer_socket.close()

if __name__ == '__main__':
    main()

