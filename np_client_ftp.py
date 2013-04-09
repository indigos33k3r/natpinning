#!/usr/bin/env python
from optparse import OptionParser
from threading import Thread
import socket
import struct

CALLBACK_PORT = 0
CALLBACK_IP = None

class FTPClient():
	def __init__(self,ftpserver,ftpport=21):
		self.FTPServer = ftpserver
		self.FTPPort = ftpport
		self.connect()
	#end def
	def receivemsg(self):
	 	while 1:
			indata = self.s.recv(1024).split('\r\n')
			for line in indata:
				x = line.split(" ",2)
				if x[0] == "220": #server banner
					print "Connected"
					self.s.send("USER anonymous\r\n")
				elif x[0] == "331": #send pass
					self.s.send("PASS natpin@work.net\r\n")
				elif x[0] == "230": #logged in succesfully
					cmd = "PORT " + CALLBACK_IP.replace(".",",")
					for val in self.ftpCalcPortNotation(CALLBACK_PORT):
						cmd = cmd + "," + str(val)
					print cmd
					self.s.send(cmd + "\r\n")
				elif x[0] == "200": #last cmd succesfull, send list
					self.s.send("LIST\r\n") #after this command is send, the servi will try connectin on callback port
	#end def
	def connect(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
		self.s.connect((self.FTPServer,self.FTPPort))
		self.sockThread = Thread(target=self.receivemsg)
		self.sockThread.start()
	#end def
	def ftpCalcPortNotation(self,port):
		x = port%256
		y = (port -x)/256
		return (y,x)
	#end def
#end class


#OPTIONS
parser = OptionParser()
parser.add_option('-s','--server', dest="ftpserver", help="FTP server")
parser.add_option('-i','--ip', dest="callbackip",help="IP to call back on")
parser.add_option('-p','--port', dest="callbackport",help="Port to call back on")

(opts,args) =parser.parse_args()

#MAIN
if (opts.ftpserver is None) or (opts.callbackip is None) or (opts.callbackport is None):
	print "Invalid args, add -h for options"
else:
	CALLBACK_PORT= int(opts.callbackport)
	CALLBACK_IP = opts.callbackip
	x = FTPClient(opts.ftpserver)
