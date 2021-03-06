import sys,os,thread

from PySide import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl


import numpy as np
# import pyuic generated user interface file
import template

from keithley6221 import *

PD = KEITHLEY6221()
PD.connect()

app = QtGui.QApplication(sys.argv)




def update_buffer():
	while 1:
		if myapp.fetch_data.checkState() and myapp.PD_armed==True:
			I,V = PD.get_PD()
			I=np.array(I)
			V=np.array(V)
			dI = np.diff(I)
			dV = np.diff(V)
			myapp.dIdV = dI/dV
			
			myapp.total_readings.setText('Loaded readings= %s'%(len(I)) )
			if(len(I)>3 and len(V)>3):
				myapp.c1.setData(I,V)
				j=V[:-1]
				sorter = j.argsort()
				k=dI/dV
				infinities = np.where(k==np.inf)[0]
				print 'dI/dV == infinity at ',infinities,k
				j=np.delete(j[sorter],infinities)
				k=np.delete(k[sorter],infinities)

				myapp.c2.setData(j   ,k)  #Plot dI/dV after removing last element of V for size matching
				dIdVfit = np.polyfit(j,k,2)
				myapp.dIdVfit.setText('dI/dV = %0.2e*V+%0.2e*V+%0.4e '%(dIdVfit[0],dIdVfit[1],dIdVfit[2]) )

				IVfit = np.polyfit(I,V,1)
				
				if IVfit[0]>1e40:
					myapp.IVfit.setText('Increase Voltage sensitivity'%(res) )
				else:
					myapp.IVfit.setText('V = %0.4e*I+%0.2e'%(IVfit[0],IVfit[1]) )

			myapp.I=I
			myapp.V=V
		time.sleep(0.5)


class MyMainWindow(QtGui.QMainWindow, template.Ui_MainWindow):
	def __init__(self, parent=None):
		super(MyMainWindow, self).__init__(parent)
		self.setupUi(self)
		self.I = []
		self.V = []
		self.dIdV = []
		self.vc_values = [1e-3,10e-3,100e-3,1,10,100]
		self.vcs = [self.v1,self.v2,self.v3,self.v4,self.v5,self.v6,]
		#self.timer = QtCore.QTimer()
		#self.timer.start(1000)
		#self.timer.timeout.connect(update) 
		self.IVgraph.setLabel('left', 'Voltage', units='V')
		self.IVgraph.setLabel('bottom', 'Current', units='A')

		self.dIdVgraph.setLabel('left', 'dI/dV', units='')
		self.dIdVgraph.setLabel('bottom', 'V', units='V')


		self.c1 = self.IVgraph.plot()
		self.c1.setPen((200,200,100))

		self.c2 = self.dIdVgraph.plot()
		self.c2.setPen((250,200,100))
		
		self.check_status()


	def check_status(self):
		self.nv_present = PD.nvpr()
		if(self.nv_present): self.nvpr.setStyleSheet("background-color:green;");
		else: self.nvpr.setStyleSheet("background-color:red	;");
		self.PD_armed = PD.PD_status()

		if(self.PD_armed):
			self.state.setStyleSheet("background-color:green;");
			self.state.setText("DISARM")
		else:
			self.state.setStyleSheet("background-color:red	;");
			self.state.setText("ARM")
	
	def toggle_state(self):
		if self.PD_armed:
			self.disarm_PD()
			self.PD_armed = False
			self.state.setStyleSheet("background-color:red	;");
			self.state.setText("ARM")
		else:
			self.arm_PD()
			self.PD_armed = True
			self.state.setStyleSheet("background-color:green;");
			self.state.setText("DISARM")
	
	def __del__(self):
			print 'BYE BYE'
			
	def start_measuring(self):
		print 'Measuring....'
		PD.init_measurements_PD()

	def dump_to_file(self):
		np.savetxt(self.filename.text()+'IV.txt',np.column_stack((self.I,self.V)) )
		np.savetxt(self.filename.text()+'dIdV.txt',np.column_stack((np.delete(self.V,-1),self.dIdV)) )
		
		print 'saved to file %s'%(self.filename.text())

	def set_pulse_width(self):
		PD.pulse_width = self.pulse_width.value()*1e-6
		print 'Pulse width changed to : %s %s S '%(PD.pulse_width,self.pulse_width.value()*1e-6)

	def disarm_PD(self):
		PD.abort_PD()	

	def arm_PD(self):
		PD.arm_PD()	

	def set_vc(self):
		for a in range(6):
			if self.vcs[a].isChecked():
				PD.voltage_compliance = self.vc_values[a]
				print 'Voltage sensitivity changed :',self.vc_values[a]
		
myapp = MyMainWindow()

thread.start_new_thread(update_buffer,())

myapp.show()
app.exec_()

print 'closing threads---'
PD.abort_PD()
time.sleep(2)

