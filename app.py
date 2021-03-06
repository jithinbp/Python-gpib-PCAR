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
from multi import *

app = QtGui.QApplication(sys.argv)



def update_readings_loop():
	while myapp.alive:
		if(((myapp.fetch_data.checkState() and myapp.DC.progress<100) or myapp.update_buffer_request) and myapp.armed in['DC','PD'] ):
			update_buffer()
			myapp.update_buffer_request = False

		time.sleep(0.2)

#def update_delta_loop():
#	while myapp.alive:
#		if (myapp.DC.armed == 'delta' ):
#			print 'VOltages :',myapp.DC.get_latest()
#
#		time.sleep(0.1)

def update_temperature_loop():
	while myapp.alive:
		try:
			if (myapp.DC.armed == 'delta' ):
				v = myapp.DC.get_latest().split(',')[0]
				print v
				myapp.res = '%0.4e'%(float(v)*1000)     #temporary. remove later
				myapp.res_yaxis = myapp.res_yaxis[1:]
				myapp.res_yaxis.append(float(myapp.res))
		except:
			pass
			
		myapp.temp = myapp.LS.get_temp() 
		try:
			val = float(myapp.temp)
			myapp.temp_yaxis = myapp.temp_yaxis[1:]
			myapp.temp_yaxis.append(val)
			myapp.temp_xaxis = myapp.temp_xaxis[1:]
			myapp.temp_xaxis.append(time.time() - myapp.start_time)
			myapp.temperature_file.write(str(time.time() - myapp.start_time) +'\t'+myapp.temp+'K'+'\n')
			myapp.c2.setData(myapp.temp_xaxis,myapp.temp_yaxis)	
		except:
			print myapp.temp
		
		myapp.c3.setData(myapp.temp_xaxis,myapp.res_yaxis)
		time.sleep(0.5)

def update_buffer():
	if myapp.armed != False:
		V,dIdV = myapp.DC.get_datapoints()
		dIdV=np.array(dIdV)
		V=np.array(V)
		if(len(dIdV)>3 and len(V)>3):
			myapp.c1.setData(V,dIdV)
			conductance = dIdV.mean()
			if conductance>1e40:
				myapp.dIdVfit.setText('Increase Voltage sensitivity' )
			else:
				myapp.dIdVfit.setText('C = %0.4e R = %0.4e'%(conductance, 1/conductance) )

		myapp.dIdV=dIdV
		myapp.V=V


class MyMainWindow(QtGui.QMainWindow, template.Ui_MainWindow):
	def __init__(self, parent=None):
		super(MyMainWindow, self).__init__(parent)
		self.setupUi(self)
		self.dIdV = []
		self.V = []
		self.temp = 0
		self.progressBar.setValue(100)
		self.vc_values = [1e-3,10e-3,100e-3,1,10,100]
		self.vcs = [self.v1,self.v2,self.v3,self.v4,self.v5,self.v6,]
		self.armed = False
		self.update_buffer_request = False
		self.temperature_file = open('temperature/'+time.strftime('%d-%h_%H-%M')+'.txt','wt')
		self.resistance_file  = open('res/'+time.strftime('%d-%h_%H-%M')+'.txt','at')
		self.comments_file = open('comments.txt','at')
		
		
		self.dIdVgraph.setLabel('left', 'dI/dV', units='')
		self.dIdVgraph.setLabel('bottom', 'V', units='V')
		self.temp_graph.setLabel('left', 'Temp', units='K')
		self.temp_graph.setLabel('bottom', 'Time', units='S')

		self.temp_res_graph.setLabel('left', 'Resistance', units='Ohm')
		self.temp_res_graph.setLabel('bottom', 'Temperature', units='K')

		self.start_time = time.time()
		self.temp_yaxis = [0 for a in range(60)]
		self.temp_xaxis = [(-30+a/2.0) for a in range(60)]
		self.res_yaxis = [0 for a in range(60)]
		
		self.res=''
		
		self.c1 = self.dIdVgraph.plot()
		self.c1.setPen((250,200,100))

		self.c2 = self.temp_graph.plot()
		self.c2.setPen((25,250,100))
		self.c2.setData(self.temp_xaxis,self.temp_yaxis)


		self.c3 = self.temp_res_graph.plot()
		self.c3.setPen((25,250,100))
		self.c3.setData(self.temp_xaxis,self.res_yaxis)

		self.messages.horizontalScrollBar()
		#---------------------ACTIVATE STEPPER MOTOR---------------
		self.stepper=STEPPER()
		if(not self.stepper.connected): self.messages.append('Stepper motor Failed')
		self.set_stepper_indicator()
		#---------------------ACTIVATE KEITHLEYs ------------------
		self.messages.append('Connecting to KEITHLEYs')
		vc=1		
		for a in range(6):
			if self.vcs[a].isChecked():
				vc = self.vc_values[a]

		self.pts = self.num_points.value()
		self.DC = KEITHLEY6221(self.current_start.value()*1e-3,	self.current_stop.value()*1e-3, self.pts, self.pulse_width.value()*1e-6,vc)
		print self.current_start.value()*1e-3,	self.current_stop.value()*1e-3, self.pts, self.pulse_width.value()*1e-6,vc
		self.DC.connect()
		self.check_status()
		self.messages.append('Connected')
		
		self.DC.arm_delta()
		#----------------------------ACTIVATE TEMPERATURE CONTROLLER-------
		self.messages.append('Connecting to Temp controller')
		self.LS = LAKESHORE350()
		self.messages.append('Retrieving curve list')
		self.LS.connect()
		self.curvelist.addItems(self.LS.curve_mnemonics)
		self.start_temperature=''
		
		self.alive = True
		self.timer = QtCore.QTimer()
		self.timer.start(100)
		self.timer.timeout.connect(self.update_values) 
		#-----------------ACTIVATE MULTIMETER--------------------(temp)
		self.multi = MULTI()
		self.multi.connect()
		
		
		
		
		
	def update_values(self):
		self.progressBar.setValue(int(self.DC.progress))
		if len(self.DC.error_buffer):
			m1 = self.DC.error_buffer.pop()
			if(m1[0]!='0'):
				self.messages.append(m1[0]+' : '+m1[1])
		self.temperature.setText(str(self.LS.input_num)+': '+self.temp + ' K')
		self.live_monitor.display(self.res)
		self.resistance_file.write('%s %s\n'%(self.temp,self.res))
			
#-------------------KEITHLEY functions=----------------------------------
	def check_status(self):
		self.nv_present = self.DC.nvpr()
		if(self.nv_present):self.nvpr.setStyleSheet("background-color:green;");
		else: self.nvpr.setStyleSheet("background-color:red	;");
		self.armed = self.DC.get_status()

		if(self.armed=='DC'):
			self.state_dc.setStyleSheet("background-color:green;");
			self.state_dc.setText("Rearm DC")
			self.messages.append('Differential conductance mode ready')
		else:
			self.state_dc.setStyleSheet("background-color:red;");
			self.state_dc.setText("Arm DC")

		if(self.armed=='PD'):
			self.state_pd.setStyleSheet("background-color:green;");
			self.state_pd.setText("Rearm PD")
			self.messages.append("I wouldn't be so sure yet")
		else:
			self.state_pd.setStyleSheet("background-color:red;");
			self.state_pd.setText("Arm PD")
	
	
	def __del__(self):
			print 'BYE BYE'
			
	def start_measuring(self):
		print 'Measuring....'
		self.DC.init_measurements()
		self.start_temperature = self.temp
		print 'started measurements at ',self.start_temperature,'K'

		filename = 'backups/'+self.DC.filename+'_'+self.start_temperature+'K'+'.txt'
		print 'dumping to backup file : ',filename
		self.backup_file = open(filename,'wt')



	def dump_to_file(self):
		filename = 'plots/'+self.DC.filename+'_'+self.start_temperature+'K'+'.txt'
		print 'dumping to file : ',filename
		np.savetxt(filename,np.column_stack((self.V,self.dIdV)) )
		self.messages.append('dumping to file : '+filename)
		self.comments_file.write(filename+' '+self.comments.text()+'\n')

	def set_pulse_width(self,val):
		self.DC.pulse_width = val*1e-6
		print 'Pulse width changed to : %s '%(self.DC.pulse_width)

	def set_current_start(self,val):
		self.DC.start_current = val*1e-3
		self.DC.set_stepsize()
		print 'Pulse start current changed to : %s A '%(self.DC.start_current)

	def set_current_stop(self,val):
		self.DC.stop_current = val*1e-3
		self.DC.set_stepsize()
		print 'Pulse stop current changed to : %s A '%(self.DC.stop_current)

	def set_points(self,pts):
		self.pts = pts
		self.DC.pts = pts
		self.DC.set_stepsize()
		print 'Pulse stepsize current changed to : %s A '%(self.DC.stepsize)


	def abort_all(self):
		self.DC.abort()
		self.armed = False
		self.messages.append('Abort called.  Rearm modes.')


	def arm_DC(self):
		self.abort_all()
		self.DC.arm_DC()	
		self.check_status()

	def arm_PD(self):
		self.abort_all()
		self.DC.arm_PD()	
		self.check_status()

	def arm_delta(self):
		self.abort_all()
		self.DC.arm_delta()	
		self.check_status()

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
#thread.start_new_thread(update_delta_loop,())
thread.start_new_thread(update_temperature_loop,())

myapp.show()
app.exec_()

print 'closing threads---'
myapp.alive=False
myapp.DC.abort()

