import time, atexit
import RPi.GPIO as GPIO
from Adafruit_PWM_Servo_Driver import PWM
from devtools import rangetest
from datetime import datetime

PWM_ADDRESS = 0x40
PWM_FREQUENCY = 1000
PWM_BITS = 12
PWM_RANGE = 2 ** PWM_BITS

L_ENCODER = 22
R_ENCODER = 23

L_GPIO = 24
R_GPIO = 25

L_PWM = 14
R_PWM = 15

SPEED_MAX = 1
SPEED_MIN = 950



class MotorController:

	def __init__( self ):

		# Register an exit function
		atexit.register( self._exit_handler )

		# Initialize the gpio pins
		GPIO.setmode( GPIO.BCM )
		GPIO.setup( L_GPIO, GPIO.OUT )
		GPIO.setup( R_GPIO, GPIO.OUT )

		GPIO.setup( L_ENCODER, GPIO.IN, pull_up_down=GPIO.PUD_UP )
		GPIO.setup( R_ENCODER, GPIO.IN, pull_up_down=GPIO.PUD_UP )

		GPIO.add_event_detect( L_ENCODER, GPIO.FALLING, callback=self.encoder, bouncetime=5 )
		GPIO.add_event_detect( R_ENCODER, GPIO.FALLING, callback=self.encoder, bouncetime=5 )

		self.last  = { L_ENCODER: 0, R_ENCODER: 0 }
		self.count = { L_ENCODER: 0, R_ENCODER: 0 }

		# Initialize the pwm board
		self.pwm = PWM( PWM_ADDRESS )
		self.pwm.setPWMFreq( PWM_FREQUENCY )

		# Initialize variables
		self.speed = 0

	def encoder( self, channel ):
		now = datetime.now()
		if self.last[ channel ] == 0:
			diff = 0
		else:
			diff = now - self.last[ channel ]

		self.last [ channel ] = now
		self.count[ channel ] += 1
		print( "%d - %s" % ( channel, diff ) )

	def _exit_handler( self ):
		self.stop()
		GPIO.cleanup()

	def _convert_speed( self, speed ):
		return int( ( SPEED_MAX - SPEED_MIN ) * speed + SPEED_MIN )

	@rangetest( speed = (-1.0, 1.0) )
	def run( self, speed ):

		# Store the current speed
		self.speed = speed

		# See if we need to stop
		if ( speed == 0 ):
			self.stop()
			return

		# Get the direction
		forward = ( speed > 0 )

		# Get the pulse length from our speed
		speed = abs( speed )
		pulse = self._convert_speed( speed )

		# Adjust the pulse for direction
		if ( not forward ):
			pulse = PWM_RANGE - pulse

		# Set the speed and direction
		self.pwm.setPWM( L_PWM, 0, pulse )
		self.pwm.setPWM( R_PWM, 0, pulse )

		# Turn on the motors
		self.start()

	def turn( self ):

		# Set the speed and direction
		self.pwm.setPWM( L_PWM, 0, 1 )
		self.pwm.setPWM( R_PWM, 0, PWM_RANGE - 1 )

		# Turn on the motors
		self.start()

	def start( self ):
		GPIO.output( L_GPIO, GPIO.HIGH )
		GPIO.output( R_GPIO, GPIO.HIGH )

	def stop( self ):
		GPIO.output( L_GPIO, GPIO.LOW )
		GPIO.output( R_GPIO, GPIO.LOW )
