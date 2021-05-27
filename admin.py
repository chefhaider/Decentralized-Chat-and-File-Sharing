from cryptography.fernet import Fernet

import socket
import threading






class Admin:

    def __init__(self,nick,recon,peers):

        

        self.key = Fernet.generate_key()
        self.f = Fernet(self.key)

        port = 1000
        self.connection = []

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1 )
        
        sock.bind(('0.0.0.0',port))
        sock.listen(1)

        sock.settimeout(0.5)


        print('> You were made the Admin')

        if recon:
            print('> Press Enter to Continue...')
        else:
            print('> You Started the Group chat')

        iThread1 = threading.Thread(target=self.sendMsg,args=(nick,))
        iThread1.daemon = True
        iThread1.start()

        while True:
            conn = None
            try:
                conn,addr = sock.accept()

                conn.send(self.key)
                
                name = self.f.decrypt(conn.recv(1024)).decode()
                
                alert = '> ' + str(addr) + ' joined as ' + name
                

                if not name in peers:
                    
                    peers.append(name)

                    for c in self.connection:
                        c.send(self.f.encrypt(alert.encode()))

                    print(alert)
                    

                    
                    
                    
                self.connection.append(conn)

                for c in self.connection:
                    names = ('\x11'+','.join(peers)).encode()
                    c.send(self.f.encrypt(names))
                
                iThread = threading.Thread(target=self.handler,args=(conn,name,peers))
                iThread.daemon = True
                iThread.start()

                

            except socket.timeout:
                pass

            

            



    def sendMsg(self,nick):

        while True:

            message =  input()

            if message == '$enable file sharing':

                file_name = input('> input file name: ') + '.txt'

                for c in self.connection:
                    c.send(self.f.encrypt(message.encode()))

                with open(file_name,'rb') as file:
                    file_data = file.read(1024)
                
                    for c in self.connection:
                        c.send(self.f.encrypt(file_data))

                    
            else:

                message = nick + ':>>' + message
                message = message.encode()
                for c in self.connection:
                    c.send(self.f.encrypt(message))



    def handler(self,conn,name,peers):

        while True:

            


            rcv_msg = conn.recv(1024)

            if not rcv_msg:
                self.connection.remove(conn)
                conn.close()

                alert = '> ' + str(name) + ' left'

                peers.remove(name)
                

                for c in self.connection:
                    c.send(self.f.encrypt(alert.encode()))
                    names = ('\x11'+','.join(peers)).encode()
                    c.send(self.f.encrypt(names))
                
                print(alert)
                break
            
            
            print(self.f.decrypt(rcv_msg).decode())

            

            for c in self.connection:
                c.send(rcv_msg)