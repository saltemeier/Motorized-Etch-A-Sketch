# -*- coding: utf-8 -*-
"""
@author: steve

Started from a copy of complex_harmongraph.py on 1/12/20.

"""

import math as np


class  cplx_hgraph:

    def __init__(self, _hMotor, _vMotor, _x1Amp, _x1Per, _y1Amp, _y1Per, _x2Amp, _x2Per, _y2Amp, _y2Per, _rotatePer,
                 _ampDecay=0.95, _stopSize=0.25, _x1Init=0, _y1Init=0, _x2Init=0, _y2Init=0, _minStepInc=2000, _stepLimit=1000000):
        self.hMotor = _hMotor
        self.vMotor = _vMotor
        self.x1Amp = float(_x1Amp)
        self.x1Per = float(_x1Per)
        self.x2Amp = float(_x2Amp)
        self.x2Per = float(_x2Per)
        self.y1Amp = float(_y1Amp)
        self.y1Per = float(_y1Per)
        self.y2Amp = float(_y2Amp)
        self.y2Per = float(_y2Per)
        self.rotatePer = _rotatePer
        self.ampDecay = _ampDecay
        self.stopSize = _stopSize
        self.x1Init = _x1Init
        self.x2Init = _x2Init
        self.y1Init = _y1Init
        self.y2Init = _y2Init
        self.minStepInc = _minStepInc
        self.stepLimit = _stepLimit
        self.counter = 0.0
        self.hDecay = self.vDecay = self.ampDecay
        self.done = False

#        print("x1Init:", self.x1Init, "   x1Amp:", self.x1Amp, "  x1Per:", self.x1Per)
#        print("x2Init:", self.x2Init, "   x2Amp:", self.x2Amp, "  x2Per:", self.x2Per)
#        print("y1Init:", self.y1Init, "   y1Amp:", self.y1Amp, "  y1Per:", self.y1Per)
#        print("y2Init:", self.y2Init, "   y2Amp:", self.y2Amp, "  y2Per:", self.y2Per)

        #Calculate the formula input that corresponds to the entered coordinates
        if self.x1Amp > 0:
#            print("ratio:", self.x1Init/self.x1Amp)
#            print("asin:", np.asin(self.x1Init/self.x1Amp))
#            print("x1Init:", self.x1Init)
            self.x1Init = np.asin(self.x1Init/self.x1Amp)*self.x1Per/np.pi
        else:
            self.x1Init = 0
        if self.x2Amp > 0:
            self.x2Init = np.asin(self.x2Init/self.x2Amp)*self.x2Per/np.pi
#            print("x2Init:", self.x2Init)
        else:
            self.x2Init = 0
        if self.y1Amp > 0:
            self.y1Init = np.asin(self.y1Init/self.y1Amp)*self.y1Per/np.pi
#            print("y1Init:", self.y1Init)
        else:
            self.y1Init = 0
        if self.y2Amp > 0:
            self.y2Init = np.asin(self.y2Init/self.y2Amp)*self.y2Per/np.pi
#            print("y2Init:", self.y2Init)
        else:
            self.y2Init = 0

        #Set up for first move
        self.calc_next_move()


    def calc_next_move(self):
        newXVal = self.x1Amp*(self.hDecay**(self.counter/16000.0))*np.sin((self.counter+self.x1Init)/self.x1Per*np.pi) + \
                  self.x2Amp*(self.hDecay**(self.counter/16000.0))*np.sin((self.counter+self.x2Init)/self.x2Per*np.pi)
        newYVal = self.y1Amp*(self.vDecay**(self.counter/16000.0))*np.sin((self.counter+self.y1Init)/self.y1Per*np.pi) + \
                  self.y2Amp*(self.vDecay**(self.counter/16000.0))*np.sin((self.counter+self.y2Init)/self.y2Per*np.pi)

        #Convert these values to polar coordinates
        r = (newXVal**2+newYVal**2)**0.5
        if newXVal != 0:
            theta = np.atan(newYVal/newXVal)
        else:
            theta = np.atan(newYVal/0.0000001)

        if newXVal < 0:
            theta += np.pi
        elif newYVal   < 0:
            theta += 2*np.pi

        #Add in the rotational component of the drawing platgform
        if not self.rotatePer == 0:
            theta += (2.0*np.pi)*((self.counter/self.rotatePer)%1)

        #Convert back to cartesion coordinates
        self.hDest = round(r*np.cos(theta), 0)
        self.vDest = round(r*np.sin(theta), 0)

#        print(self.counter, "\tx: ", self.hDest, "\ty: ", self.vDest)

        #Now set up to move to the new xVal and yVal
        #Get the current position
        hCurrPos = self.hMotor.get_currPos()
        vCurrPos = self.vMotor.get_currPos()

        #Set the clockwise variable for each motor
        if hCurrPos > self.hDest:
            if not self.hMotor.get_clockwise():
                self.hMotor.set_clockwise(True)
        elif hCurrPos < self.hDest:
            if self.hMotor.get_clockwise():
                self.hMotor.set_clockwise(False)

        if vCurrPos > self.vDest:
            if not self.vMotor.get_clockwise():
                self.vMotor.set_clockwise(True)
        elif vCurrPos < self.vDest:
            if self.vMotor.get_clockwise():
                self.vMotor.set_clockwise(False)

        #Set the correct speed for each motor to move to the new destination
        if (abs(self.hDest - hCurrPos) > abs(self.vDest - vCurrPos)):
            self.hMotor.set_motorStepInc(self.minStepInc)
            if (self.vDest - vCurrPos) != 0:
                self.vMotor.set_motorStepInc(round(self.minStepInc*abs(self.hDest - hCurrPos)/abs(self.vDest - vCurrPos), 0))
        else:
            self.vMotor.set_motorStepInc(self.minStepInc)
            if (self.hDest - hCurrPos) != 0:
                self.hMotor.set_motorStepInc(round(self.minStepInc*abs(self.vDest - vCurrPos)/abs(self.hDest - hCurrPos), 0))

        #Reset the last motor step to tjhe current time
        self.hMotor.reset_lastMotorStep()
        self.vMotor.reset_lastMotorStep()


    def poke(self):

        #Return True if the drawing is complete, returns False otherwise

        #Get the current position
        hCurrPos = self.hMotor.get_currPos()
        vCurrPos = self.vMotor.get_currPos()

        if hCurrPos != self.hDest: hCurrPos = self.hMotor.poke()
        if vCurrPos != self.vDest: vCurrPos = self.vMotor.poke()

        if hCurrPos == self.hDest and vCurrPos == self.vDest:
            if (self.hDecay**(self.counter/16000.0) < self.stopSize) or (self.vDecay**(self.counter/16000.0) < self.stopSize) or (self.counter >= self.stepLimit):
#                print("hDecay:", self.hDecay)
#                print("vDecay:", self.vDecay)
                return True

            #Calculate the next destination
            self.calc_next_move()
            self.counter += 1.0

        return False

