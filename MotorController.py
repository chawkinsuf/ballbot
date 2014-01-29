import time, atexit
import RPi.GPIO as GPIO
from Adafruit_PWM_Servo_Driver import PWM
from devtools import rangetest

PWM_ADDRESS = 0x40
PWM_FREQUENCY = 1000
PWM_BITS = 12
PWM_RANGE = 2 ** PWM_BITS

L_GPIO = 24
R_GPIO = 25

L_PWM = 14
R_PWM = 15

SPEED_MAX = 0
SPEED_MIN = 950



class MotorController:

	def __init__( self ):

		# Register and exit function
		atexit.register( self._exit_handler )

		# Initialize the gpio pins
		GPIO.setmode( GPIO.BCM )
		GPIO.setup( L_GPIO, GPIO.OUT )
		GPIO.setup( R_GPIO, GPIO.OUT )

		# Initialize the pwm board
		self.pwm = PWM( PWM_ADDRESS )
		self.pwm.setPWMFreq( PWM_FREQUENCY )

	def _exit_handler( self ):
		self.stop()
		GPIO.cleanup()

	def _convert_speed( self, speed ):
		return ( SPEED_MAX - SPEED_MIN ) * speed + SPEED_MIN

	def stop( self ):
		GPIO.output( L_GPIO, GPIO.LOW )
		GPIO.output( R_GPIO, GPIO.LOW )

	@rangetest( speed = (0.0, 1.0) )
	def forward( self, speed, stop = None ):

		# Get the pulse length from our speed
		pulse = self._convert_speed( speed )

		# Set the speed and direction
		pwm.setPWM( L_PWM, 0, pulse )
		pwm.setPWM( R_PWM, 0, pulse )

		# Turn the motors on
		GPIO.output( L_GPIO, GPIO.HIGH )
		GPIO.output( R_GPIO, GPIO.HIGH )

		if ( not stop is None):

			# Sleep the specified time
			time.sleep( stop )

			# Turn off the motors
			GPIO.output( L_GPIO, GPIO.LOW )
			GPIO.output( R_GPIO, GPIO.LOW )

	@rangetest( speed = (0.0, 1.0) )
	def reverse( self, speed, stop = None ):

		# Get the pulse length from our speed
		pulse = self._convert_speed( speed )

		# Set the speed and direction
		pwm.setPWM( L_PWM, 0, PWM_RANGE - pulse )
		pwm.setPWM( R_PWM, 0, PWM_RANGE - pulse )

		# Turn the motors on
		GPIO.output( L_GPIO, GPIO.HIGH )
		GPIO.output( R_GPIO, GPIO.HIGH )

		if ( not stop is None):

			# Sleep the specified time
			time.sleep( stop )

			# Turn off the motors
			GPIO.output( L_GPIO, GPIO.LOW )
			GPIO.output( R_GPIO, GPIO.LOW )
