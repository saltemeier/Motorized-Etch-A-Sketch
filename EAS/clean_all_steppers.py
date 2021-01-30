# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 10:50:27 2019

@author: steve
"""
from sys import path
path.append(r'/home/pi/EAS/steppers')

import stepper_control as sc

hMotor = sc.stepper(6, 19, 13, 26, _name="hMotor")
eMotor = sc.stepper(12, 20, 16, 21, _name="eMotor")
vMotor = sc.stepper(4, 27, 17,  22, _name="vMotor")

hMotor.turn_off()
vMotor.turn_off()
eMotor.turn_off()

hMotor.cleanup()
