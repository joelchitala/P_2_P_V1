
from io import TextIOWrapper
import json
import os
import socket
import threading

from src.client.client_commands import ClientCommands
from src.parser.parser import Parser

class ServerAddress():
    def __init__(self,ip:str,port:int):
        self.IP = ip
        self.PORT = port
    
    def getAddr(self):
        return (self.IP,self.PORT)
    
class ClientConfig():
    def __init__(self, port:int, message_port:int, buffer_size:int, file_port:int, file_buffer_size:int=8000000, file_dir:str = None,):
        self.PORT = port;
        self.MESSAGE_PORT = message_port
        self.FILE_PORT = file_port
        self.FILE_DIRECTORY = file_dir
        self.FILE_BUFFER_SIZE = file_buffer_size
        self.BUFFER_SIZE = buffer_size
    

class Client():
    def __init__(self, client_config:ClientConfig):
        self.name = None
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.CLIENT_CONFIG = client_config
        
        self.parser = Parser()

    def printToConsole(self, message, is_command):
        if is_command:
            print(f"{self.name}: command -> {message}")
        else:
            print(f"{self.name}: {message}")
    
    def printRemoteMessageToConsole(self,data):
        print(f"\n{data['name']}: {data['message']}")
    
    def run(self):
        self.sock.bind(('0.0.0.0',self.CLIENT_CONFIG.PORT))

        message_thread = threading.Thread(target=self.message_listener,daemon=True)
        message_thread.start()

        file_thread = threading.Thread(target=self.file_listiner,daemon=True)
        file_thread.start()

        try:
            while True:
                print("Running client")

                name = None
                while True:
                    temp = input("Enter Name -> ")
                    if temp.strip() != "":
                        name = temp
                        break;
                    else:
                        print("Name can not be empty")
            
                self.name = name

                print('-c exit to quit the client')
                print(f"{name}:")
                while True:
                    text = input("-> ")
                    
                    is_command = False
                    command = None

                    if len(text) > 1:
                        if text[:2].strip().lower() == "-c":
                            is_command = True
                            command = text.strip().lower()

                    if is_command:
                        match text.lower().strip():
                            case ClientCommands.EXIT.value:
                                print(f"Exiting Client: {name}")
                                exit(1)
                            case _:
                                self.interpret(command=command)
                    else:
                        self.printToConsole(text, is_command)
        except:
            print("Error")
                

    def sendMessageTo(self, message, ip:str, port:int):
        data = {
            "name":self.name,
            "message":message,
        }

        address = (ip,port)

        self.sock.sendto(f"{json.dumps(data)}".encode(),address);
    
    def sendFileTo(self, file: TextIOWrapper, ip:str, port:int):
        broadcast_file = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        data = {
          "filename":os.path.basename(file.name),
          "filepath":file.name,
          "filesize":os.path.getsize(file.name)
        }

        broadcast_file.settimeout(2)
        broadcast_file.connect((ip,port))
        broadcast_file.send(f'{json.dumps(data)}'.encode())
        broadcast_file.send(f"{file.read(self.CLIENT_CONFIG.FILE_BUFFER_SIZE)}".encode())
        broadcast_file.settimeout(None)

    def file_listiner(self):
        file_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        file_socket.bind(('0.0.0.0',self.CLIENT_CONFIG.FILE_PORT))
        file_socket.listen()

        while True:
            data, address = file_socket.accept()
            file_data = data.recv(self.CLIENT_CONFIG.BUFFER_SIZE)
            file_data = json.loads(file_data.decode())

            file_content = data.recv(self.CLIENT_CONFIG.FILE_BUFFER_SIZE)
            file_content = file_content.decode()

            file_dir = self.CLIENT_CONFIG.FILE_DIRECTORY

            if file_dir is None:
                return;

            file_path = f"{file_dir}\\{file_data['filename']}"

            if os.path.exists(file_dir):
                file = open(file_path,"w+")
                file.write(file_content)
                file.close()
            else:
                raise Exception(f"Path: {file_path} does not exist")
                
            

    # def broadcast(self,name,message):
    #     for client in self.clients:
    #         address = (client["address"][0],int(client["message_port"]))
    #         self.sock.sendto(f"{name} -> {message}".encode(),address)

    def message_listener(self):
        message_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        message_socket.bind(('0.0.0.0',self.CLIENT_CONFIG.MESSAGE_PORT))

        while True:
            data, addr = message_socket.recvfrom(self.CLIENT_CONFIG.BUFFER_SIZE)
            data = json.loads(data.decode())
            self.printRemoteMessageToConsole(data)
    
    def interpret(self, command: str):
        print("-----Interpreting-----")

        array = self.parser.parse(command)

        for arr in array:
            root_command = arr["root_command"]

            if root_command is None:
                return
            
            root_command_content = root_command["value"]["content"]

            command_prefix = root_command_content.split(":")[0].lower()
            command_postfix = root_command_content.split(":")[1].lower()

            param_data = {}

            for parameter in arr["parameters"]:
                param_value = parameter["param"]["content"][1:]
                content_value = parameter["value"]["content"].strip('"')

                param_data[param_value] = content_value
                

            match command_prefix:
                case "show":
                    if command_postfix == "ip":
                        ip = socket.gethostbyname(socket.gethostname())
                        self.printToConsole(message= f" IPv4 Address: {ip}", is_command=True)

                    if command_postfix == "port":
                        self.printToConsole(message= f" Port: {self.CLIENT_CONFIG.PORT}", is_command=True)

                    if command_postfix == "message_port":
                        self.printToConsole(message= f" Port: {self.CLIENT_CONFIG.MESSAGE_PORT}", is_command=True)

                case "send":
                    if command_postfix == "text":
                        self.sendMessageTo(message=param_data["message"],ip=param_data["ip"],port=int(param_data["port"]))
                    
                    if command_postfix == "file":
                        file = open(param_data["file"])
                        self.sendFileTo(file= file , ip=param_data["ip"], port=int(param_data["port"]))


                    

            
