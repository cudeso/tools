#!/usr/bin/env python 
#
# Simple network server
#
# Simple network server for TCP or UDP. 
# Run as restricted user.
#  Based on http://ilab.cs.byu.edu/python/select/echoserver.html
# 
#   -p --port       Network port
#   -t --protocol   Network protocol (tcp or udp)
#   -l --logfile    Where to log
#   -i --ip         IP of server ('free' text, needed for logging)
#   -e --echo       Echo request back (default False)
#   -s --single     Take only one request
#
#
#  Koen Van Impe on 2014-12-29
#   koen dot vanimpe at cudeso dot be
#   license New BSD : http://www.vanimpe.eu/license
#
#

import select 
import socket 
import sys 
import re
import time, datetime
import argparse

backlog = 5 
size = 1024
host = '' 
# Leave host to '' to bind to any host


'''
    Log a message
'''
def log_message(file, message, address, ip, port, protocol):
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    remote_ip = str(address[0])
    remote_port = str(address[1])
    logline = "%s %s %s -> %s %s/%s : %s\n" % ( timestamp, remote_ip, remote_port, ip, protocol, port, message)
    file.write(logline)                    

'''
    Build the TCP server
'''
def tcp_server(port, logfile, echo, single, ip):
    print "TCP server on tcp/%s, logging to %s" % (port, logfile)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host,port))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    server.listen(backlog) 
    input = [server,sys.stdin] 
    running = 1 
    file = open(logfile, 'a')
    while running: 
        inputready,outputready,exceptready = select.select(input,[],[]) 
        for s in inputready: 
            if s == server: 
                # handle the server socket 
                client, address = server.accept() 
                input.append(client) 

            elif s == sys.stdin: 
                # handle standard input 
                junk = sys.stdin.readline() 
                running = 0 

            else: 
                # handle all other sockets 
                data = s.recv(size) 
                if data:
                    message = re.sub(r'\W+', '', data)
                    if len(message) > 0:
                        if echo == "echo":
                            s.send(message)
                        log_message(file, message, address, ip, port, 'tcp')
                    if single == True:
                        running = 0
                else: 
                    s.close() 
                    input.remove(s) 
    file.close()
    server.close()
    print "Stopped"



'''
    Build the UDP server
'''
def udp_server(port, logfile, echo, single, ip):
    print "UDP server on udp/%s, logging to %s" % (port, logfile)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind((host,port))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    input = [server,sys.stdin] 
    running = 1 
    file = open(logfile, 'a')
    while running: 
        inputready,outputready,exceptready = select.select(input,[],[]) 

        for s in inputready: 
            data = s.recvfrom(size)
            if data:
                message = re.sub(r'\W+', '', data[0])
                if len(message) > 0:
                    if echo == "echo":
                        s.sendto(message, data[1])
                    log_message(file, message, data[1], ip, port, 'udp')
                if single == True:
                    running = 0
            else: 
                s.close()
    file.close()
    server.close()                        
    print "Stopped"



def main():
    parser = argparse.ArgumentParser(description='Simple network server', epilog='Koen Van Impe - koen.vanimpe@cudeso.be')
    parser.add_argument('-p', '--port' , action="store", type=int, required=True, help="Network port (eg. 23, 80, 161, ...)")
    parser.add_argument('-t', '--protocol' , action="store", choices=['tcp', 'udp'], required=True, help="Protocol (tcp or udp")
    parser.add_argument('-l', '--logfile' , action="store", required=True, help="Where to log the connections")
    parser.add_argument('-i', '--ip' , action="store", required=True, help="IP of the server (for logging, no checks)")
    parser.add_argument('-e', '--echo' , action="store", help="Echo server or reply", default="echo")
    parser.add_argument('-s', '--single' , action="store_true", help="Single reply and stop", default=False)
    args=parser.parse_args()  
    port = args.port
    if (not(port >= 0 and port <= 65535)):
        sys.exit("Invalid port rage %s" % port)
    protocol = args.protocol
    logfile = args.logfile
    echo = args.echo
    single = args.single
    ip = args.ip

    if protocol == "tcp":
        tcp_server(port, logfile, echo, single, ip)
    elif protocol == "udp":
        udp_server(port, logfile, echo, single, ip)
    else:
        sys.exit("Invalid protocol %s" % protocol)


'''
 Jump to the main function
'''
if __name__ == "__main__":
  main()