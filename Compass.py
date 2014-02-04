import ctypes, atexit, math, time
import RPi.GPIO as GPIO
from Adafruit_I2C import Adafruit_I2C

# ============= Module for =============
# HMC5883L : 3-Axis Digital Compass
# ======================================

class Compass:

	Address				= 0x1e

	class Register:
		ConfigA			= 0x00
		ConfigB			= 0x01
		Mode			= 0x02
		X_MSB			= 0x03
		X_LSB			= 0x04
		Z_MSB			= 0x05
		Z_LSB			= 0x06
		Y_MSB			= 0x07
		Y_LSB			= 0x08
		Status			= 0x09
		ID_A			= 0x10
		ID_B			= 0x11
		ID_C			= 0x12

	class Mode:
		Continuous		= 0x00
		Single			= 0x01
		Idle			= 0x02

	class Config:
		class Samples:
			One			= 0x00
			Two			= 0x01
			Four		= 0x02
			Eight		= 0x03

		class Rate:
			Hz_00_75	= 0x00
			Hz_01_50	= 0x01
			Hz_03_00	= 0x02
			Hz_07_50	= 0x03
			Hz_15_00	= 0x04
			Hz_30_00	= 0x05
			Hz_75_00	= 0x06

		class Measurement:
			Normal		= 0x00
			Positive	= 0x01
			Negative	= 0x02

		class Gain:
			Ga_0_9		= 0x00
			Ga_1_3		= 0x01
			Ga_1_9		= 0x02
			Ga_2_5		= 0x03
			Ga_4_0		= 0x04
			Ga_4_7		= 0x05
			Ga_5_6		= 0x06
			Ga_8_1		= 0x07

	# Setup config defaults (these are the chip defaults)
	samples		= Config.Samples.One
	rate		= Config.Rate.Hz_15_00
	measurement	= Config.Measurement.Normal
	gain		= Config.Gain.Ga_1_3

	def __init__( self, interrupt = None, callback = None ):

		# Initialize the module
		self.i2c = Adafruit_I2C( self.Address )

		# Start in idle mode
		self.i2c.write8( self.Register.Mode, self.Mode.Idle )

		# Register an exit function
		atexit.register( self._exit_handler )

		# Make sure we are on our default config values
		self.data_a = None
		self.data_b = None
		self.setConfig()

		# Initialize interrupt variables
		self.interrupt_pin 		= interrupt
		self.interrupt_count 	= 0
		self.interrupt_callback = callback

		# Setup a GPIO interrupt
		if self.interrupt_pin is not None:
			print( 'Setting interrupt on pin %d' % interrupt )
			GPIO.setmode( GPIO.BCM )
			GPIO.setup( self.interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN )
			GPIO.add_event_detect( self.interrupt_pin, GPIO.FALLING, callback=self._interrupt_callback )

	# Read the hardware interrupt pin
	def _interrupt_callback( self, channel ):
		print( 'Interrupt on channel %d' % channel )
		self.interrupt_count += 1
		data = self.getMeasurement()
		if callable( self.interrupt_callback ):
			self.interrupt_callback( data )

	# Cleanup
	def _exit_handler( self ):
		self.stop()
		GPIO.remove_event_detect( self.interrupt_pin )
		GPIO.cleanup()

	# Set the options available on the chip
	def setConfig( self, samples = None, rate = None, measurement = None, gain = None ):

		# Only update if the value was given
		if samples is not None:
			self.samples = samples
		if rate is not None:
			self.rate = rate
		if measurement is not None:
			self.measurement = measurement
		if gain is not None:
			self.gain = gain

		# Formt the binary data to send
		data_a = self.samples << 5 | self.rate << 2 | self.measurement
		data_b = self.gain << 5

		# Send the data
		if ( data_a != self.data_a ):
			print( 'Sending %s to ConfigA' % format( data_a, '#010b' ) )
			self.i2c.write8( self.Register.ConfigA, data_a )
			self.data_a = data_a

		if ( data_b != self.data_b ):
			print( 'Sending %s to ConfigB' % format( data_b, '#010b' ) )
			self.i2c.write8( self.Register.ConfigB, data_b )
			self.data_b = data_b

	# Set the chip to continuous mode
	def run( self ):
		self.i2c.write8( self.Register.Mode, self.Mode.Continuous )		# Still working on why I have to execute this sequence to get
		self.i2c.readU8( self.Register.Mode )							# continuous mode to operate reliably. With only a single write,
		self.i2c.write8( self.Register.Mode, self.Mode.Continuous )		# the mode is only enabled every other time the mode is enabled.

	# Set the chip to idle mode
	def stop( self ):
		self.i2c.write8( self.Register.Mode, self.Mode.Idle )

	# Triggers the chip to issue a single measurement and returns the value if no interrupt is set
	def singleMeasurement( self, force = False ):

		# Set chip into single measurement mode
		self.i2c.write8( self.Register.Mode, self.Mode.Single )

		# The specs specify a 6 ms wait before the measurement is ready
		time.sleep( 0.01 )

		# If there is no interrupt, return the measurement now
		if self.interrupt_pin is None:
			return self.getMeasurement()

	# Read two bytes and process to a signed short integer
	def readAxis( self, reg_msb, reg_lsb ):
		msb = self.i2c.readU8( reg_msb )
		lsb = self.i2c.readU8( reg_lsb )
		data = msb << 8 | lsb
		# print( format( data, '#018b' ) )
		return ctypes.c_short( data ).value

	# Read the current measurement on the chip
	def getMeasurement( self ):
		x = self.readAxis( self.Register.X_MSB, self.Register.X_LSB )
		y = self.readAxis( self.Register.Y_MSB, self.Register.Y_LSB )
		z = self.readAxis( self.Register.Z_MSB, self.Register.Z_LSB )

		azimuth = math.degrees( math.atan2( x, y ) )
		print( '%s [ %0.2f ]' % ( (x, y, z), azimuth ) )
		return azimuth