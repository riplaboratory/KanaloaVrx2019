#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from std_msgs.msg import Float32

import sys


publishers = []

def wamv_create_pub(pub_names):
    # publishers = []
    global publishers

    for pub_name in pub_names:
        publishers.append(rospy.Publisher(pub_name, Float32, queue_size=10))

    # rospy.init_node('wamv_thrust_publisher_node', anonymous=True)
    # rate = rospy.Rate(10) # 10hz

    # rospy.init_node('wamv_thrust_publisher_node', anonymous=True)
    
    # while not rospy.is_shutdown():
    #     # hello_str = "hello world %s" % rospy.get_time()
    #     # rospy.loginfo(hello_str)
    #     for i in range(len(pub_values)):
    #         publishers[i].publish(pub_values[i])
    #         # pub.publish(hello_str)
    #     rate.sleep()

def wamv_pub(pub_name, pub_values):
	for i in range(len(pub_values)):
		publishers[i].publish(pub_values[i])

	# rate.sleep()

# if __name__ == '__main__':

# 	heading = float(raw_input("\n\t Heading (-90 to 90): \n\t"))

# 	if heading != "q":
# 		speed = float(raw_input("\n\t What speed do you want to go (-1.0 to 1.0): \n\t"))
# 		# heading *= -1

# 	try:

def rotate_WAMV(speed):
	wamv_create_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"])

	wamv_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [-speed, speed, speed, -speed])


def drive_WAMV(speed, heading):

	wamv_create_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"])

	if 0 < heading < 90:
		q_left = speed + heading/1000
		q_right = speed - heading/1000

		# print(q_left)
		# print(q_right)

		wamv_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [q_right, q_left, q_left, q_right])


	elif -90 < heading < 0:
		q_left = speed + heading/1000
		q_right = speed - heading/1000

		wamv_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [q_right, q_left, q_left, q_right])


	elif heading == 0:
		wamv_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [speed, speed, speed, speed])


	elif heading == 180 or heading == -180:
		wamv_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [-speed, -speed, -speed, -speed])


	elif heading == -90:
		wamv_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [0.7*speed, -speed, 0.7*speed, -speed])


	elif heading == 90:
		wamv_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"], [-speed, 0.7*speed, -speed, -0.7*speed])

	else:
		sys.exit("Bye")


# except rospy.ROSInterruptException:
# 	pass

# wamv_create_pub(["/wamv/thrusters/right_front_thrust_cmd", "/wamv/thrusters/left_front_thrust_cmd",
# 				"/wamv/thrusters/left_rear_thrust_cmd", "/wamv/thrusters/right_rear_thrust_cmd"])