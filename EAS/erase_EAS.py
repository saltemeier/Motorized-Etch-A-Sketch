# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 14:21:16 2019

@author: steve

Code Rotates the EAS forward x steps, back y steps, forward y steps, back y steps, 
forward y steps, and then back x steps to return to its original position.
"""

#import stepper_control as sc

numShakes = 3  #Number of times to shake the EAS
shakeRatio = 0.75  #shake lower bound as percent of shake upper bound

def erase(motor, speed, stepsPerRev, numTurns, numShakes, shakeRatio):

    '''
    motor is an object of class stepper
    speed is in revolutions per second for the smaller gear
    stepsPerRev is number of steps in one full revolution for the motor
    numTurns is the number of turns the smaller gear should make when erasing
    '''

    stepIncrement = 1000000/(stepsPerRev*speed)
    motor.set_motorStepInc(stepIncrement)

    startPos = currPos = motor.get_currPos()
    print("startPos:", startPos, "currPos:", currPos)

    #Rotate forward
    motor.set_clockwise(False)
    print("destination:", startPos + numTurns*stepsPerRev)
    motor.reset_lastMotorStep()
    while abs(currPos) < startPos + numTurns*stepsPerRev:
        currPos = motor.poke()
#        print (currPos)

    #Rotate back and forth
    for shake in range(numShakes):
        motor.set_clockwise(not motor.get_clockwise())
        while abs(currPos) > startPos + numTurns*stepsPerRev*shakeRatio:
            currPos = motor.poke()
        motor.set_clockwise(not motor.get_clockwise())
        while abs(currPos) < startPos + numTurns*stepsPerRev:
            currPos = motor.poke()


    #Rotate back to starting position
    motor.set_clockwise(not motor.get_clockwise())
    while abs(currPos) > startPos:
        currPos = motor.poke()
