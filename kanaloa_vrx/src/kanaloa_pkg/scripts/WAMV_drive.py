#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from std_msgs.msg import Float32

from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import Imu

from math import radians
from math import cos
from math import sin


import sys
import time

class WAMV_Driver:

	def __init__(self, ros_node_name="WAMV_driver_node"):

		self.publishers = []
		self.subscribers = []
		
		self.ros_node_name = ros_node_name

		self.thrust_values = {}

		self.init_node()
		self.init_publishers()

		self.heading_rad = 0


	##################################################
	### Class Init Scripts
	##################################################
	
	def init_node(self):
		rospy.init_node(self.ros_node_name, anonymous=True)
		self.rate = rospy.Rate(10) # 10hz

	def init_publishers(self):
		self.publishers.append(self.create_publisher_object("/wamv/thrusters/left_front_thrust_cmd", Float32))
		self.publishers.append(self.create_publisher_object("/wamv/thrusters/left_rear_thrust_cmd", Float32))
		self.publishers.append(self.create_publisher_object("/wamv/thrusters/right_front_thrust_cmd", Float32))
		self.publishers.append(self.create_publisher_object("/wamv/thrusters/right_rear_thrust_cmd", Float32))

	
	##################################################
	### Create Publishers And Subscribers
	##################################################

	def create_publisher_object(self, pub_name, pub_type):
		rospy_publisher = rospy.Publisher(pub_name, pub_type, queue_size=10)
		publisher_object = {"topic": pub_name, "message": pub_type, "publisher": rospy_publisher, "node_type":"Publisher"}
		return publisher_object

	def get_publisher_topic(self, topic_name):
		return next(item for item in self.publishers if item["topic"] == topic_name)

	# def publisher():
	# 	rospy.Publisher("/wamv/thrusters/left_front_thrust_cmd", Float32, drive)
	# 	rospy.Publisher("/wamv/thrusters/left_rear_thrust_cmd", Float32, drive)
	# 	rospy.Publisher("/wamv/thrusters/right_front_thrust_cmd", Float32, drive)
	# 	rospy.Publisher("/wamv/thrusters/right_rear_thrust_cmd", Float32, drive)

	##################################################
	### Ta Da! Drive Function!
	##################################################

	def drive(self, heading, speed):
	#uses given heading and moves in that general direction
		# if -360 <= heading <= -180:
		# 	heading += 360
		# 	heading *= -1

		# if 180 <= heading <= 360:
		# 	heading -= 360

		# heading_rad = -1*heading*(3.14159/180)
		# heading_rad = radians(heading)

		# print(heading)

		global thrust_values

		thrust_values = 0

		self.thrust_values = {0}
		q1 = self.get_publisher_topic("/wamv/thrusters/right_front_thrust_cmd")
		q2 = self.get_publisher_topic("/wamv/thrusters/left_front_thrust_cmd")
		q3 = self.get_publisher_topic("/wamv/thrusters/left_rear_thrust_cmd")
		q4 = self.get_publisher_topic("/wamv/thrusters/right_rear_thrust_cmd")


		#NE direction
		if 0 < heading < 90:
			q_left = speed + heading/1000
			q_right = speed - heading/1000

			thrust_values["q1"] = q_right
			thrust_values["q2"] = q_left
			thrust_values["q3"] = q_left
			thrust_values["q4"] = q_right

		#SE direction
		elif -90 < heading < 0:
			q_left = speed + heading/1000
			q_right = speed - heading/1000

			thrust_values["q1"] = q_right
			thrust_values["q2"] = q_left
			thrust_values["q3"] = q_left
			thrust_values["q4"] = q_right

		#Forward
		elif heading == 0:

			thrust_values["q1"] = speed
			thrust_values["q2"] = speed
			thrust_values["q3"] = speed
			thrust_values["q4"] = speed

		#Backward
		elif heading == 180:

			thrust_values["q1"] = -speed
			thrust_values["q2"] = -speed
			thrust_values["q3"] = -speed
			thrust_values["q4"] = -speed

		#Right
		elif heading == 90:

			thrust_values["q1"] = speed
			thrust_values["q2"] = -speed
			thrust_values["q3"] = speed
			thrust_values["q4"] = -speed

		#Left
		elif heading == -90:

			thrust_values["q3"] = -speed
			thrust_values["q4"] = speed
			thrust_values["q2"] = -speed
			thrust_values["q1"] = speed

	
	# self.thrust_values = thrust_values	
	# q3["publisher"].publish(thrust_values["q3"])
	# q4["publisher"].publish(thrust_values["q4"])
	# q2["publisher"].publish(thrust_values["q2"])
	# q1["publisher"].publish(thrust_values["q1"])


wamv = WAMV_Driver()
wamv.drive(30, 0.75)
rospy.spin()