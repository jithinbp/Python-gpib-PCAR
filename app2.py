'''
Python program to run a point contact spectroscopy setup
for extracting energy gaps in superconductors from dI/dV spectra
of metal-superconductor ballistic contacts
Author  : Jithin B.P, jithinbp@gmail.com
License : GNU GPL version 3
Started on october-2013
Last edit : 19-mar-2014, added stepper motor settings
*
'''
import sys,os,thread

from PySide import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl


import numpy as np
# import pyuic generated user interface file
import template

from keithley6221 import *		#the enclosed Class deals with the KEITHLEYs
from stepper import *			#this one handles the stepper motor
from lakeshore350 import *

app = QtGui.QApplication(sys.argv)



def update_readings_loop():
	while myapp.alive:
		if ( ((myapp.fetch_data.checkState() and myapp.DC.progress<100) or myapp.update_buffer_request) and myapp.DC_armed==True ):
			update_buffer()
			myapp.update_buffer_request = False
		#myapp.temp = myapp.LS.get_temp()
		time.sleep(0.5)

def update_buffer():
	if myapp.DC_armed==True:
		I,V = myapp.DC.get_DC()
		I=np.array(I)
		V=np.array(V)
		dI = np.diff(I)
		dV = np.diff(V)
		myapp.dIdV = dI/dV
		myapp.total_readings.setText('%s'%(len(I)) )
		if(len(I)>3 and len(V)>3):
			myapp.c1.setData(I,V)
			j=V[:-1]
			sorter = j.argsort()
			k=dI/dV
			k=k[sorter]
			j=j[sorter]
			
			infinities = np.where(k==np.inf)[0]
			print 'dI/dV == infinity at ',infinities
			j=np.delete(j,infinities)
			k=np.delete(k,infinities)
			if(len(j)>2):
				myapp.c2.setData(j ,k)  #Plot dI/dV after removing last element of V for size matching
				dIdVfit = np.polyfit(j,k,1)
				myapp.dIdVfit.setText('dI/dV = %0.2e*V+%0.4e '%(dIdVfit[0],dIdVfit[1]) )

				IVfit = np.polyfit(I,V,1)
			
				if IVfit[0]>1e40:
					myapp.IVfit.setText('Increase Voltage sensitivity' )
				else:
					myapp.IVfit.setText('V = %0.4e*I+%0.2e'%(IVfit[0],IVfit[1]) )

		myapp.I=I
		myapp.V=V


class MyMainWindow(QtGui.QMainWindow, template.Ui_MainWindow):
	def __init__(self, parent=None):
		super(MyMainWindow, self).__init__(parent)
		self.setupUi(self)
		self.I = []
		self.V = []
		self.temp = 0;
		self.progressBar.setValue(10)
		self.dIdV = []
		self.vc_values = [1e-3,10e-3,100e-3,1,10,100]
		self.vcs = [self.v1,self.v2,self.v3,self.v4,self.v5,self.v6,]
		self.DC_armed = False
		self.update_buffer_request = False
		self.IVgraph.setLabel('left', 'Voltage', units='V')
		self.IVgraph.setLabel('bottom', 'Current', units='A')

		self.dIdVgraph.setLabel('left', 'dI/dV', units='')
		self.dIdVgraph.setLabel('bottom', 'V', units='V')


		self.c1 = self.IVgraph.plot()
		self.c1.setPen((200,200,100))

		self.c2 = self.dIdVgraph.plot()
		self.c2.setPen((250,200,100))

		self.messages.horizontalScrollBar()
		self.stepper=STEPPER()
		if(not self.stepper.connected): self.messages.append('Stepper motor Failed')
		self.set_stepper_indicator()

		self.messages.append('Connecting to KEITHLEYs')
		vc=1		
		for a in range(6):
			if self.vcs[a].isChecked():
				vc = self.vc_values[a]

		self.pts = self.num_points.value()
		self.DC = KEITHLEY6221(self.current_start.value()*1e-3,	self.current_stop.value()*1e-3, self.pts, self.pulse_width.value()*1e-6,vc)
		print self.current_start.value()*1e-3,stepsize, \
				self.current_stop.value()*1e-3,self.pulse_width.value()*1e-6,vc
		self.DC.connect()
		self.check_status()
		self.messages.append('Connected')

		self.messages.append('Connecting to Temp controller')
		self.LS = LAKESHORE350()
		self.messages.append('Retrieving curve list')
		#self.LS.connect()
		#self.curvelist.addItems(self.LS.curve_mnemonics)
		
		self.alive = True
		self.timer = QtCore.QTimer()
		self.timer.start(100)
		self.timer.timeout.connect(self.update_values) 
		
	def update_values(self):
		self.progressBar.setValue(int(self.DC.progress))
		#self.temperature.setText(str(self.LS.input_num)+': '+self.temp + ' K')
			
#-------------------KEITHLEY functions=----------------------------------
	def check_status(self):
		self.nv_present = self.DC.nvpr()
		if(self.nv_present):self.nvpr.setStyleSheet("background-color:green;");
		else: self.nvpr.setStyleSheet("background-color:red	;");
		self.DC_armed = self.DC.DC_status()

		if(self.DC_armed):
			self.state.setStyleSheet("background-color:green;");
			self.state.setText("DISARM")
		else:
			self.state.setStyleSheet("background-color:red	;");
			self.state.setText("ARM")
	
	def toggle_state(self):
		if self.DC_armed:
			self.disarm_DC()
			self.state.setStyleSheet("background-color:red	;");
			self.state.setText("ARM")
		else:
			self.arm_DC()
			self.state.setStyleSheet("background-color:green;");
			self.state.setText("DISARM")
	
	def __del__(self):
			print 'BYE BYE'
			
	def start_measuring(self):
		print 'Measuring....'
		self.DC.init_measurements_DC()

	def dump_to_file(self):
		np.savetxt(self.filename.text()+'IV.txt',np.column_stack((self.I,self.V)) )
		np.savetxt(self.filename.text()+'dIdV.txt',np.column_stack((np.delete(self.V,-1),self.dIdV)) )
		
		print 'saved to file %s'%(self.filename.text())

	def set_pulse_width(self,val):
		self.DC.pulse_width = val
		print 'Pulse width changed to : %s '%(self.DC.pulse_width)

	def set_current_start(self,val):
		self.DC.DC_start_current = val
		print 'Pulse start current changed to : %s A '%(self.DC.DC_start_current)

	def set_current_stop(self,val):
		self.DC.DC_stop_current = val
		print 'Pulse stop current changed to : %s A '%(self.DC.DC_stop_current)

	def set_points(self,pts):
		self.pts = pts
		self.DC.DC_stepsize = abs(self.DC.DC_stop_current - self.DC.DC_start_current)/pts
		if(self.DC.DC_stepsize<1e-7): self.DC.DC_stepsize = 1e-7
		print 'Pulse stepsize current changed to : %s A '%(self.DC.DC_stepsize)


	def disarm_DC(self):
		self.DC.abort_DC()
		self.DC_armed = False	

	def arm_DC(self):
		self.DC.arm_DC()	
		self.DC_armed = True

	def set_vc(self):
		for a in range(6):
			if self.vcs[a].isChecked():
				self.DC.voltage_compliance = self.vc_values[a]
				print 'Voltage sensitivity changed :',self.vc_values[a]

	def update_buffer(self):
		self.update_buffer_request = True
		print 'Initated an update request'
	
#---------------------Stepper motor control functions--------------------------
	def stepper_fwd(self):
		self.stepper.forward()
		self.position.setText('Position: '+str(self.stepper.pos))
		self.set_stepper_indicator()

	def stepper_back(self):
		self.stepper.backward()
		self.position.setText('Position: '+str(self.stepper.pos))
		self.set_stepper_indicator()

	def enable_stepper(self):
		self.stepper.enable()
		self.set_stepper_indicator()
		
	def disable_stepper(self):
		self.stepper.disable()
		self.set_stepper_indicator()
	
	def set_stepper_indicator(self):
		val = self.stepper.steps[self.stepper.phase]
		up = "background-color:green;"
		dn = "background-color:grey;"
		self.a_1.setStyleSheet(dn);
		self.a_2.setStyleSheet(dn);
		self.a_3.setStyleSheet(dn);
		self.a_4.setStyleSheet(dn);
		if self.stepper.active:
			if val & 8: self.a_1.setStyleSheet(up);
			if val & 4: self.a_2.setStyleSheet(up);
			if val & 2: self.a_3.setStyleSheet(up);
			if val & 1: self.a_4.setStyleSheet(up);


#---------------------LakeShore functions-----------------------------------------
	def select_temperature_curve(self, choice):
		data = self.LS.curves[choice]
		self.LS.curve_num = data[1]
		self.LS.selected_curve = self.LS.curve_mnemonics[choice]
		print data

	def select_temperature_input(self, inp):
		self.LS.input_num = inp
		print self.LS.input_num

	def load_temperature_parameters(self):
		print 'setting input ',self.LS.input_num,' and curve ',self.LS.curve_num,self.LS.selected_curve
		msg = self.LS.load_parameters()
		self.messages.append(msg)
		
myapp = MyMainWindow()

thread.start_new_thread(update_readings_loop,())

myapp.show()
app.exec_()

print 'closing threads---'
myapp.alive=False
myapp.DC.abort_DC()

