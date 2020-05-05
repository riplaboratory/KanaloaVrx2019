# Setting up VRX Gazebo environment  
Option 2: Build VRX from source  
If you havn't Build from source yet, Good News! We have documentation for that as well! [Build From Source](https://github.com/riplaboratory/Kanaloa/blob/master/Documentation/Software/RobotX-Simulation/readme.md)


#### Source the VRX environment

``` source ~/vrx_ws/devel/setup.bash ```  
You will need to do this step evertime you start your computer

Launch a project (choose one)

```
roslaunch vrx_gazebo station_keeping.launch
roslaunch vrx_gazebo wayfinding.launch
roslaunch vrx_gazebo perception_task.launch
roslaunch vrx_gazebo navigation_task.launch verbose:=true
roslaunch vrx_gazebo dock.launch verbose:=true
roslaunch vrx_gazebo scan_and_dock.launch verbose:=true
```

#### Launch control scheme (choose one)
In new terminal tab CTRL+SHIFT+T  
We must switch to a new terminal window because the current one we are in is occupied with the simulation.

Gamepad: ```roslaunch vrx_gazebo usv_joydrive.launch```  
Keyboard: ```roslaunch vrx_gazebo usv_keydrive.launch```

#### To get a camera setup
In new terminal tab  
In terminal:
```roslaunch wamv_gazebo rviz_vrx.launch```

You'll enter the Robotic visualization app "Rviz" which will give you views of all the cameras on the WAMV as well as a model of the WAMV.

TIP: If you’re computer is running slow, you can close the Gazebo app and observe your WAMV through the camera provided. The simulation will continue to run but it will not have to visualize all the calculations needed.
