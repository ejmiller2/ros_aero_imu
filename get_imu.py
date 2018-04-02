import spidev
import time
import smbus
from bmi150_regmap import *
from bmi160_regmap import *
from math import cos, sin, radians


def open_imu():
	'''
	Opens BMI_160 imu on bus 3, cs 0 associated with the Intel-Aero RTF platform
	'''
	imu = spidev.SpiDev()
	opened = imu.open(3,0)		# SPI bus 3, CS 0

	if(opened == 0):
		print 'failed to open'
		return -1

	return imu

def hardware_init(imu):
	'''
	###############################################################################
	Need to write a while catch to ensure registers are writen to before moving on.
	###############################################################################
	'''
	print 'Reset BMI160'
	imu.xfer2([CMD + write, SOFTRESET])
	time.sleep(0.2)

	# After reset, read from register 0x7f as per datasheet recommendation
	print 'Read 0x7F: ', imu.xfer2([0x7F + read, 0x00])[1]
	# Check chip ID
	print 'Chip ID (should be 0xD1): ', format(imu.xfer2([CHIP_ID + read, 0x00])[1], '#04X')
	# Reset the FIFO
	#imu.xfer2([CMD + write, FIFO_FLUSH])
	#time.sleep(0.05)
	#print 'FIFO Length: ', imu.xfer2([FIFO_LENGTH + read, 0,0])[1:]


def fifo_flush(imu):
	'''
	###############################################################################
	Need to write a while catch to ensure registers are writen to before moving on.
	###############################################################################
	'''
	# Reset the FIFO
	print 'Reset FIFO'
	imu.xfer2([CMD + write, FIFO_FLUSH])
	time.sleep(0.05)
	print 'FIFO Length: ', imu.xfer2([FIFO_LENGTH + read, 0,0])[1:]


def configure_pmu(imu):
	'''
	###############################################################################
	Need to write a while catch to ensure registers are writen to before moving on.
	###############################################################################
	'''
	imu.xfer2([CMD + write, ACC_NORMAL])
	time.sleep(0.05)
	imu.xfer2([CMD + write, GYR_NORMAL])
	time.sleep(0.05)
	#imu.xfer2([CMD + write, MAG_NORMAL])
	print 'pmu status: ', format(imu.xfer2([PMU_STATUS + read, 0x00])[1], '#04X')


def calibrate(imu):
	'''
	###############################################################################
	Need to write a while catch to ensure registers are writen to before moving on.
	###############################################################################
	'''
	# Check offset before
	print 'Offset AX (before): ', format(imu.xfer2([OFFSET + read, 0x00])[1], '#04X')
	print 'Offset GX (before): ', format(imu.xfer2([OFFSET + 3 + read, 0x00])[1], '#04X')
	print 'Offset 6 (before): ', format(imu.xfer2([OFFSET + 6 + read, 0x00])[1], '#04X')
	# Enable offset for GYR and ACC
	#imu.xfer2([OFFSET + 6 + write, 0xc0])
	imu.xfer2([OFFSET + 6 + write, 0x40])
	# Calibrate
	imu.xfer2([FOC_CONF + write, 0x7d]) #all
	#imu.xfer2([FOC_CONF + write, 0x40]) #gyro
	#imu.xfer2([FOC_CONF + write, 0x3d]) #acc
	imu.xfer2([CMD + write, START_FOC])
	time.sleep(1)
	# check offset after
	print 'Offset AX (after): ', format(imu.xfer2([OFFSET + read, 0x00])[1], '#04X')
	print 'Offset GX (after): ', format(imu.xfer2([OFFSET + 3 + read, 0x00])[1], '#04X')
	print 'Offset 6 (after): ', format(imu.xfer2([OFFSET + 6 + read, 0x00])[1], '#04X')
	# Reset the FIFO
	imu.xfer2([CMD + write, FIFO_FLUSH])
	time.sleep(0.05)


def configure_acc(imu):
	'''
	Set Acc Data Rate @ 100Hz, see page 56
	'''
	imu.xfer2([ACC_CONF + write, 0x28])
	time.sleep(0.05)
	print 'ACC Range: ', format(imu.xfer2([ACC_RANGE + read, 0x00])[1], '#04X')


def configure_gyr(imu):
	'''
	Set Gyro Data Rate @ 100Hz, see page 57
	'''
	imu.xfer2([GYR_CONF + write, 0x28])
	time.sleep(0.05)
	imu.xfer2([GYR_RANGE + write, 0x00]) # 0=>2000 deg/s
	#imu.xfer2([GYR_RANGE + write, 0x03]) # 3=>250 deg/s
	time.sleep(0.05)
	print 'GYR Range: ', format(imu.xfer2([GYR_RANGE + read, 0x00])[1], '#04X')

def enable_mag(imu):
	imu.xfer2([MAG_IF_1 + write, 0x03])
	time.sleep(0.05)
	imu.xfer2([Aux_Data2write + write, 0x00])
	time.sleep(0.05)
	imu.xfer2([Aux_Reg2write + write, 0x03])
	time.sleep(0.05)
	print 'STATUS: ', imu.xfer2([STATUS + read, 0x00])[1]

def configure_FIFO(imu):
	'''
	Set Acc & Gyro Feeds to FIFO
	'''
	imu.xfer2([FIFO_CONFIG2 + write, 0xC0])
	time.sleep(0.05)


def read_FIFO_frame(imu):
	FIFO_Length = imu.xfer2([FIFO_LENGTH + read, 0,0])[1:]	#Check if the FIFO is empty
	if((FIFO_Length[0] + FIFO_Length[1]*256) > 12):		#If not, read frame
		data =  imu.xfer2([FIFO_DATA + read, 0,0,0,0,0,0,0,0,0,0,0,0])[1:]
		gx = fuse_bits(data[0], data[1])
		gy = fuse_bits(data[2], data[3])
		gz = fuse_bits(data[4], data[5])
		ax = fuse_bits(data[6], data[7])
		ay = fuse_bits(data[8], data[9])
		az = fuse_bits(data[10], data[11])
		return [gx, gy, gz, ax, ay, az]
	return -1


def fuse_bits(lsb, msb):
	val = lsb + 256*msb
	if val >= 2**15:
		val -= 2**16
	return val


def read_raw_sensors(imu):
	ACC = imu.xfer2([ACC_ALL + read, 0,0,0,0,0,0])[1:]
	GYR = imu.xfer2([GYR_ALL + read, 0,0,0,0,0,0])[1:]

	gx = fuse_bits(GYR[0], GYR[1])
	gy = fuse_bits(GYR[2], GYR[3])
	gz = fuse_bits(GYR[4], GYR[5])
	ax = fuse_bits(ACC[0], ACC[1])
	ay = fuse_bits(ACC[2], ACC[3])
	az = fuse_bits(ACC[4], ACC[5])
	return [gx, gy, gz, ax, ay, az]



def configure_bmi160():
	imu = open_imu()
	if(imu == -1):
		exit()
	hardware_init(imu)
	configure_pmu(imu)
	#calibrate(imu)
	configure_acc(imu)
	configure_gyr(imu)
	#fifo_flush(imu)

	#imu.xfer2([FIFO_CONFIG2 + write, 0xD0])
	#imu.xfer2([FIFO_CONFIG2 + write, 0xC0])
	#fifo_flush(imu)

	return imu

if __name__=="__main__":
	imu = configure_bmi160()
	gyr_fact = 32768.0 / 2000.0 #range 2000
	#gyr_fact = 32768.0 / 250 #range 250
	#gyr_fact = 32768.0 / 125 #range 125
	acc_fact = 32768.0 / 2.0 #range 2G
	#fifo_flush(imu)
	seq = 0

	while True:
		time.sleep(0.01)
		check = read_raw_sensors(imu)
		#check = read_FIFO_frame(imu)
		if((check != -1) and ((seq % 100)==0)):
			print 'IMU: ', check
			[gx, gy, gz, ax, ay, az] = check
			#print 'gx deg: ', (gx / gyr_fact)
			#print 'gx rad: ', radians(gx / gyr_fact)
			print 'acc (g): ', (ax / acc_fact), (ay / acc_fact), (az / acc_fact)
			print 'gyr (d): ', (gx / gyr_fact), (gy / gyr_fact), (gz / gyr_fact)
		seq += 1
	imu.close()
