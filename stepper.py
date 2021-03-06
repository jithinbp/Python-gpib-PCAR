'''
Python program to communicate with microHOPE based stepper motor controller
Author  : Jithin B.P, jithinbp@gmail.com
License : GNU GPL version 3
Started on 17-March-2014
Last edit : 19-March-2014
*
'''
import serial,time

class STEPPER:
	FORWARD=chr(1)
	BACKWARD=chr(2)
	ENABLE=chr(3)
	DISABLE=chr(4)
	STATUS=chr(5)
	pos=0
	phase=0
	active=True
	steps=[12,6,3,9]
	connected = False
	def __init__(self):
		try:
			self.dev =  serial.Serial('/dev/ttyACM0', 38400, stopbits=1, timeout = 1.0)
			self.connected=True
			print self.dev, 'stepper motor activated'
			self.status()
			print self.steps[self.phase]
		except:
			print 'failed to activate stepper motor communications'

	def forward(self):
		if not self.connected: return

		if self.active:
			self.dev.write(self.FORWARD)
			self.pos+=1
			self.phase+=1
			if(self.phase==4): self.phase=0
		else:
			print 'Enable stepper motor first'
			
	def backward(self):
		if not self.connected: return

		if self.active:
			self.dev.write(self.BACKWARD)
			self.pos-=1
			self.phase-=1
			if(self.phase==-1): self.phase=3
		else:
			print 'Enable stepper motor first'

	def enable(self):
		if not self.connected: return

		self.dev.write(self.ENABLE)
		self.status()

	def disable(self):
		if not self.connected: return

		self.dev.write(self.DISABLE)
		self.status()

	def status(self):
		if not self.connected: return

		self.dev.write(self.STATUS)
		x=self.dev.read(2)
		a=0
		if(len(x)==2):
			a = ord(x[0])
			self.active=(ord(x[1])!=0)
		self.phase = self.steps.index(a)
		print 'stepper state ',a,self.active,self.phase
		return a
