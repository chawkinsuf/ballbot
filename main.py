#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import RPi.GPIO as GPIO
import time, signal, sys

L_GPIO = 24
R_GPIO = 25

L_PWM = 14
R_PWM = 15


def signal_handler( signal, frame ):

	# Stop the motors
	GPIO.output( L_GPIO, GPIO.LOW )
	GPIO.output( R_GPIO, GPIO.LOW )

	# Exit
	GPIO.cleanup()
	sys.exit(0)


# Capture control-c presses
signal.signal( signal.SIGINT, signal_handler )

# Initialize the gpio pins
GPIO.setmode( GPIO.BCM )
GPIO.setup( L_GPIO, GPIO.OUT )
GPIO.setup( R_GPIO, GPIO.OUT )

# Initialize the pwn board
pwm = PWM( 0x40 )
pwm.setPWMFreq( 1000 )

# Enable both motors
GPIO.output( L_GPIO, GPIO.HIGH )
GPIO.output( R_GPIO, GPIO.HIGH )

# Test forward speeds
print('Forward')
for i in range(0,1000,10):
	pwm.setPWM( L_PWM, 0, i )
	pwm.setPWM( R_PWM, 0, i )
	time.sleep( 0.05 )
	if i % 50 == 0:
		print( i )

# Test reverse speeds
print('Reverse')
for i in range(0,1000,10):
	pwm.setPWM( L_PWM, 0, 4096-i )
	pwm.setPWM( R_PWM, 0, 4096-i )
	time.sleep( 0.05 )
	if i % 50 == 0:
		print( i )

time.sleep(2)

# Forward full
pwm.setPWM( L_PWM, 0, 4096 )
pwm.setPWM( R_PWM, 0, 4096 )

time.sleep(2)

# Forward backward
pwm.setPWM( L_PWM, 4096, 0 )
pwm.setPWM( R_PWM, 4096, 0 )

time.sleep(2)

# Turn left
pwm.setPWM( L_PWM, 0, 4096 )
pwm.setPWM( R_PWM, 4096, 0 )

time.sleep(2)

# Turn right
pwm.setPWM( L_PWM, 4096, 0 )
pwm.setPWM( R_PWM, 0, 4096 )

time.sleep(2)

# Stop the motors
GPIO.output( L_GPIO, GPIO.LOW )
GPIO.output( R_GPIO, GPIO.LOW )

# Exit
GPIO.cleanup()
