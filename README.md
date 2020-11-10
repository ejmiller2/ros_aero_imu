# ros_aero_imu
ROS publisher for 9DOF IMU on Intel Aero board. Tested with ROS Kinetic. The axes and orientation may not conform with ROS specifications. Based on work from https://github.com/wnukmat/Intel-Aero/tree/master/sensors.

## ROS Topics
Publishes raw IMU data on topic 'imu/data_raw' (use package like [imu_filter_madgwick](http://wiki.ros.org/imu_filter_madgwick) to generate 'imu/data' with orientation.) Publishes at 100Hz (currently hard coded).

Publishes Magnetometer data on 'imu/mag'. Publishes at 10Hz (currently hard coded).

## Requirements
Accessing the BMI160 (IMU) via SPI requires the user to have permission to access the SPI device. For example, add an spi group, and add the group to your user.

```
sudo chgrp spi /dev/spidev*
sudo chmod g+rw /dev/spidev*
```

Accessing the BMM150 (Magnatometer) via I2C requires the user to have permission to access the I2C device. The device group should already be i2c. Make sure to add this group to your user.

## Running

To demonstrate the usage, you can view the orientation using rviz with the [rviz_imu_plugin](http://wiki.ros.org/rviz_imu_plugin).

Run `roscore` and start a base transform:
```
rosrun tf static_transform_publisher 0 0 0 0 0 0 1 map base_imu_link 10
```

Start ros_aero_imu to begin publishing the raw IMU and Magnetometer data from the Aero board: `./ros_aero_imu.py`

State the imu_filter_madgwick to read `imu/data_raw` and `imu/mag` and generate `imu/data` with orientation:
```
rosrun imu_filter_madgwick imu_filter_node
```

Start rviz (with rviz_imu_plugin enabled): `rosrun rviz rviz`

In rviz, set Fixed Frame to `base_imu_link`. Add rviz_imu_plugin to the view. Set the IMU view Topic to `/imu/data`. You should see the coordinate axes in the view, which should move according to the orientation of the Aero board.
