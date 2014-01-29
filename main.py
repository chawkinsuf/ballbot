#!/usr/bin/python

from MotorController import MotorController
import time, signal, sys


def signal_handler( signal, frame ):
	sys.exit(0)


# Capture control-c presses
signal.signal( signal.SIGINT, signal_handler )

motors = MotorController()

motors.run( 1 )
time.sleep( 2 )
motors.run( -1 )
time.sleep( 2 )
motors.run( 0 )