# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 11:06:43 2019

This differs from stepper_control.py in that the motor speed is not as precisely controlled,
but the code and interface become simpler

@author: steve
"""

moveStepInc = 1000

import datetime as dt
import RPi.GPIO as GPIO

halfstep = [[1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1],
            [1,0,0,1]]

class stepper:
    
    #class atrributes - none


    #instance attributes
    def __init__(self, _A, _A_bar, _B, _B_bar, _startP=0, _clockwise = 1, _name = 'A', _backlash = 0):
        self.A = _A
        self.A_bar = _A_bar
        self.B = _B
        self.B_bar = _B_bar
        self.currPos = _startP
        self.nextStep = 0
        self.clockwise = _clockwise
        self.name = _name
        self.lastMotorStep = dt.datetime.now()
        self.motorStepInc = dt.timedelta(microseconds=10000)
        self.backlash = _backlash  #The number of (half) steps to take to adjust for backlash
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.A, GPIO.OUT)
        GPIO.setup(self.A_bar, GPIO.OUT)
        GPIO.setup(self.B, GPIO.OUT)
        GPIO.setup(self.B_bar, GPIO.OUT)


    def set_clockwise(self, _clockwise):
        clockwise = _clockwise
        if self.clockwise != clockwise:
            #Chansging directiion so make correction for backlash
            currPos = startPos = self.get_currPos()
            self.clockwise = clockwise
            if self.clockwise:
                #Decreasing position
                destination = currPos - self.backlash
            else:
                #Increasing position
                destination = currPos + self.backlash

            #Make the required backlash move
            while currPos != destination:
                currPos = self.poke()

            #Reset currPos to correct value
            self.set_currPos(startPos)
            return True
        else:
#            print("clockwise is unchanged as", self.clockwise)
            return False


    def set_motorStepInc(self, _motorStepInc):
        self.motorStepInc = dt.timedelta(microseconds=_motorStepInc)
#        print("New motor step increment:", self.motorStepInc)


    def get_motorStepInc(self):
        return self.motorStepInc


    def set_currPos(self, _currPos):
        self.currPos = _currPos


    def get_currPos(self):
        return self.currPos


    def get_clockwise(self):
        return self.clockwise


    def reset_lastMotorStep(self):
        self.lastMotorStep = dt.datetime.now()


    def set_backlash(self, _backlash):
        self.backlash = _backlash


    def turn_off(self):
        GPIO.output(self.A, GPIO.LOW)
        GPIO.output(self.A_bar, GPIO.LOW)
        GPIO.output(self.B, GPIO.LOW)
        GPIO.output(self.B_bar, GPIO.LOW)


    def cleanup(self):
        GPIO.cleanup()


    def poke(self):
        checkTime = dt.datetime.now()
#        print("lastMotorStep:", self.lastMotorStep)
#        print("actual:", (checkTime - self.lastMotorStep), "    target:", self.motorStepInc)
        if (checkTime - self.lastMotorStep) > self.motorStepInc:
            self.lastMotorStep = checkTime
#            print("checkTime:", checkTime, "    lastMotorStep:", self.lastMotorStep)
#       print("nextStep:", self.nextStep)

            GPIO.output(self.A, halfstep[self.nextStep][0])
            GPIO.output(self.B, halfstep[self.nextStep][1])
            GPIO.output(self.A_bar, halfstep[self.nextStep][2])
            GPIO.output(self.B_bar, halfstep[self.nextStep][3])


            if self.clockwise:
                self.nextStep += 1
                self.currPos -= 1
            else:
                self.nextStep -= 1
                self.currPos += 1

            if (self.nextStep == 8): self.nextStep = 0;
            if (self.nextStep == -1): self.nextStep = 7;

        return(self.currPos)


    def go_to(self, position):
#        print(self.name, "going to:", position, "from", self.currPos)
        if self.currPos > position:  #Need to move down
            self.set_clockwise(True)
        else:
            self.set_clockwise(False)

        #Move to position
        while self.currPos != position:
#            print(self.name, "\tcurrPos:", self.currPos, "\ttarget:", position)
            self.poke()

