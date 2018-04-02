'''
==============================================================
Author:			Matthew Wnuk
Business:		None of Yours Incorporated
Date Modified:		Feb 2018
Discription:		Register Map for BMI_150 Magnetometer
==============================================================
Notes:
	Default register value for PowerControl is listed as 1, but set to 0. (this may be a function of configuration by the Intel-Aero RTF in which I am accessing the sensor). This must be changed before any operation with the sensor.

Page numbers refer to Data Sheet DS001-01-786480
'''


address = 0x12

Aux_Chip_ID = 0x40			#Chip ID register, value: 0x32	p23

###################################################
#	DATA Readings Register Map
###################################################
Aux_x_lsb = 0x42			#LSB of X axis mag field	p23
Aux_x_msb = 0x43			#MSB of X axis mag field	p23
Aux_y_lsb = 0x44			#LSB of Y axis mag field	p24
Aux_y_msb = 0x45			#MSB of Y axis mag field	p24
Aux_z_lsb = 0x46			#LSB of Z axis mag field	p24
Aux_z_msb = 0x47			#MSB of Z axis mag field	p25
Aux_HR_lsb = 0x48			#LSB of Hall resistance		p25
Aux_HR_msb = 0x49			#MSB of Hall resistance		p25

###################################################
#	Configuration Register Map
###################################################
Aux_Int_Stat = 0x4A			#Interrupt Status register	p26
Aux_Control = 0x4B			#Power Control Register		p26
Aux_Op_Mode = 0x4C			#Operational mode register	p27

Aux_Low_Thresh = 0x4F			#Low Threshold Interrupt 	p29
Aux_High_Thresh = 0x50			#High Threshold Interrupt 	p30
Aux_Rep_Control_XY = 0x51		#Repetitions control X/Y  	p30
Aux_Rep_Control_Z = 0x52		#Repetitions control Z  	p30


###################################################
#	Interrupt Register Map
###################################################
Aux_Int_En = 0x4D			#Interrupt Control register	p28
Aux_Int_En2 = 0x4E			#Interrupt Control register 2	p28

###################################################
#	Trim Register Map
###################################################
BMM150_DIG_X1                = 0x5D
BMM150_DIG_Y1                = 0x5E
BMM150_DIG_Z4_LSB            = 0x62
BMM150_DIG_Z4_MSB            = 0x63
BMM150_DIG_X2                = 0x64
BMM150_DIG_Y2                = 0x65
BMM150_DIG_Z2_LSB            = 0x68
BMM150_DIG_Z2_MSB            = 0x69
BMM150_DIG_Z1_LSB            = 0x6A
BMM150_DIG_Z1_MSB            = 0x6B
BMM150_DIG_XYZ1_LSB          = 0x6C
BMM150_DIG_XYZ1_MSB          = 0x6D
BMM150_DIG_Z3_LSB            = 0x6E
BMM150_DIG_Z3_MSB            = 0x6F
BMM150_DIG_XY2               = 0x70
BMM150_DIG_XY1               = 0x71
