# Control Numato 32-relay USB board with serial commands

import serial
import time

PORTNAME = '/dev/tty.usbmodem14201' # set port name here

# Configure serial communication
ser = serial.Serial() 
ser.baudrate = 9600
ser.port = PORTNAME
ser.bytesize = 8 
ser.parity = 'N'
ser.stopbits = 1
ser.timeout = 0 # second

# Relay status to send
INPUT = '0000'+'0000'+'0000'+'0000'+'0000'+'0000'+'0000'+'0000'
inputhex = hex(int(INPUT,2))[2:].zfill(8)

# Open port
ser.open()
print('Port open')

# Write all 
CMD = 'relay writeall '+inputhex+'\r' # hex numbers lower case
ser.write(CMD.encode()) # convert to byte array
time.sleep(0.05)
ser.flushInput()

ser.write(b'relay readall\r')
time.sleep(0.05)
ser_bytes = ser.readlines() # Always 3 elements
output = ser_bytes[len(ser_bytes)-2].decode("utf-8") # Penultimate element

ser.close()
if not ser.close():
	print('Port closed')

# Print relay status
outputbin = str(bin(int(output, 16)))[2:].zfill(32)
print(outputbin)