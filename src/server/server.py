import socket

from src.server.server_commands import ServerCommands

class ServerConfig():
    def __init__(self, port:int, message_port:int, buffer_size:int, file_port:int, file_buffer_size:int=8000000, file_dir:str = None,):
        self.PORT = port;
        self.MESSAGE_PORT = message_port
        self.FILE_PORT = file_port
        self.FILE_DIRECTORY = file_dir
        self.FILE_BUFFER_SIZE = file_buffer_size
        self.BUFFER_SIZE = buffer_size


class Server():
    def __init__(self,server_config:ServerConfig):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.SERVERCONFIG = server_config
    
    def run(self):
        self.sock.bind(('0.0.0.0',self.SERVERCONFIG.PORT))
        while True:
            print('-c exit to quit the server')
            text = input("server -> ")

            match text.lower():
                case "-c exit":
                    print("Exiting the server")
                    break;



