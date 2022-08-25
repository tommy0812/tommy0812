#!/usr/bin/env python3
import os
import sys
import cv2
import time
import math
import numpy as np
import rospy
from ti_radar.msg import radar
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import MultiArrayDimension

"""
data[0]=num of obj
data[1]=x
data[2]=y
data[3]=depth
data[4]=snr
"""

class radar_points:
    def img_callback(self,data):
        try:
            self.cv_image = self.bridge.imgmsg_to_cv2(data,desired_encoding="passthrough")
        except CvBridgeError as e:
            print(e)

    def __init__(self):
        rospy.init_node('radar', anonymous=True)
        self.bridge=CvBridge()
        self.image=rospy.Subscriber("/usb_cam/image_raw",Image,self.img_callback)
        self.sub = rospy.Subscriber("radar_raw",radar,self.radar_raw_callback)

        self.list_pub = rospy.Publisher("radar_depth",Float32MultiArray,queue_size = 1)
        self.radar_points_demo_pub = rospy.Publisher("radar_points_demo",Image,queue_size = 1)
        
        self.range_list = Float32MultiArray()
        self.range_list.data = []
        self.snr = 130

        # Parameter for RAV4_RSU 640*360 20201216
        self.fx = 481.097434
        self.fy = 487.495792
        self.ox = 319.968559
        self.oy = 184.946026
        self.distCoeff = np.array([4.6893478978788754e-02, -1.4879514064553304e-01,
                                    -1.1199343363913639e-03, -1.7156348260077375e-05,
                                    9.1628133582285928e-02])
        self.image_width = 640
        self.image_height = 360

        """ X + 10 degrees, points go up in image
            Y + 10 degrees, points go right in image """
        self.rotation_matrix =np.array([[ 0.9986295347545737, 0.0, -0.05233595624294383    ],
                                        [ 0.001369995621214652, 0.9996573249755571, 0.026141073709985894    ],
                                        [ 0.052318022017859046, -0.026176948307873153, 0.9982873293543425    ]]) #Y:-3 DEGREES X: -1.5 DEGREES

        self.translation_matrix = np.array([0,0.1,0])

        self.radar_data = []
        self.depth_image = np.zeros((self.image_height,self.image_width))
        self.cv_image = np.ones((self.image_height, self.image_width,3)).astype(np.uint8)
        self.img = np.ones((self.image_height, self.image_width,3)).astype(np.uint8)
    def radar_raw_callback(self,data):
        # print("Callback :",data.numObj,len(data.x),len(data.y),len(data.range),len(data.peakVal))
        self.radar_data=[data.numObj,data.x,data.y,data.range,data.peakVal] # here peakVal is snr
        self.point_to_img(self.radar_data)
        self.publish_data()

    def point_to_img(self,data):
        self.img = self.cv_image
        self.detection = []
        self.depth_image = np.zeros((self.image_height,self.image_width))
        if (len(data[1]) == len(data[2]) and len(data[1]) > 0):
            for i in range(len(data[1])):
                if data[2][i] >0:
                    radar_coor = np.array([data[1][i],0,data[2][i]])
                    # print("radar_coor:",radar_coor)
                    radar_camera_coordinate = self.rotation_matrix.dot(radar_coor)+self.translation_matrix
                    # print("radar_camera_coordinate",radar_camera_coordinate)
                    temp_x = radar_camera_coordinate[0]/radar_camera_coordinate[2]
                    temp_y = radar_camera_coordinate[1]/radar_camera_coordinate[2]

                    r2 = temp_x * temp_x + temp_y * temp_y
                    tmpdist = 1 + self.distCoeff[0]*r2 + self.distCoeff[1]*r2*r2 + self.distCoeff[4]*r2*r2*r2
                    
                    r_image_x =  temp_x * tmpdist + 2 * self.distCoeff[2] * temp_x * temp_y + self.distCoeff[3]* (r2 + 2 * temp_x * temp_x)
                    r_image_y =  temp_y * tmpdist +self.distCoeff[2] * (r2 + 2 * temp_y * temp_y) + 2 * self.distCoeff[3] * temp_x * temp_y
                    r_image_x = int(self.fx * r_image_x + self.ox)
                    r_image_y = int(self.fy * r_image_y + self.oy)

                    if ( r_image_x >=0 and r_image_x < 640  and r_image_y >=0 and r_image_y < 360):
                        self.depth_image[r_image_y][r_image_x] = data[3][i]
                            
                        if (data[3][i] > 0): # and data[4][i] > self.snr):
                            self.detection.append(r_image_x)
                            self.detection.append(r_image_y)
                            self.detection.append(data[3][i])
                            self.detection.append(data[4][i]) # not peakval -> snr
                      

                    """ Plot points <30m """
                    if data[3][i]>0 and data[3][i]<30:
                        # print("Depth:", round(data[3][i],2), "SNR:",data[4][i])
                        cv2.circle(self.img,(r_image_x, r_image_y),2,(0,255,255),-1)
                        cv2.putText(self.img,str(round(data[3][i],1)), (r_image_x-20,r_image_y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,255,255),1)      
                    self.radar_points_demo_pub.publish(self.bridge.cv2_to_imgmsg(self.img.astype(np.uint8),'bgr8'))


        self.range_list.layout.dim = []
        self.range_list.layout.dim.append(MultiArrayDimension())
        self.range_list.layout.dim[0].label = "width"
        self.range_list.layout.dim[0].size = len(self.detection)
        self.range_list.layout.dim[0].stride = 0
        self.range_list.layout.data_offset=3
        self.range_list.data=self.detection

    def publish_data(self):
        self.list_pub.publish(self.range_list)

if __name__=='__main__':
    try:
        radar_point = radar_points()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
