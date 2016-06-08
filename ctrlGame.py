import sys
import socket


if __name__ == "__main__":
    if len(sys.argv) != 3 :
        print("Usage: python falppybirdRemoteCtrl.py <target ip> <port>")
        exit(-1)    
      
    HOST = sys.argv[1]
    PORT = sys.argv[2]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    
    sock.connect((HOST, int(PORT)))  
    print "Host %s connected\n" % (HOST)
    
    while True:  
        inputStr = raw_input("Enter the cmd: 1. start game; 2. stop game ");
        if len(inputStr) != 1 or int(inputStr)<1 or int(inputStr)>2:
            print "input error"
            continue
        try:  
            sndLen = sock.send( inputStr.ljust(16));
        except socket.error, e:
            print "Destination connection snd error"
        except Exception as ex:  
            print "Destination connection broken"
            break
        except KeyboardInterrupt:  
            print "Interrupted!"  
            break
        if(inputStr == "2"):
            break
    sock.close()

