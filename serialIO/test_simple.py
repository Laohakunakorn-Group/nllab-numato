import serial

PORTNAME = '/dev/tty.usbmodem14201' # set port name here
ser = serial.Serial(PORTNAME) # open serial port
print(ser.name)
ser.close()