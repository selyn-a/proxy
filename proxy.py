import socket
import sys
import re
import os
import threading
import errno
import time
import json
import uuid

LOG_FLAG=False
BUFFER_SIZE = 2048

# implement this method that modifies the header as specified in the spec
# TODO: IMPLEMENT THIS METHOD
def modify_headers(client_data):
    ''' modify header as specified in the spec''' 
    return client_data # must return the new data with the updated header

# implement this method that parses server info from client data 
# must return 4 tuples of (server_ip, server_port, hostname, isCONNECT)
# TODO: IMPLEMENT THIS METHOD
def parse_server_info(client_data):
    ''' parse server info from client data and
    returns 4 tuples of (server_ip, server_port, hostname, isCONNECT) '''

    
    #replace below lines with correct values as specified in client_data
    server_ip = ""
    server_port = 0
    hostname = ""
    isCONNECT = False # if it is HTTP CONNECT request then set to True otherwise False
    return (server_ip, server_port, hostname, isCONNECT) 

# Creates a subdirectory for the hostname and a new json file
# Do not change this method
def create_log(hostname, incoming_header, modified_header, server_response):
    pathname = "Log/" + hostname
    if not os.path.exists(pathname):
        os.makedirs(pathname, 0o777, exist_ok=True)
        os.chmod('Log', 0o777)
        os.chmod(pathname, 0o777)
    
    json_dict = {
        'Incoming header': incoming_header,
        'Modified header': modified_header,
        'Server reponse received' : server_response
    }
    #Dir/Subdir/hostnameuuid.json
    with open(pathname + "/" + hostname + str(uuid.uuid1()) + ".json", "w+") as outfile:
        json.dump(json_dict, outfile, indent=4)

# Creates a subdirectory for the hostname and a new json file (Use this for CONNECT requests)
# Do not change this method
def create_log2(hostname, incoming_header, response_sent):
    pathname = "Log/" + hostname
    if not os.path.exists(pathname):
        os.makedirs(pathname, 0o777, exist_ok=True)
        os.chmod('Log', 0o777)
        os.chmod(pathname, 0o777)

    json_dict = {
        'Incoming header': incoming_header,
        'Proxy response sent': response_sent,
    }
    #Dir/Subdir/hostnameuuid.json
    with open(pathname + "/" + hostname + str(uuid.uuid1()) + ".json", "w+") as outfile:
        json.dump(json_dict, outfile, indent=4)
        
# A new thread should call this proxy method when starting
# TODO: IMPLEMENT THIS METHOD 
def proxy(client_socket,client_IP):
    with client_socket:
        request=client_socket.recv(1024)
        client_data_decoded = (request).decode('utf-8','backslashreplace')
        server_ip, server_port, hostname, isCONNECT=parse_server_info(client_data_decoded)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverside_socket:
            if(isCONNECT==False):
                serverside_socket.connect((server_ip, server_port))
                modified_client_data = modify_headers(request) # modified string is decoded string
                encoded_client_data = modified_client_data.encode('utf-8') #so you encode it 
                serverside_socket.sendall(encoded_client_data)

            else:
                serverside_socket.connect((server_ip, server_port))
                try:
                    serverside_socket.sendall(b'check') # this could be recv too
                    client_socket.sendall(b'HTTP 200 OK')
                except socket.error as e:
                    serverside_socket.close() # clean up your socket object
                    client_socket.sendall(b'HTTP 502 Bad Gateaway')
                return


    global LOG_FLAG
    pass

# TODO: IMPLEMENT THIS METHOD
def main():
    # check arguments
    if(len(sys.argv)!=2 and len(sys.argv)!=3):
        print("Incorrect number of arguments. \nUsage python3 http_proxy.py PORT")
        print("Incorrect number of arguments. \nUsage python3 http_proxy.py PORT Log")
        sys.exit()

    # enable logging
    if(len(sys.argv)==3 and sys.argv[2]=="Log"):
        global LOG_FLAG
        LOG_FLAG = True
        DIR_NAME = "./Log"  
        if not (os.path.isdir(DIR_NAME)):
            os.system("mkdir Log")
    


    ''' Create proper socket(s) and do proper binding.
        Create a new thread whenever new client's TCP connection request arrives
        and let the new thread call proxy method as the thread starts '''
    
    PROXY_HOST = '' # Symbolic name meaning all available interfaces
    PROXY_PORT = 56225 # Arbitrary non-privileged port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listening_socket:

        listening_socket.bind((PROXY_HOST, PROXY_PORT))
        listening_socket.listen(1)
        print("I opened a listening socket at port", PROXY_PORT)

        while True: # server has to be always running
            print("I am waiting for a client to do TCP connection request")
            servicing_socket, client_addr = listening_socket.accept()
            print("A new thread is handling the client")
            print(servicing_socket, client_addr)
            worker_thread = threading.Thread(target=proxy, args=(servicing_socket, client_addr))
            worker_thread.start()
    

# DO NOT CHANGE THIS METHOD
if __name__ == "__main__":
    main()