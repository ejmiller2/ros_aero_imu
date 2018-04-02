import time
import smbus
from bmi150_regmap import *


def twos_complement(data, bits):
	val = data
	if data >= 2**(bits-1):
		val = data - 2**bits
	return val

def fuse_bits(lsb, msb):
	val = lsb + 256*msb
	return val


def read_trim_registers(bus):
	trim = {}
	print('Reading BMM150 trim registers')
	trim_x1y1 = bus.read_i2c_block_data(address, BMM150_DIG_X1, 2)
	#print trim_x1y1

	trim_xyz = bus.read_i2c_block_data(address, BMM150_DIG_Z4_LSB, 4)
	#print trim_xyz

	trim_xy1xy2 = bus.read_i2c_block_data(address, BMM150_DIG_Z2_LSB, 10)
	#print trim_xy1xy2

	# 8-bit signed values
	trim['x1'] = twos_complement(trim_x1y1[0],8)
	trim['y1'] = twos_complement(trim_x1y1[1],8)
	trim['x2'] = twos_complement(trim_xyz[2],8)
	trim['y2'] = twos_complement(trim_xyz[3],8)
	trim['xy2'] = twos_complement(trim_xy1xy2[8],8)
	# 8-bit unsigned values
	trim['xy1'] = trim_xy1xy2[9]
	# 16-bit signed values
	trim['z2'] = twos_complement(fuse_bits(trim_xy1xy2[0], trim_xy1xy2[1]), 16)
	trim['z3'] = twos_complement(fuse_bits(trim_xy1xy2[6], trim_xy1xy2[7]), 16)
	trim['z4'] = twos_complement(fuse_bits(trim_xyz[0], trim_xyz[1]), 16)
	# 16-bit unsigned value
	trim['z1'] = fuse_bits(trim_xy1xy2[2], trim_xy1xy2[3])
	trim['xyz1'] = fuse_bits(trim_xy1xy2[4], trim_xy1xy2[5])

	#print 'X1: ', trim['x1']
	#print 'X2: ', trim['x2']
	#print 'Y1: ', trim['y1']
	#print 'Y2: ', trim['y2']
	#print 'XY1: ', trim['xy1']
	#print 'XY2: ', trim['xy2']
	#print 'Z1: ', trim['z1']
	#print 'Z2: ', trim['z2']
	#print 'Z3: ', trim['z3']
	#print 'Z4: ', trim['z4']
	#print 'XYZ1: ', trim['xyz1']

	return trim;


def compensate_x(mag_data_x, data_rhall, trim_data):
	# Overflow condition check
	if ((mag_data_x != -4096) and (data_rhall != 0) and (trim_data['xyz1'] != 0)):
		#/*Processing compensation equations*/
		process_comp_x0 = trim_data['xyz1'] * 16384.0 / data_rhall
		retval = process_comp_x0 - 16384.0
		process_comp_x1 = trim_data['xy2'] * (retval * retval / 268435456.0)
		process_comp_x2 = process_comp_x1 + retval * (trim_data['xy1']) / 16384.0
		process_comp_x3 = trim_data['x2'] + 160.0
		process_comp_x4 = mag_data_x * ((process_comp_x2 + 256.0) * process_comp_x3)
		retval = ((process_comp_x4 / 8192.0) + (trim_data['x1'] * 8.0)) / 16.0
	else:
		#/* overflow, set output to 0.0f */
		retval = 0.0

	return retval

def compensate_y(mag_data_y, data_rhall, trim_data):
	# Overflow condition check
	if ((mag_data_y != -4096) and (data_rhall != 0) and (trim_data['xyz1'] != 0)):
		#/*Processing compensation equations*/
		process_comp_y0 = trim_data['xyz1'] * 16384.0 / data_rhall
		retval = process_comp_y0 - 16384.0
		process_comp_y1 = trim_data['xy2'] * (retval * retval / 268435456.0)
		process_comp_y2 = process_comp_y1 + retval * (trim_data['xy1']) / 16384.0
		process_comp_y3 = trim_data['y2'] + 160.0
		process_comp_y4 = mag_data_y * ((process_comp_y2 + 256.0) * process_comp_y3)
		retval = ((process_comp_y4 / 8192.0) + (trim_data['y1'] * 8.0)) / 16.0
	else:
		#/* overflow, set output to 0.0f */
		retval = 0.0

	return retval

def compensate_z(mag_data_z, data_rhall, trim_data):
	# Overflow condition check
	if ((mag_data_z != -16384) and (trim_data['z2'] != 0) and (trim_data['z1'] != 0) and (data_rhall != 0) and (trim_data['xyz1'] != 0)):
		#/*Processing compensation equations*/
		process_comp_z0 = (mag_data_z) - (trim_data['z4'])
		process_comp_z1 = (data_rhall) - (trim_data['xyz1'])
		process_comp_z2 = ((trim_data['z3']) * process_comp_z1)
		process_comp_z3 = (trim_data['z1']) * (data_rhall) / 32768.0
		process_comp_z4 = (trim_data['z2']) + process_comp_z3
		process_comp_z5 = (process_comp_z0 * 131072.0) - process_comp_z2
		retval = (process_comp_z5 / ((process_comp_z4) * 4.0)) / 16.0
	else:
		#/* overflow, set output to 0.0f */
		retval = 0.0

	return retval


def configure_bmi150():
	print 'Configuring BMM150'
	bus = smbus.SMBus(2)
	ret = bus.write_byte_data(address, Aux_Control, 0x01)	#Set Power Control bit to en
	time.sleep(0.05)
	ret = bus.write_byte_data(address, Aux_Op_Mode, 0x00)	#Set Operation mode to Normal
	time.sleep(0.05)

	return bus

def check_data_ready(bus):
	ret = bus.read_byte_data(address, Aux_HR_lsb)
	return ret & 0x01 == 0x01


def read_mag_frame(bus, trim):
	if(check_data_ready(bus)):
		ret = bus.read_i2c_block_data(address, Aux_x_lsb, 8)
		#print 'Raw: ', ret
		raw_x = twos_complement((ret[1]*32 + (ret[0]>>3)), 13)
		raw_y = twos_complement((ret[3]*32 + (ret[2]>>3)), 13)
		raw_z = twos_complement((ret[5]*128 + (ret[4]>>1)), 15)
		Rhall = twos_complement((ret[7]*64 + (ret[6]>>2)), 14)
		#print 'Raw: ', raw_x, raw_y, raw_z, Rhall

		x = compensate_x(raw_x, Rhall, trim)
		y = compensate_y(raw_y, Rhall, trim)
		z = compensate_y(raw_z, Rhall, trim)

		return [x, y, z]
	return -1

if __name__=="__main__":
	bus = configure_bmi150()
	trim = read_trim_registers(bus)
	count = 0

	print 'STARTING LOOP'
	while (count < 10):
		check = read_mag_frame(bus, trim)
		if(check != -1):
			time.sleep(0.1)

			print check
			[x, y, z] = check
		else:
			print 'Read Error'

		count += 1
		check = 0
