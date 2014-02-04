#!/usr/bin/python

# from MotorController import MotorController
from Compass import Compass
from pprint import pprint
import time, signal, sys


def signal_handler( signal, frame ):
	sys.exit(0)


# Capture control-c presses
signal.signal( signal.SIGINT, signal_handler )




compass = Compass( interrupt = 25 )
compass.setConfig( rate = Compass.Config.Rate.Hz_03_00, samples = Compass.Config.Samples.Two, gain = Compass.Config.Gain.Ga_0_9 )

# compass.singleMeasurement()
# compass.singleMeasurement()
# compass.singleMeasurement()
# time.sleep(2)

compass.run()
time.sleep(4)
print(compass.interrupt_count)
compass.stop()
time.sleep(2)
compass.run()
time.sleep(4)
print(compass.interrupt_count)



# motors = MotorController()

# time.sleep(10)
# print( motors.count )
# sys.exit(0)

# motors.run( 1 )
# time.sleep( 2 )
# # motors.run( -1 )
# time.sleep( 2 )
# motors.run( 0 )

# print( motors.count )