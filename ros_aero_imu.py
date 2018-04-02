#!/usr/bin/env python

import roslib; roslib.load_manifest( 'rviz_plugin_tutorials' )
from sensor_msgs.msg import Imu, MagneticField
import rospy
from math import cos, sin, radians
import tf
from get_imu import *
from get_mag import *

rospy.init_node( 'aero_imu' )

topic = 'imu/data_raw'
mag_topic = 'imu/mag'
publisher = rospy.Publisher( topic, Imu )
mag_publisher = rospy.Publisher( mag_topic, MagneticField )

frame_id = rospy.get_param('~frame_id', '/base_imu_link')
print 'Frame ID: ', frame_id
br = tf.TransformBroadcaster()
rate = rospy.Rate(100)
radius = 5
angle = 0

dist = 3
# factors for conversion
#acc_fact = 1000.0
acc_fact = 32768.0 / 2.0 #range 2G
#gyr_fact = 900.0
gyr_fact = 32768.0 / 2000.0 #range 2000 deg/s
gravity = 9.806
mag_fact = 10**6 # micro Tesla to Tesla
seq = 0

# configure BMI160
bmi160 = configure_bmi160()
bmi150 = configure_bmi150()
trim = read_trim_registers(bmi150)

print 'Publishing IMU and Mag data (ctl-c to quit)'

mag_data = [0,0,0]
while not rospy.is_shutdown():
    # read IMU data
    #check = read_FIFO_frame(bmi160)
    check = read_raw_sensors(bmi160)

    if(check != -1):
        #print 'IMU: ', check
        [gx, gy, gz, ax, ay, az] = check
        imu = Imu()
        #header
        imu.header.seq = seq
        imu.header.stamp = rospy.Time.now()
        imu.header.frame_id = frame_id
        #quanterion orientation
        imu.orientation_covariance[0] = 0
        #angular velocity
        imu.angular_velocity.x = radians(gx / gyr_fact)
        imu.angular_velocity.y = radians(gy / gyr_fact)
        imu.angular_velocity.z = radians(gz / gyr_fact)
        imu.angular_velocity_covariance[0] = 0
        #linear acceleration
        imu.linear_acceleration.x = (ax / acc_fact) * gravity
        imu.linear_acceleration.y = (ay / acc_fact) * gravity
        imu.linear_acceleration.z = (az / acc_fact) * gravity
        imu.linear_acceleration_covariance[0] = 0

        publisher.publish( imu )
    else:
        print 'ERROR: Read IMU'

    # read Magnetometer data
    if ((seq % 10) == 0):
        mag_data = read_mag_frame(bmi150, trim)
        if(mag_data != -1):
            #print 'Mag: ', mag_data
            [mx, my, mz] = mag_data
            mag = MagneticField()
            #header
            mag.header.seq = seq % 10
            mag.header.stamp = rospy.Time.now()
            mag.header.frame_id = frame_id
            #magnetic field
            mag.magnetic_field.x = mx / mag_fact
            mag.magnetic_field.y = my / mag_fact
            mag.magnetic_field.z = mz / mag_fact
            mag.magnetic_field_covariance[0] = 0

            mag_publisher.publish( mag )
        else:
            print 'ERROR: Read Mag'

    seq = seq + 1
    rate.sleep()
