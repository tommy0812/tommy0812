''' 
Traffic Monitor Detector (ISK) for BM-201" : 2020/04/30
ex0:
Hardware: Batman-201 ISK

V6: Point Cloud Spherical
	v6 structure: [(range,azimuth,elevation,doppler),......]
	
V7: Target Object List
	V7 structure: [(tid,posX,posY,velX,velY,accX,accY,posZ,velZ,accZ),....]
	
V8: Target Index
	V8 structure: [id1,id2....]
	
V9:Point Cloud Side Info
	v9 structure: [(snr,noise'),....]

(1)Download lib:
install:
~#sudo pip intall mmWave
update:
~#sudo pip install mmWave -U
'''

import serial
import numpy as np
from mmWave import trafficMD
import time
import os

os.system("sudo chmod 777 /dev/ttyUSB1")
port = serial.Serial("/dev/ttyUSB1",baudrate = 921600, timeout = 0.5)
tmd = trafficMD.TrafficMD(port)

def uartGetdata():
	# print("mmWave: {:} example:".format(name))
	port.flushInput()

	start = time.time()
	#hdr = tmd.headerShow()
	(dck,v6,v7,v8,v9)=tmd.tlvRead(False)

	dic = {"numObj": 0}
	dic_empty = {}
	out_sfldx = 2
	list_x = []
	list_y = []
	list_velocity = []
	list_r = []

	if dck:
		# print("V6:V7:V8:V9 = length([{:d},{:d},{:d},{:d}])".format(len(v6),len(v7),len(v8),len(v9)))
		if len(v6) != 0:
			# print("V6: Point Cloud Spherical v6:len({:d})-----------------".format(len(v6)))
			#[(range,azimuth,elevation,doppler),......]
			for id, element in enumerate(v6):
				# print('id', id)
				# print('element', element)

				r = v6[id][0]
				azimuth_angle = v6[id][1]     #az: azimuth   Theta <Theta Obj ->Y Axis 
				theta_angle = v6[id][2]       #el: elevation Phi <Theta bottom -> Obj
				velocity = v6[id][3]

				z = r * np.sin(theta_angle)                      #r * sin(Phi)
				x = r * np.cos(theta_angle) * np.sin(azimuth_angle) #r * cos(Phi) * sin(Theta)
				# v_x = velocity * np.sin(azimuth_angle) #r * cos(Phi) * sin(Theta)
				y = r * np.cos(theta_angle) * np.cos(azimuth_angle) #r * cos(Phi) * cos(Theta)
				# v_y = velocity * np.cos(azimuth_angle) #r * cos(Phi) * cos(Theta)

				list_x.append(x)

				list_y.append(y)

				list_velocity.append(velocity)
					
				list_r.append(r)

				dic['numObj'] = len(v6)

			dic['doppler'] = np.array(list_velocity)
			dic['range'] = np.array(list_r)
			dic['x'] = np.array(list_x)
			dic['y'] = np.array(list_y)

			print('numObj:', dic['numObj'])
			print('x', x)
			print('y', y)
			print("range",range)

	end = time.time()
	# print('IWR6843_time:', (end - start))	
	# print('IWR6843_fps:', 1/(end - start))
	return dic_empty , dic, out_sfldx
if __name__ == "__main__":
	while (1):
		uartGetdata()






