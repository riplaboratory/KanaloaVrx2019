#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from std_msgs.msg import Float32

from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import Imu

from math import radians
from math import degrees
from math import cos
from math import sin


import sys
import time

def drive(pub_names, pub_values):
    publishers = []
    for pub_name in pub_names:
        publishers.append(rospy.Publisher(pub_name, Float32, queue_size=10))

    rospy.init_node('wamv_thrust_publisher_node', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        # hello_str = "hello world %s" % rospy.get_time()
        # rospy.loginfo(hello_str)
        for i in range(len(pub_values)):
            publishers[i].publish(pub_values[i])
            # pub.publish(hello_str)
        rate.sleep()

if __name__ == '__main__':

	heading = float(raw_input("\n\t Heading (-180 to 180): \n\t"))

	if heading != "q":
		speed = float(raw_input("\n\t What speed do you want to go (0 to 1.0): \n\t"))
		# heading += radians(45)
		heading_rad = radians(heading)
		

	try:

		if 0 < heading < 90:
			q2_q4_thrust = sin(heading_rad)
			q1_q3_thrust = -cos(heading_rad)

			# print (q1_q3_thrust)

			drive(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
					"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [q1_q3_thrust*speed, q2_q4_thrust*speed, q2_q4_thrust*speed, q1_q3_thrust*speed])


		elif 90 < heading < 180:

			q2_q4_thrust = cos(heading_rad)
			q1_q3_thrust = sin(heading_rad)

			# print(q1_q3_thrust)
			# print(q2_q4_thrust)

			drive(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
					"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [q1_q3_thrust*-speed, q2_q4_thrust*speed, q2_q4_thrust*speed, q1_q3_thrust*-speed])

		elif -180 < heading < -90:
			q2_q4_thrust = sin(heading_rad)
			q1_q3_thrust = cos(heading_rad)

			# print(q1_q3_thrust)
			# print(q2_q4_thrust)

			drive(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
					"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [q1_q3_thrust*-speed, q2_q4_thrust*speed, q2_q4_thrust*speed, q1_q3_thrust*-speed])


		elif -90 < heading < 0:

			# if heading == -45:
			# 	# heading -= degrees(1.0)
			# 	q2_q4_thrust = cos(heading_rad)
			# 	q1_q3_thrust = sin(heading_rad)

			# 	talker(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
			# 		"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [q1_q3_thrust*speed, q2_q4_thrust*-0.5*speed, q2_q4_thrust*-0.5*speed, q1_q3_thrust*speed])

			# else:

			q2_q4_thrust = sin(heading_rad)
			q1_q3_thrust = cos(heading_rad)

			# print(q1_q3_thrust)
			# print(q2_q4_thrust)

			drive(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
					"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [q1_q3_thrust*speed, q2_q4_thrust*-speed, q2_q4_thrust*-speed, q1_q3_thrust*speed])


		elif heading == 0:
			drive(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
					"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [speed, speed, speed, speed])

		elif heading == 180 or heading == -180:
			drive(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
					"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [-speed, -speed, -speed, -speed])

		elif heading == 90:
			drive(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
					"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [-speed, speed, speed, -speed])

		elif heading == -90:
			drive(["/wamv/thrusters/left_front_thrust_cmd", "/wamv/thrusters/left_rear_thrust_cmd", 
					"/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [-speed, 0, 0, -speed])

		else:
			sys.exit("Bye")


	except rospy.ROSInterruptException:
		pass