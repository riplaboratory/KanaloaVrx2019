#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from std_msgs.msg import Float32

from geographic_msgs.msg import GeoPoseStamped
from geographic_msgs.msg import GeoPath

from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import Imu

from tf.transformations import euler_from_quaternion, quaternion_from_euler

# Import Custom Services, add_way_point, way_point_cmd
from way_point_wamv.srv import *

from math import radians
from math import atan2
from math import cos
from math import sin
from math import acos
from math import asin
from math import degrees
from math import sqrt

import sys
import time


class WAMV_Way_Point:
	
	def __init__(self, ros_node_name="wamv_navigation_node"):

		self.ros_node_name = ros_node_name

		self.navigation_indicator = True

		# Thrust Values
		self.thrust_values = {}

		# Queued Coordinates And Station Keeping List
		self.queued_coordinates = []
		self.queued_station_keep_times = [] 

		# Manual Offset If IMU heading is off 
		self.imu_degree_offset_bias = 0

		# IMU Orientation, either "ENU" or "NED"
		self.imu_orientation = "ENU"

		# List Of All Thruster Publishers And Anysubscrbers
		self.publishers = []
		self.subscribers = []

		# Current Coordinate and Next Desire Coordinates List
		self.desired_coordinates = []
		self.current_coordinates = []

		# Station Keep Timer
		self.station_keep_timer = 0 			# Will hold the time in minutes to station keep at next desired coordinates 
		self.station_keep_end_time = 0			# Will hold the actual time (in seconds) to stop station keeping
		self.station_keep_end_time_set = False 	# When False, the station keep end time has not been set yet because point was not reached yet

		# Curent Degree Offset And Distance To Next Coordinate
		self.degree_offset = 0
		self.distance = 0

		self.max_thrust = 1 #Max thrust is 1000, 750 default limiter put in place

		# Reverse Multiplier, either == 1 of -1
		self.q1_rm = 1
		self.q2_rm = 1
		self.q3_rm = 1
		self.q4_rm = 1

		# self.init_node()
		self.init_publishers()
		self.init_subscribers()
		self.init_services()

		roll = pitch = yaw = 0.0


	##################################################
	### Class Init Scripts
	##################################################

	def init_node(self):
		rospy.init_node(self.ros_node_name, anonymous=True)
		self.rate = rospy.Rate(10) # 10hz

	def init_subscribers(self):
		self.subscribers.append(self.create_subscriber_object("/wamv/sensors/gps/gps/fix", NavSatFix, self.distance_manager))
		self.subscribers.append(self.create_subscriber_object("/wamv/sensors/imu/imu/data", Imu, self.rotation_manager))
		self.subscribers.append(self.create_subscriber_object("/vrx/station_keeping/goal", GeoPoseStamped, self.way_point_response_func))
		self.subscribers.append(self.create_subscriber_object("/vrx/wayfinding/waypoints", GeoPath, self.way_point_response_func))

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

	def create_subscriber_object(self, sub_name, sub_type, callback):
		rospy_subscriber = rospy.Subscriber(sub_name, sub_type, callback)
		subscriber_object = {"topic": sub_name, "message": sub_type, "subscriber": rospy_subscriber, "node_type":"Subscriber"}
		return subscriber_object

	def get_publisher_topic(self, topic_name):
		return next(item for item in self.publishers if item["topic"] == topic_name)

	def get_subscriber_topic(self, topic_name):
		return next(item for item in self.subscribers if item["topic"] == topic_name)


	##################################################
	### Getters And Setters
	##################################################

	def add_way_point(self, coordinates, station_keep_time=0):
		self.queued_coordinates.append(coordinates)
		self.queued_station_keep_times.append(station_keep_time)

		if self.navigation_indicator == False:
			print("NAVIGATION INDICATOR FALSE")
			self.set_next_waypoint()


	##################################################
	### Navigation Controller
	##################################################

	def calculate_distance(self, current_gps_coords, desired_gps_coords):
		r = 6371 #radius of Earth, km

		# lat2_in, lon2_in = desired_gps_coords
		lat1_in, lon1_in = current_gps_coords
		lat2_in, lon2_in = desired_gps_coords

		#convert to coordinates to radians
		lat1,lon1,lat2,lon2 = map(radians, [lat1_in,lon1_in,lat2_in,lon2_in])

		# Calculate distance between GPS coordinates (Haversine Formula)
		deltalon = lon2 - lon1
		deltalat = lat2 - lat1
		alpha = 2*asin( sqrt( (sin(abs(deltalat)/2))**2 + cos(lat1)*cos(lat2)*((sin(abs(deltalon)/2))**2) ) )
		distance = alpha * r * 1000 # Distance in meters

		# print("DISTANCE")
		# print(distance)

		return distance

	def caclulate_rotation(self, current_gps_coords, desired_gps_coords, heading):
		lat1, lon1 = desired_gps_coords
		lat2, lon2 = current_gps_coords

		deltalon = lon2 - lon1
		deltalat = lat2 - lat1

		#OKAY NOW turn angle calc
		x = cos(lat2)*sin(deltalon)
		y = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(deltalon)
		bearing = degrees(atan2(y,x)) #Measured from East (-180,180) ccw+ cw-

		#bearing: angle cw between North and goal
		#heading: angle cw bt North and direction wamv is pointing
		theta = -1* heading - bearing #theta is going to be turn angle

		if -360 <= theta <= -180:
			theta += 360


		if 180 <= theta <= 360:
			theta -= 360

		# print("Heading")
		# print(heading)
		# print("Bearing")
		# print(bearing)

		# print("THETA")
		# print(theta)

		return theta


	##################################################
	### Subscriber Manager Functions
	##################################################

	def distance_manager(self, gps_data):

		max_thrust = self.max_thrust

		self.current_coordinates = [gps_data.latitude, gps_data.longitude]

		if len(self.desired_coordinates) > 0:

			self.distance = self.calculate_distance([gps_data.latitude, gps_data.longitude], self.desired_coordinates) #Distance in meters

		self.check_station_keep_timer()


		thrust_values = {}
		q1 = self.get_publisher_topic("/wamv/thrusters/right_front_thrust_cmd")
		q2 = self.get_publisher_topic("/wamv/thrusters/left_front_thrust_cmd")
		q3 = self.get_publisher_topic("/wamv/thrusters/left_rear_thrust_cmd")
		q4 = self.get_publisher_topic("/wamv/thrusters/right_rear_thrust_cmd")

		if self.navigation_indicator == True:
			# thrust_values["q1"] = 0
			# thrust_values["q2"] = 0
			# thrust_values["q3"] = 0
			# thrust_values["q4"] = 0


			if 180 > self.degree_offset > 30:

				thrust_values["q3"] = 0.5*max_thrust
				thrust_values["q4"] = -0.5*max_thrust
				thrust_values["q2"] = 0.5*max_thrust
				thrust_values["q1"] = -0.5*max_thrust


			elif -180 < self.degree_offset < -30:

				thrust_values["q3"] = -0.5*max_thrust
				thrust_values["q4"] = 0.5*max_thrust
				thrust_values["q2"] = -0.5*max_thrust
				thrust_values["q1"] = 0.5*max_thrust


			elif self.distance > 20:
				left_thrust = max_thrust + self.degree_offset * 4/1000
				right_thrust = max_thrust - self.degree_offset * 4/1000

				if left_thrust >= 1.0*max_thrust: left_thrust = 1.0*max_thrust
				if left_thrust <= -1.0*max_thrust: left_thrust = -1.0*max_thrust
				if right_thrust >= 1.0*max_thrust: right_thrust = 1.0*max_thrust
				if right_thrust <= -1.0*max_thrust: right_thrust = -1.0*max_thrust


				thrust_values["q3"] = left_thrust
				thrust_values["q4"] = right_thrust
				thrust_values["q2"] = left_thrust
				thrust_values["q1"] = right_thrust


				#if 90 < self.degree_offset < 180 or -90 < self.degree_offset < -180:
				#   thrust_values["q3"] = -1 * left_thrust
				#   thrust_values["q4"] = -1 * right_thrust
				#   thrust_values["q2"] = -1 * left_thrust
				#   thrust_values["q1"] = -1 * right_thrust

			elif self.distance > 3:

				left_thrust = 0.5*max_thrust + self.degree_offset * 4/1000
				right_thrust = 0.5*max_thrust - self.degree_offset * 4/1000

				if left_thrust >= 0.50*max_thrust: left_thrust = 0.50*max_thrust
				if left_thrust <= -0.50*max_thrust: left_thrust = -0.50*max_thrust
				if right_thrust >= 0.50*max_thrust: right_thrust = 0.50*max_thrust
				if right_thrust <= -0.50*max_thrust: right_thrust = -0.50*max_thrust

				if 90 < self.degree_offset < 180 or -90 < self.degree_offset < -180:

					thrust_values["q3"] = -1*left_thrust
					thrust_values["q4"] = -1*right_thrust
					thrust_values["q2"] = -1*left_thrust
					thrust_values["q1"] = -1*right_thrust
				else:
					thrust_values["q3"] = left_thrust
					thrust_values["q4"] = right_thrust
					thrust_values["q2"] = left_thrust
					thrust_values["q1"] = right_thrust


			elif self.distance <= 3:

				thrust_values["q3"] = 0
				thrust_values["q4"] = 0
				thrust_values["q2"] = 0
				thrust_values["q1"] = 0


			# self.thrust_values = thrust_values
			# print(thrust_values)
			# q3["publisher"].publish(thrust_values["q3"])
			# q4["publisher"].publish(thrust_values["q4"])
			# q2["publisher"].publish(thrust_values["q2"])
			# q1["publisher"].publish(thrust_values["q1"])


			# self.print_progress()

		else:
			thrust_values["q3"] = 0
			thrust_values["q4"] = 0
			thrust_values["q2"] = 0
			thrust_values["q1"] = 0

		self.thrust_values = thrust_values	
		q3["publisher"].publish(thrust_values["q3"])
		q4["publisher"].publish(thrust_values["q4"])
		q2["publisher"].publish(thrust_values["q2"])
		q1["publisher"].publish(thrust_values["q1"])




	def rotation_manager(self, imu_data):

		self.check_station_keep_timer()

		if self.navigation_indicator == True and len(self.current_coordinates)==2:

			global roll, pitch, yaw

			q = imu_data.orientation
			# print(q)

			q_list = [q.x, q.y, q.z, q.w]

			# To convert from quat to euler angles
			(roll, pitch, yaw) = euler_from_quaternion (q_list)
			# print("ROLL")
			# print(roll)

			# print("PITCH")
			# print(pitch)

			# print("YAW")
			# print(yaw)

			# To convert from euler to quat
			# quat = quaternion_from_euler (roll, pitch, yaw)
			# print quat
			

			# if self.imu_orientation == "NED":
			# 	yaw_rad = atan2(2.0 * (q.y*-q.x + q.w*q.z), q.w*q.w - q.z*q.z - q.y*q.y + q.x*q.x)
			# else:
			# 	yaw_rad = atan2(2.0 * (q.y*q.z + q.w*q.x), q.w*q.w - q.x*q.x - q.y*q.y + q.z*q.z)
			
			# yaw_rad = atan2(2.0 * (q.y*q.z + q.w*q.x), q.w*q.w - q.x*q.x - q.y*q.y + q.z*q.z)

			yaw_rad = atan2(2.0 * (q.y*-q.x + q.w*q.z), q.w*q.w - q.z*q.z - q.y*q.y + q.x*q.x)
			# print("yaw rad")
			# print(yaw_rad)

			# yaw_deg = (yaw_rad+3.14159/2)*-180/3.14159
			yaw_deg = yaw_rad*(180/3.14159)
			# yaw_deg -= imu_degree_offset_bias # YAW in terms of north, gets larger when going cw

			# print("yaw_deg: " + str(yaw_deg))

			
			# yaw_deg *= -1
			# yaw_deg += 180
			# print("yaw deg")
			# print(yaw_deg)
			# print("yaw_deg post_process")

			theta_offset = self.caclulate_rotation(self.current_coordinates, self.desired_coordinates, yaw_deg)
			theta_offset *= -1
			theta_offset += self.imu_degree_offset_bias

			# print("Theta Offset")
			# print(theta_offset)

			# theta_offset -= 180

			# if theta_offset > 180:
			# 	theta_offset -= 360
			# elif theta_offset < -180:
			# 	theta_offset += 360
			# print(theta_offset)

			if -5 < theta_offset < 5:
				self.degree_offset = 0
				# print("no degree offset")
			else:
				self.degree_offset = theta_offset
				# print(self.degree_offset)

			# print("Theta OFfset")
			# print(theta_offset)

			# print("Distance:")
			# print(self.distance)

		self.print_progress()
		


	##################################################
	### Handle Service Requests
	##################################################


	def start_navigation(self):
		self.navigation_indicator = True

		if len(self.desired_coordinates) == 0:
			self.set_next_waypoint()


	def stop_navigation(self):
		self.navigation_indicator = False
		self.desired_coordinates = []
		# print("Stopping Navigation")


	def set_station_keep_timer(self, station_keep_time): # Input time in minutes
		self.station_keep_end_time = time.time() + station_keep_time * 60 

	def check_station_keep_timer(self):
		
		if time.time() > self.station_keep_end_time:
			self.set_next_waypoint()

		#If WAMV within 10 meters of point for first time, and has desired coordinates, navigation indicator, start timer
		if self.distance <= 3 and self.station_keep_end_time_set == False and len(self.desired_coordinates) > 0 and self.navigation_indicator == True: 
			self.station_keep_end_time_set = True


		# self.print_progress()


	def set_next_waypoint(self):

		self.station_keep_end_time_set = False

		if len(self.queued_coordinates) > 0:
			self.desired_coordinates = self.queued_coordinates[0]
			self.set_station_keep_timer(self.queued_station_keep_times[0])
			print("SET STATION KEEP TIMER: ")
			print(self.queued_station_keep_times[0])
			print(time.time())
			print(time.time() + self.queued_station_keep_times[0]*60)
			print(self.queued_station_keep_times[0]*60+time.time() - time.time())
			# print(time.time() - self.queued_station_keep_times[0]*60)
			# print(type(time.time()))
			# print(time.time() < self.queued_station_keep_times[0]*60)

			self.queued_coordinates.pop(0)
			self.queued_station_keep_times.pop(0)

		else:
			self.stop_navigation()

	# def remove_current_coordinate(self):
	# 	"null"

	def remove_next_queued_coordinate(self):
		self.queued_coordinates.pop(0)
		self.queued_station_keep_times.pop(0)

	def remove_all_coordinates(self):
		self.queued_coordinates = []
		self.queued_station_keep_times = []
		self.desired_coordinates = []


	def print_progress(self):
		print(chr(27) + "[2J")
		print(" Navigation: " + str(self.navigation_indicator))
		print(" Thrust: " + str(self.thrust_values))


		print("\n Current Coordinates: " + str(self.current_coordinates))
		print(" Desired Coordinates: " + str(self.desired_coordinates))

		print("\n Station Keeping: " + str(self.station_keep_end_time_set))
		if self.station_keep_end_time_set == False: 
			timer = 0
		else:
			timer = round((self.station_keep_end_time - time.time()) / 60, 2)
		print(" Station Keep Timer: " + str(timer) + " minutes")
		# print(time.time())

		print("\n Distance: " + str(self.distance))
		print(" Angle Offset: " + str(self.degree_offset))

		print("\n Queued Coordinates: " + str(self.queued_coordinates))
		print(" Queued Minutes: " + str(self.queued_station_keep_times))
		print("\n --------------------------------------------------------- \n\n")


	#################################################
	## ROS Services
	#################################################

	def init_services(self):
		self.way_point_service = rospy.Service('way_point', add_way_point, self.way_point_response_func)
		self.way_point_command_service = rospy.Service('way_point_cmd', way_point_cmd, self.way_point_cmd_response_func)

	def way_point_response_func(self, data):
		try:
				# lat = req.latitude
				# lon = req.longitude
				# minutes = req.minutes

				lat = data.pose.position.latitude
				lon = data.pose.position.longitude
				minutes = 10

				self.add_way_point([lat, lon], minutes)
				print("Recieved Way Point")

				return add_way_pointResponse(recieved=True)



		except:
				return add_way_pointResponse(recieved=False)

	def way_point_cmd_response_func(self, req):
		try:
				
				# command = "Start Navigation"

				cmd = req.command

				if cmd == "Start Navigation":
					self.start_navigation()

				elif cmd == "Stop Navigation":
					self.stop_navigation()

				elif cmd == "Remove Next Coordinate":
					self.remove_next_queued_coordinate()

				elif cmd == "Remove All Coordinates":
					self.remove_all_coordinates()

				elif cmd == "Remove Current Coordinate":
					self.set_next_waypoint()

				elif "Max Speed " in cmd:
					self.max_thrust = int(cmd.split("Max Speed ")[1])

				elif cmd == "Kill":
					self.stop_navigation()

					for i in range(5):
						for publisher in self.publishers:
								publisher["publisher"].publish(0)

						for thruster in self.thrust_values:
							self.thrust_values[thruster] = 0
						# self.print_progress()
						print("KILLING")

				else:
					return way_point_cmdResponse(recieved=False)


				return way_point_cmdResponse(recieved=True)
			
		except:
				return way_point_cmdResponse(recieved=False)

# rospy.init_node("wamv_class")

#creating object wamv1
# wamv1 = WAMV_Way_Point()
#wamv1.main()
#wamv1.add_way_point([0,0], 5)
#wamv1.start_navigation()
# wamv1.print_progress()

# rospy.spin()
