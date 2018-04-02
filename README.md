# ros_aero_imu
ROS publisher for 9DOF IMU on Intel Aero board.

## ROS Topics
Publishes raw IMU data on topic 'imu/data_raw' (use package like [imu_filter_madgwick](http://wiki.ros.org/imu_filter_madgwick?distro=kinetic) to generate 'imu/data' with orientation.)

Publishes Magnetometer data on 'imu/mag'

## Requirements
Accessing the BMI160 (IMU) via SPI requires the user to have permission to access the SPI device. For example, add an spi group, and add the group to your user. 

```
sudo chgrp spi /dev/spidev*
sudo chmod g+rw /dev/spidev*
```

Accessing the BMM150 (Magnatometer) via I2C requires the user to have permission to access the I2C device. The device group should already be i2c. Make sure to add this group to your user.
