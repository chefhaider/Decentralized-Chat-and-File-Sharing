from cryptography.fernet import Fernet

import socket
import threading

from random import randrange
from time import sleep

from admin import Admin




class Peer:

    def __init__(self,nick,recon,peerList):

        
        
        
        
        self.file_sharing = False

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1 )
        self.iThread = None


        port = 1000
        sock.connect(('192.168.100.11',port))
        



        self.key =  sock.recv(1024)
        self.f = Fernet(self.key)

        sock.send(self.f.encrypt(nick.encode()))

        sock.settimeout(0.5)

        if recon:
            print('> Press Enter to Continue')
        else:
            print('> You Joined')


        self.iThread = threading.Thread(target=self.sendMsg,args=(sock,nick))
        self.iThread.daemon = True
        self.iThread.start()

        while True:
            try:
                
                rcv_msg = self.f.decrypt(sock.recv(1024))
                rcv_msg = rcv_msg.decode()

                if rcv_msg[0:1] == '\x11':
                    rcv_msg = rcv_msg[1:]
                    peerList.clear()
                    peerList += rcv_msg.split(',')

                elif rcv_msg == '$enable file sharing':

                    self.file_sharing = True

                elif self.file_sharing:

                    with open('received_file_by_'+nick+'.txt','wb') as file:
                        file.write(rcv_msg.encode())
                    
                    print('> file received')

                    self.file_sharing = False

                else:
                    
                    if not rcv_msg.split(':>>')[0] == nick:
                        print(rcv_msg)
                
            except socket.timeout:
                pass
            
           

    def sendMsg(self,sock,nick):
        
        while True:
            
            message = nick+':>>'+input()
            message = message.encode()

            try:
                sock.send(self.f.encrypt(message))
            except ConnectionResetError:
                break




if __name__ == "__main__":

    
    recon = False
    peerList = []
    nick = input('> Enter your nickname: ')

    
    try:
        while True:

            try:
                peer = Peer(nick,recon,peerList)
            except ConnectionRefusedError:
                admin = Admin(nick,recon,peerList)
            except ConnectionResetError:
                
                print('> Admin left')
                if peerList[0] == nick:
                    peerList.remove(nick)
                else:
                    sleep(.3)
                    
                recon = True

                continue
                
    except KeyboardInterrupt:
        print('You left the Chat\n')
        pass