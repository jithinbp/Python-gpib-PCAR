from PySide import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import sys,os,csv,math

import numpy as np


# import pyuic generated user interface file
import template

app = QtGui.QApplication(sys.argv)

#-----------
#globals
k=1.38e-23
e=1.6e-19
delta=2e-3*e

z=0

T=3

def gamma2(u2):
	return (u2+z*z*(2*u2-1) )**2

def u2(E):
	return 0.5*(1+math.sqrt((E**2-delta**2)/(E**2)) )


def PA(E): #probability of andreev reflection
	if E<delta:
		t2=E*E + (delta*delta-E*E)*( (1+2*z*z)**2 )
		return (delta*delta)/t2
	else:
		u=u2(E)
		return u*(1-u)/gamma2(u)

def PB(E): #probability of ordinary reflection
	if E<delta:
		return 1-PA(E)
	else:
		u=u2(E)
		return (2*u-1)*(2*u-1)*(1+z*z)*z*z/gamma2(u)


def PC(E): #probability of transmission sans branch crossing
	if E<delta:
		return 0
	else:
		u=u2(E)
		return u*(2*u-1)*(1+z*z)/gamma2(u)


def PD(E): #probability of transmission with branch crossing
	if E<delta:
		return 0
	else:
		u=u2(E)
		return (1-u)*(2*u-1)*(z*z)/gamma2(u)


def term1(E,V):
		x = np.exp((E-e*V)/(k*T))
		
		return x
def integ(V):
	Energies1 = np.linspace(-0.1*e,0,1000)
	Energies2 = np.linspace(0,0.1*e,1000)
	dE = e/200
	x=0
	for E in Energies2:
		t1=term1(E,V)
		#print t1
		x+=dE*( t1/((1+t1)*(1+t1)*k*T)  )*(1+PA(E)-PB(E))
	for E in Energies1:
		t1=term1(-E,V)
		#print t1
		x+=dE*( t1/((1+t1)*(1+t1)*k*T)  )*(1+PA(E)-PB(E))
	return x

#-----------

class MyMainWindow(QtGui.QMainWindow, template.Ui_MainWindow):
	def __init__(self, parent=None):
		super(MyMainWindow, self).__init__(parent)
		self.setupUi(self)
		self.c1col=(250,200,50)
		self.c2col=(250,200,250)
		self.c3col=(20,230,50)
		self.fitcol=(255,10,10)
		
		self.ready = False
		self.x = []
		self.y = []
		self.dIdV = []
		self.end = 0

		self.graph.setLabel('left', 'differential resistance', units='.')
		self.graph.setLabel('bottom', 'Voltage', units='V')

		self.editedgraph.setLabel('left', 'differential Conductance', units='.')
		self.editedgraph.setLabel('bottom', 'Voltage', units='V')

		self.gc = self.editedgraph.plot()
		self.gc.setPen(self.c1col)

		self.fc = self.fitgraph.plot()
		self.fc.setPen(self.c1col)

		self.c = self.graph.plot()
		self.c.setPen(self.c1col)

		ar = np.loadtxt('28-Mar_19-58.txt')
		self.c.clear()
		self.gc.clear()
		self.x =np.concatenate(ar[:,0:1])
		self.y =np.concatenate(ar[:,1:2])
		
		self.c.setData(self.x,self.y)
		self.dIdV = 1.0/self.y

		self.gc.setData(self.x,self.dIdV)
		self.ready = True
		fifth = int(len(self.x)/5)
		val = np.average(self.dIdV[:fifth])
		print fifth,val
		self.gc.setData(self.x,self.dIdV/val)
		
		self.fx = np.linspace(0,15e-3,100)
		self.fy = [integ(a) for a in self.fx]
		self.fc.setData(self.fx,self.fy)
		
		
	def keyPressEvent(self, e):
		global z
		if e.key() == QtCore.Qt.Key_Escape:
			self.close()

		elif e.key() == QtCore.Qt.Key_Up:
			z+=0.01
			self.fy = [integ(a) for a in self.fx]
			self.fc.setData(self.fx,self.fy)

		elif e.key() == QtCore.Qt.Key_Down:
			z-=0.1
			if(z<0):z=0
			self.fy = [integ(a) for a in self.fx]
			self.fc.setData(self.fx,self.fy)

	def __del__(self):
		print 'BYE BYE'
			

		
myapp = MyMainWindow()


myapp.show()
app.exec_()


