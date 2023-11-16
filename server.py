import socket
from queue import Queue
from threading import Thread
import time
import sys

IP = ""
PRODUCER_PORT = 0
CONSUMER_PORT = 0

event_queue = Queue()
consumer_count = 0
consumer_online = 0

def producer_worker():
    # connect producer
    producer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    producer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    producer_socket.bind((IP, PRODUCER_PORT))
    producer_socket.listen(5)
    
    try:
        # receive events from producer, put them into event_queue
        producer_connection_socket, _ = producer_socket.accept()
        print('[Producer connected]')
        producer_connection_socket.send('Connected, producer'.encode())
        while True:
            events = producer_connection_socket.recv(1024).decode()
            if not events == 'closed':
                for i in range(len(events)):    # put events into event_queue
                    event_queue.put(events[i])
                if len(events) != 0:
                    print('[Events created]')
                    print(f'[Remain events: {event_queue.qsize()}]')
            else:   # if producer.py is termated, break -> finally -> print 'disconnected'
                break
    finally:
        print('[Producer disconnected]')
        producer_socket.close()
        producer_connection_socket.close()
        

def consumer_worker(consumer_connection_socket, consumer_name):  
    global consumer_online  # to check # of consumers online
    try:
        consumer_connection_socket.send(f'Connected, {consumer_name}'.encode())
        while True:
            req = consumer_connection_socket.recv(1024).decode()
            
            if req == 'event request':
                if event_queue.empty():
                    message = 'No event in queue'
                else:
                    event = event_queue.get()
                    message = f'Event {event} is processed in {consumer_name}'
                consumer_connection_socket.send(message.encode())
                print(f'[Remain events: {event_queue.qsize()}]')
                
            elif req == 'closed':   # if consuemr.py terminated, break -> finally -> print 'disconnected'
                break
    finally:  
        consumer_connection_socket.close()
        consumer_online -= 1
        print(f'[C{consumer_name[1:]} disconnected]')  ## for uppercase 'C' ..
        print(f'[{consumer_online} consumers online]')
        
        
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python server.py [IP] [PRODUCER_PORT] [CONSUMER_PORT]')
        sys.exit(1)
        
    # get args for server.py
    IP = sys.argv[1]
    PRODUCER_PORT = int(sys.argv[2])
    CONSUMER_PORT = int(sys.argv[3])
        
    event_queue = Queue()
    consumer_count = 0
    consumer_online = 0
    

    # thread for producer
    producer_thread = Thread(target=producer_worker)
    producer_thread.start()
    
    # listen for consumer connection
    consumer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    consumer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    consumer_socket.bind((IP, CONSUMER_PORT))
    consumer_socket.listen(5)
    
    # thread for consumer
    try:
        while True:            
            consumer_connection_socket, _ = consumer_socket.accept()
            consumer_count += 1
            consumer_online += 1
            consumer_name = f'consumer {consumer_count}'
            consumer_name_uppercase = f'Consumer {consumer_count}'
            print(f'[{consumer_name_uppercase} connected]')
            print(f'[{consumer_online} consumers online]')
            consumer_thread = Thread(target=consumer_worker, args=(consumer_connection_socket, consumer_name,))
            consumer_thread.start()
    except:
        consumer_socket.close()
        