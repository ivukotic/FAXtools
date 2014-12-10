import socket

UDP_IP = "134.79.200.87"
UDP_PORT = 993`
MESSAGE = "Hello, World!"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

