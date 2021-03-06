#Commands for dealing with the ANC300 controller

import telnetlib, time, socket
import os,string
import numpy as np

from console_out import *

class KEITHLEY6221:
	def __init__(self):
		self.host    = '192.168.10.4'	#IP address for KEITHLEY 6221
		self.port	= 1394			#standard telnet console. 
		self.timeout = 30
		self.status=''
		self.identity=''
		self.connected=False
		self.PD_armed=False
		
		self.voltage_compliance=100e-3
		self.pulse_width = 100e-6

		
		self.style='\033[7;95m'
		self.text=Text()

	def connect(self):
		try:
			self.device = telnetlib.Telnet(self.host, self.port, self.timeout)
			self.identity = self.go('*IDN?')
			self.text.show(self.identity,'message')
			self.status	=	'connected'
			self.connected = True
			self.go(':TRAC:CLE')

		except socket.timeout:
			self.status = "socket timeout"
			self.identity = 'none'
			self.connected = False
		return self.identity
		
	def go(self,command):
		self.device.write(command+'\n')
		if command[-1]=='?':
			received = self.device.read_until('/700x', 2 ).split('/700x')[0]
			self.text.show(command+':'+received[:10]+'...','blue')
			return received
		else:
			self.text.show(command+':'+'\t\t\t|','blue')
			return True
		
	def clear(self):
		self.go('*CLS')
	

#-----------------------------------------------DIFFERENTIAL CONDUCTANCE----------------------------------------------

	def arm_DC(self):
		if self.status:
			self.go('SYST:COMM:SER:SEND "VOLT:RANG 2"')
			self.go('SYST:COMM:SER:SEND "VOLT:NPLC 1"')
			self.clear()
			rep = self.go('SOUR:DCONductance:NVPResent?')
			self.text.show('Serial connection check[dI/dV] :'+rep,'message')
			self.clear()
			self.go('SOUR:DCON:STARt -10e-6')
			self.go('SOUR:DCON:STEP 1e-6')
			self.go('SOUR:DCON:STOP 10e-6')
			self.go('SOUR:DCON:DELTa 1e-6')
			self.go('SOUR:DCON:DELay 0.002')
			self.go('SOUR:DCON:ARM')
			self.go('INIT:IMM')

	def disarm_DC(self):
			self.text.show('Disarming differential conductance','message')
			self.go("SOUR:SWE:ABOR")

	def get_DC(self):
		if self.status:

			self.clear()
			data = self.go('SENS:DATA?')	
		
			return data
		else:
			return 0

#|||||||||||||||||||||||||||||||------------DIFFERENTIAL CONDUCTANCE----------||||||||||||||||||||||||||||
			
			

#-----------------------------------------------PULSED DELTA----------------------------------------------
	def arm_PD(self):
		
		if self.status:
			self.go('SYST:COMM:SER:SEND "VOLT:NPLC 1"') #to nanovoltmeter
			self.go(':syst:comm:ser:send ":sens:volt:rang %s"'%(str(self.voltage_compliance))) 
			time.sleep(0.5)
			self.go('SOUR:PDEL:COUN INF')    #points
			
			
			self.go('SOUR:PDEL:WIDT %e'%(self.pulse_width))
			self.sdel = self.pulse_width/2.0+10e-6  # so that it is always > 55uS
			self.go('SOUR:PDEL:SDEL %e'%(self.sdel)) #source delay
			print self.pulse_width,self.sdel
			
			self.go('SOUR:PDEL:INT 5')    

			
			self.go('SOUR:PDEL:SWE ON')   
			self.go('SOUR:SWE:SPAC LIN')
			self.go('SOUR:CURR:STAR 1e-6')
			self.go('SOUR:CURR:STOP 100e-6')
			self.go('SOUR:CURR:STEP 1e-7') #stepsize .1uA
			self.go('SOUR:DEL 1e-1')
			
			self.go('SOUR:SWE:RANG BEST')
			self.go(':FORM:ELEM SOUR,READ')
			self.go('SOUR:PDEL:LME 1')
			self.go(':TRAC:CLE')
			self.text.show('Arming Pulse Delta ','message')
			self.go('SOUR:PDEL:ARM')
			time.sleep(2)
			self.PD_armed=True
	def init_measurements_PD(self):
		if self.status:
			self.clear()
			self.go(':TRAC:CLE')
			self.go('*CLS')
			self.go('INIT:IMM')

	def nvpr(self):
			return int(self.go('SOUR:DCONductance:NVPResent?'))

	def PD_status(self):
			self.PD_armed = int(self.go('SOUR:PDEL:ARM?'))
			return self.PD_armed
			
	def abort_PD(self):
			''' disarm pulse delta mode and return to normal state'''
			self.text.show('Disarming Pulse delta .','message')
			self.go("SOUR:SWE:ABOR")
			time.sleep(2)
			self.PD_armed=False

	def get_PD(self):
		if self.status:
			data=self.go(':trac:data?')
			if len(data)>4:
				data=data.split(',')
				n=1
				self.x_axis=[]
				self.y_axis=[]
				print data[0],data[1]
				while n<len(data)-2:
					self.x_axis.append( float(data[n]) )
					self.y_axis.append( float(data[n+1]) )
					n+=2
				
				return self.x_axis,self.y_axis
				
			return [[],[]]
		else:
			self.text.message(' not initialized','error',self.name+'  ',self.style)
			return [[],[]]

#|||||||||||||||||||||||||||||||||||||------------PULSED DELTA----------||||||||||||||||||||||||||||||||||||||||||


	def to_file(self):
		f=open('pd.txt','wt')
		for n in self.points:
			f.write('%s %s\n'%(n[0],n[1]) )
		print 'written to file'
		f.close()

