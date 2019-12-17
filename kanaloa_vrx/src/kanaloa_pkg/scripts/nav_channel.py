from __future__ import division

import cv2 # OpenCV for perspective transform
import math
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import sys
import time


import rospy
from sensor_msgs.msg import Image, CompressedImage

from cv_bridge import CvBridge, CvBridgeError

from drive_WAMV import drive_WAMV as drive_wamv
from drive_WAMV import rotate_WAMV as rotate_wamv

# Color Thresholds
lower_water = np.array([100,10,100])
upper_water = np.array([120,255,225])

lower_red = np.array([0,75,50])
upper_red = np.array([18,200,255])   

lower_green = np.array([75,100,50])
upper_green = np.array([80,240,240])

lower_blue = np.array([115,83,30])
upper_blue = np.array([122,255,255])

lower_white = np.array([0,0,220])
upper_white = np.array([180,20,255])

# Min Contour Size To Consider Object
min_radius = 10

# Persepctive Transofr Parameters
source = np.float32([[246.18,547.94], [1109.12,547.94],[1278.53,717.35], [105.88,720]])
destination = np.float32([[550,600],[750,600],[750,700],[550,700]])


# Gate Tracking Variables
entrance_gate_passed = False
exit_gate_passed = False
mid_gate_couter = 0

ros_img_converter = CvBridge()


# -------------------- Obstacle Avoidance --------------------

def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))
    
    return warped, mask

def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel

def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Plot
def plot_dir(grayscale_img, mean_dir, xpix, ypix):
    fig = plt.figure(figsize=(12,9))
    plt.subplot(221)
    plt.title('Data after Threshold')
    plt.imshow(grayscale_img, cmap='gray')
    plt.subplot(222)
    plt.title('Direction Estimate based on Threshold')
    plt.plot(xpix, ypix, '.')

    arrow_length = grayscale_img.shape[0]/3
    x_arrow = arrow_length * np.cos(mean_dir)
    y_arrow = arrow_length * np.sin(mean_dir)
    plt.arrow(0, 0, x_arrow, y_arrow, color='red', zorder=2, head_width=30, width=2)

def plot_mask(mask, color, position):
    mask_name = str(color)+' Mask'
    cv2.namedWindow(mask_name,cv2.WINDOW_NORMAL)
    if position == 0:
        cv2.moveWindow(mask_name, 830,30)
    elif position == 1:
        cv2.moveWindow(mask_name, 830,270)
    elif position == 2:
        cv2.moveWindow(mask_name, 830,500)
    elif position == 3:
        cv2.moveWindow(mask_name, 830,740)
    else:
        cv2.moveWindow(mask_name, 230,740)
    
    cv2.resizeWindow(mask_name, 550,250)
    cv2.imshow(mask_name, mask)
    cv2.waitKey(1)


def obstacle_avoidance(image, plot_debug=False):
    
    #set transform range
    source = np.float32([[246.18,547.94], [1109.12,547.94],[1278.53,717.35], [105.88,720]])
    destination = np.float32([[550,600],[750,600],[750,700],[550,700]])
    
    #Transorm
    warped, mask = perspect_transform(image, source, destination)
    
    hsv_img = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, lower_water, upper_water)
#     cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
#         cv2.CHAIN_APPROX_SIMPLE)[-2]
    res = cv2.bitwise_and(hsv_img, hsv_img, mask = mask)
    res_plot = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)

    plot_mask(res_plot, "Water", 4)
    
#     h, s, grayscale_img = cv2.split(mask)

    # plt.imshow(mask)
    # plt.show()
    
    x_min = 30
    x_max = 70
    y_min = 0
    y_max = 80

    x = mask.shape[1]
    y = mask.shape[0]


    x_min_crop = int(x * x_min/100)
    x_max_crop = int(x * x_max/100)
    y_min_crop = int(y * y_min/100)
    y_max_crop = int(y * y_max/100)  

    cropped_img = mask[y_min_crop:y_max_crop, x_min_crop:x_max_crop]

    xpix, ypix = rover_coords(cropped_img)
    dist, angles = to_polar_coords(xpix, ypix)
    mean_dir = np.mean(angles)

    if plot_debug:
        plot_dir(cropped_img, mean_dir*10, xpix, ypix)
    
    x_min = 15
    x_max = 85
    y_min = 15
    y_max = 85

    x = cropped_img.shape[1]
    y = cropped_img.shape[0]


    x_min_crop = int(x * x_min/100)
    x_max_crop = int(x * x_max/100)
    y_min_crop = int(y * y_min/100)
    y_max_crop = int(y * y_max/100)  

    cropped_img = cropped_img[y_min_crop:y_max_crop, x_min_crop:x_max_crop]

    xpix, ypix = rover_coords(cropped_img)
    dist, angles = to_polar_coords(xpix, ypix)
    mean_dir2 = np.mean(angles)

    # plt.imshow(cropped_img)
    # plt.show()

    # print("XPIX")
    # print(len(xpix))

    # print(cropped_img.shape)
    # print(cropped_img.shape[0])
    # print(cropped_img.shape[1])
    # print(len(xpix) / (cropped_img.shape[0] * cropped_img.shape[1]) * 100)
    # # print(len(xpix)/(cropped_img.shape[0] * cropped_img.shape[1]) * 100)
    
    trav = len(xpix) / (cropped_img.shape[0] * cropped_img.shape[1]) * 100

    # print("Trav OG")
    # print(trav)
#     print("Percentage Traversible: " + str(trav))
    
#     print(mean_dir2*100)
#     plot_dir(cropped_img, mean_dir*100, xpix, ypix)

    return {"mean_dir": mean_dir, "traversible": trav, "mean_dir2": mean_dir2}



# To be updated ....
def wamv_right_side_clear():
    return True

def wamv_left_side_clear():
    return True


# -------------------- Get Buoy Info --------------------

def find_buoy_locations(image):
    # min_radius = 10
    
    lower_threshold = {"red": lower_red,"blue": lower_blue, "green": lower_green, "white": lower_white}
    upper_threshold = {"red": upper_red,"blue": upper_blue, "green": upper_green, "white": upper_white}
    
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    buoys_object = {}



    
    
    for color in lower_threshold.keys():
        radius = 0
        mask = cv2.inRange(hsv_img, lower_threshold[color], upper_threshold[color])
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        res = cv2.bitwise_and(hsv_img, hsv_img, mask = mask)
        res_plot = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)

        plot_number = {"red": 0, "white": 1, "green":2, "blue":3}
        plot_mask(res_plot, color, plot_number[color])

        # print(color)
        # plt.imshow(mask)
        # plt.show()
        
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            # print("Radius " + color)
            # print(radius)

            if radius > min_radius:
                buoys_object[color] = {"location": [x,y], "radius": radius}
            else:
                buoys_object[color] = None
        else:
            buoys_object[color] = None

    return buoys_object


def get_gate_location(buoy_object, image_shape, colors):
    
    color_1, color_2 = colors
    
    if buoy_object[color_2] != None and buoy_object[color_1] != None:
        if buoy_object[color_1]["location"][0] < buoy_object[color_2]["location"][0]:
            
            x1, y1 = buoy_object[color_1]["location"]
            x2, y2 = buoy_object[color_2]["location"]
            
            angle = np.arctan((y2-y1)/(x2-x1)) ## May implement radius instead
            midpoint = [x1 + (x2 - x1)/2, y1 + (y2 - y1)/2]
            center_offset = [midpoint[0] - image_shape[1]/2,  midpoint[1] - image_shape[0]/2]
            distance = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            
            return {"center offset": center_offset, "angle offset": angle, "distance apart": distance, \
                   "midpoint": midpoint, "image shape": image_shape}
        
    return False

# -------------------- Drive Parameter Based On Buoy Info --------------------

def gate_drive_weights(gate_info):
    
    center_offset = gate_info["center offset"]
    # print("Center Offset")
    # print(center_offset)

    offset_thresh = 150
    
    # if center_offset[0] > offset_thresh and wamv_right_side_clear():
    #     return {"speed": 75, "heading": 0, "strafe": 90}
    
    # elif center_offset[0] < -1 * offset_thresh and wamv_left_side_clear():
    #     return {"speed": 75, "heading": 0, "strafe": -90}
    
    # if abs(center_offset[0]) < offset_thresh:
    return {"speed": 75, "heading": center_offset[0]/8, "strafe": 0}
    
    # else:
    #     return {"speed": 0, "heading": 0, "strafe": 0}


def obstacle_avoidance_weights(image):
    oa_info = obstacle_avoidance(image)
    
    traversible = oa_info["traversible"] 
    heading = math.degrees(-10 * oa_info["mean_dir"] )

    # print("Traversible:")
    # print(traversible)
    
    if traversible >= 95:
        return {"speed": traversible*0.8, "heading": heading, "strafe": 0}
    
    else:
        print("NOT TRAVERSIBLE!")
        return {"speed": -75, "heading": 0, "strafe": 0}
        

def random_drive_weights():
    "null"
    rand_heading = np.random.randint(30)
    return {"speed": 0, "heading": rand_heading, "strafe": 0}



# -------------------- ROS --------------------

def ros_main(topic_name, msg_type, callback):

    # rospy.init_node('nav_channel_driver', anonymous=True)

    rospy.Subscriber(topic_name, Image, callback)

    # rospy.spin()


# def nav_channel_drive(image_data):
#     print("Nav Channel")
#     image = ros_img_converter.imgmsg_to_cv2(image_data, "rgb8")
#     plt.imshow(image)
#     plt.show()


def nav_channel_drive(image_data):
    global entrance_gate_passed
    global mid_gate_couter
    global exit_gate_passed
    # print(chr(27)+'[2j')
    # print('\033c')
    # print('\x1bc')
    image = ros_img_converter.imgmsg_to_cv2(image_data, "bgr8")

    x_min = 0
    x_max = 100
    y_min = 20
    y_max = 80

    x = image.shape[1]
    y = image.shape[0]


    x_min_crop = int(x * x_min/100)
    x_max_crop = int(x * x_max/100)
    y_min_crop = int(y * y_min/100)
    y_max_crop = int(y * y_max/100)  

    image = image[y_min_crop:y_max_crop, x_min_crop:x_max_crop]



    # print("IMAGE")
    # print(type(image))
    # print(image.size)

    # plt.imshow(image)
    # plt.show()

    buoy_object = find_buoy_locations(image)

    general_gate_info = False

    # if entrance_gate_passed == False or entrance_gate_passed == "pending":
    if entrance_gate_passed == False:
        entrance_gate_info = get_gate_location(buoy_object, image.shape, ["white", "red"])
        general_gate_info = entrance_gate_info

        if buoy_object["white"] != None:
            # if buoy_object["white"]["radius"] > 60:
            if entrance_gate_info:
                # print(entrance_gate_info["distance apart"])
                if entrance_gate_info["distance apart"] > 900:
                    entrance_gate_passed= True

        # print("Entrance Gate")

        # if entrance_gate_info != False:
        #     entrance_gate_passed = "pending" 

        # if entrance_gate_passed == "pending" and entrance_gate_info == False:
        #     entrance_gate_passed= True
    
    elif mid_gate_couter < 10 and exit_gate_passed == False:
        middle_gate_info = get_gate_location(buoy_object, image.shape, ["green", "red"])
        exit_gate_info = get_gate_location(buoy_object, image.shape, ["blue", "red"])

        if middle_gate_info:
            general_gate_info = middle_gate_info
            # print("Middle Gate")
            # if buoy_object["green"] != None:
            #     if buoy_object["green"]["radius"] > 60:
            #         entrance_gate_passed= True
        else:
            general_gate_info = exit_gate_info
            # print("Exit Gate")
            # if buoy_object["blue"] != None:
            #     if buoy_object["blue"]["radius"] > 60:
            #         exit_gate_passed= True
            if exit_gate_info:
                # print(exit_gate_info["distance apart"])
                if exit_gate_info["distance apart"] > 900:
                    drive_wamv(1,0)
                    time.sleep(6)
                    exit_gate_passed= True

    # general_gate_info = False


    # general_gate_info = False

    # print(general_gate_info)
        
    # if entrance_gate_info:
        
    # #         get_gate_location(entrance_gate_info, image.shape, )
    #     # general_gate_info = entrance_gate_info
    # elif middle_gate_info:
        
    #     # general_gate_info = middle_gate_info
    # elif exit_gate_info:
        
        # general_gate_info = exit_gate_info

    # print("------")
        
    #     print(general_gate_info)
    if general_gate_info:
        # print("General Gate Info")

        # Navigate toward gate
        gd_weights = gate_drive_weights(general_gate_info)
        oa_weights = obstacle_avoidance_weights(image)

        # print("oa_weights")
        # print(oa_weights)

        drive_speed = (oa_weights["speed"] * 0.6 + gd_weights["speed"] * 0.4) /100
        drive_heading = (oa_weights["heading"] * 0.6 + gd_weights["heading"] * 0.4) *6 
        drive_strafe = gd_weights["strafe"] # To be used in the future
        #     drive_wamv(drive_speed, drive_heading)

        # return {"speed": drive_speed, "heading": drive_heading, "strafe": drive_strafe}
        # print("OA:")
        # print(oa_weights)
        # print("GD:")
        # print(gd_weights)
        # print({"speed": drive_speed/100, "heading": drive_heading, "strafe": drive_strafe})
        # drive_wamv(drive_speed, -1 * drive_heading)

    else:
        # print("No General Gate Info detected")
        # print("No Gates Found")
        rd_weights = random_drive_weights()
        oa_weights = obstacle_avoidance_weights(image)

        drive_speed = (oa_weights["speed"] * 0.6 + rd_weights["speed"] * 0.0) /100
        drive_heading = (oa_weights["heading"] * 0.3 + rd_weights["heading"] * 0.7) *2
        drive_strafe = rd_weights["strafe"] # To be used in the future
        #     drive_wamv(drive_speed, drive_heading)

        if drive_speed > 0:
            drive_speed = 0

        # return {"speed": drive_speed, "heading": drive_heading, "strafe": drive_strafe}
        # drive_wamv(drive_speed/100, -1* drive_heading)

    if drive_speed > 1:
        drive_speed = 1
    if drive_speed < -1:
        drive_speed = -1


    # print({"speed": drive_speed, "heading": drive_heading, "strafe": drive_strafe})

    if exit_gate_passed == True:
        print("Task Complete!")
        rospy.signal_shutdown("Task Complete!")
        sys.exit()
    # elif drive_strafe != 0 and drive_speed > 1:
    #     drive_wamv(drive_speed/3,  drive_strafe)
    elif drive_speed == 0:
        rotate_wamv(0.30)
    else:
        drive_wamv(drive_speed/1.25, drive_heading)



    if buoy_object["red"] != None:
        x,y = buoy_object["red"]["location"]
        x,y = (int(x), int(y))
        r = int(buoy_object["red"]["radius"])
        cv2.circle(image, (x, y), r, (0,0,255))
    if buoy_object["blue"] != None:
        x,y = buoy_object["blue"]["location"]
        x,y = (int(x), int(y))
        r = int(buoy_object["blue"]["radius"])
        cv2.circle(image, (x, y), r, (255,0,0))
    if buoy_object["green"] != None:
        x,y = buoy_object["green"]["location"]
        x,y = (int(x), int(y))
        r = int(buoy_object["green"]["radius"])
        cv2.circle(image, (x, y), r, (0,255,0))
    if buoy_object["white"] != None:
        x,y = buoy_object["white"]["location"]
        x,y = (int(x), int(y))
        r = int(buoy_object["white"]["radius"])
        cv2.circle(image, (x, y), r, (95,95,95))

    if general_gate_info:
        x,y = general_gate_info["midpoint"]
        x,y = (int(x), int(y))
        r = 10
        cv2.circle(image, (x, y), r, (0,165,255), thickness=-1)


    cv2.namedWindow('Image window',cv2.WINDOW_NORMAL)
    cv2.moveWindow('Image window', 40,30)
    cv2.resizeWindow('Image window', 800,480)
    cv2.imshow("Image window", image)
    cv2.waitKey(1)


def nav_channel_main():
    ros_main("/wamv/sensors/cameras/front_middle_camera/image_raw", Image, nav_channel_drive)
# ros_main("wamv/sensors/cameras/front_left_camera/image_raw/", Image, nav_channel_drive)