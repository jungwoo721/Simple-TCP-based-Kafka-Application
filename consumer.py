import socket
import sys
import time

def main():
    #====== get args for consumer.py =======
    if len(sys.argv) != 3:
        print("Usage: python consumer.py [Server_IP] [Server_PORT]")
        sys.exit(1)
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    #========================================

    # create consumer_socket, connect to server
    consumer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    consumer_socket.connect((server_ip, server_port))
    
    try:
        connection_message = consumer_socket.recv(1024).decode()
        print(connection_message)
        while True:
            consumer_socket.send('event request'.encode())  # "give me message" to server
            message = consumer_socket.recv(1024).decode()   # received message(event)
            print(message)
            time.sleep(1)
    except:
        # close socekt, inform that the socket is closed to the server
        consumer_socket.send('closed'.encode())
        consumer_socket.close()


if __name__ == '__main__':
    main()
