# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 16:14:15 2019

@author: Steve
"""

from math import asin
import datetime as dt

minStepInc = 1000


class  hgStepper:

    def __init__(self, _stepper, _clockwise, _amplitude, _perFactor, _startPos=0, _decay=0.98, _name='A'):
#        print("In init function for hgStepper")
        self.startTime = dt.datetime.now()  #Will track tiome in microseconds from this time
        self.stepper = _stepper
        self.startPos = _startPos
        self.amplitude = float(_amplitude)
        self.perFactor = _perFactor
        self.decay = float(_decay)
        self.cumulativeDecay = 1.0
        self.clockwise = _clockwise
        self.name = _name

        self.currPos = self.stepper.get_currPos()
        self.stepper.set_clockwise(self.clockwise)


#REMEMBER: clockwise means  we are decreasing the position value and counterclockwise means we are increasing the position value


    def update_params(self):

        self.cumulativeDecay = 1
        self.modA = round(self.amplitude*self.cumulativeDecay, 0)

        if self.currPos == self.amplitude:
            self.stepper.set_clockwise(True)
        elif self.currPos == -self.amplitude:
            self.stepper.set_clockwise(False)

        if self.stepper.get_clockwise():
            self.nextPos = self.currPos - 1
        else:
            self.nextPos = self.currPos + 1

        self.lastStep = round(asin(self.currPos/self.modA)/self.perFactor, 0)
        self.nextStep = round(asin(self.nextPos/self.modA)/self.perFactor, 0)
        self.motorStepInc = abs(self.nextStep - self.lastStep)
        print("Setting", self.name, " motorSepInc to", self.motorStepInc)
        self.stepper.set_motorStepInc(self.motorStepInc)
        self.stepper.reset_lastMotorStep()


    def poke(self):
        oldPos = self.stepper.get_currPos()
        newPos = self.stepper.poke();
        backlash = False

        if newPos != oldPos:  #Took a step
            if abs(newPos) == self.modA:  #At top or bottom of sine curve so change direction
                backlash = self.stepper.set_clockwise(not self.stepper.get_clockwise())
            elif newPos == 0:  #at zero, so change cumulativeDecay
                self.cumulativeDecay *= self.decay
                self.modA = round(self.amplitude*self.cumulativeDecay, 0)

            if self.stepper.get_clockwise():
                self.nextPos = newPos - 1
            else:
                self.nextPos = newPos + 1

            self.lastStep = self.nextStep
            self.nextStep = round(asin(self.nextPos/self.modA)/self.perFactor, 0)
            self.motorStepInc = abs(self.nextStep - self.lastStep)

            self.stepper.set_motorStepInc(self.motorStepInc)

        return backlash


    def get_decay(self):
        return self.cumulativeDecay
