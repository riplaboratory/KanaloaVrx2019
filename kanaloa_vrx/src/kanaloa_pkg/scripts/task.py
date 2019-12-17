#!/usr/bin/env python
# license removed for brevity

import rospy
from vrx_gazebo.msg import Task
from nav_channel import nav_channel_main
from wayfinding import WAMV_Way_Point as wayfind
from station_keeping import WAMV_Way_Point as station_keep

current_task = None

def assign(data):
	global current_task

	task_name = data.name
	# print(task_name)
	

	if task_name == "navigation_course":
		if current_task != "navigation_course":
			nav_channel_main()
			current_task = "navigation_course"

	elif task_name == "wayfinding":
		if current_task != "wayfinding":
			wayfind()
			current_task = "wayfinding"
	
	elif task_name == "stationkeeping":
		if current_task != "stationkeeping":
			station_keep()
			current_task = "stationkeeping"

	elif task_name == "scan_dock":
		if current_task != "scan_dock":
			station_keep()
			current_task = "scan_dock"

def subscriber():
	# rospy.init_node("task_name")
	rospy.Subscriber("/vrx/task/info", Task, assign)
	# rospy.spin()


	
if __name__ == '__main__':
	rospy.init_node("Team_Kanaloloz_VRX")
	while not rospy.is_shutdown():
		subscriber()

		rospy.spin()