from sys import path
path.append(r'/home/pi/EAS/steppers')
path.append(r'/home/pi/EAS/harmonograph')
path.append(r'/home/pi/EAS/cplx_hgraph')
path.append(r'/home/pi/EAS/shade_image')

import stepper_control as sc
import basic_stepper as bs
import harmonograph_control as hc
import cplx_hgraph as cxhg
import erase_EAS as eraser
from sys import modules as modules
from math import asin
from random import randint
from time import time
import shade_image as si
from PIL import Image
from numpy import asarray as np_asarray, uint8 as np_uint8
from os import listdir

import socket
import select
import ast

minMotorStepInc = 2500.0
returnToMain = False  #Variable used to terminate subroutine on ctrl-c
hBacklash = 375   #Backlash correction in steps - horizontal
vBacklash = 365   #Backlash correction in steps - vertical

eraseSpeed = 0.75
numShakes = 1  #Number of times to shake after inverting for an erase


#Function to turn off the motors and release the GPIO pins
def clean_up():
    #This function cleans up the steppers and exits
#    print("Cleaning up and exiting.")
    hMotor.turn_off()
    vMotor.turn_off()


#Function to end the program
def end_program():
    global keepRunning
    clean_up()
    keepRunning = False


def listen():
    global s #This is the socket on which the server listens
    global returnToMain

    #Listen on the socket server
    ready_to_read, ready_to_write, in_error = \
                   select.select([s], [s], [], 0)
    if len(ready_to_read)>0:
        client, address = s.accept()
        data = client.recv(size)

        #Now process the data received as a string.  Should be a function name folowed by a comma  and then a dictionary
        data = data.decode()
        print("String received:", data)
        if data[:4] == "STOP":
#            print("Received STOP command!")
            returnToMain = True
        else:
            if data.find(',') != -1:
                functionName = data[:data.find(',')]
#                print("Function to call is", functionName)
                dictStart = data.find('{')
                dictEnd = data.find('}')
                strDict = data[dictStart:dictEnd+1]

                #Now convert the string to a python dictionary
                funcInputs = ast.literal_eval(strDict)
#                print("Function input dict:", str(funcInputs))
                return functionName, funcInputs

    return None, None


#Function to reset the current position to be (0, 0)
def reset_origin(hMotor, vMotor, inputDict):
    hMotor.set_currPos(0)
    vMotor.set_currPos(0)

    #Move each drawing motor to work out the backlash
    hMotor.go_to(400)
    hMotor.go_to(0)
    vMotor.go_to(400)
    vMotor.go_to(0)

    hMotor.turn_off()
    vMotor.turn_off()


#Function to run the simple harmonograph 
def run_harmonograph(hMotor, vMotor, inputDict):
    #Code to run the simple harmonograph
    global returnToMain
    returnToMain = False
    global s  #This is the socket to listen on

    hPos = inputDict['hPos']
    vPos = inputDict['vPos']
    hRatio = inputDict['hRatio']
    vRatio = inputDict['vRatio']
    hAmp = inputDict['hAmp']
    vAmp = inputDict['vAmp']
    stopPer = inputDict['stopPer']

    #Go to the starting position from current position
#    print("calling go_to with argument", hPos)
    hMotor.go_to(hPos)
    vMotor.go_to(vPos)


    #Erase the harmonograph
    eMotor.set_motorStepInc(10000)
    eMotor.set_clockwise(False)
#    print("Erasing the EAS!")
    eraser.erase(eMotor, eraseSpeed, 1024, 7.5, numShakes, 0.4)
#    print("Done erasing.")
    eMotor.turn_off()

    #Calculate values for stepPer so that motorStepInc never less than minMotorStepInc
    hStepPer = 1/(minMotorStepInc*hAmp)
#    print("hAmp:", hAmp)
#    print("asin:", asin(1/hAmp))
    vStepPer = 1/(minMotorStepInc*vAmp)
#    print("hStepPer:", hStepPer)
#    print("vStepPer:", vStepPer)

    #Now adjust so that ratio of periods is correct without violating minMotorStepInc requirement
    if hStepPer > vStepPer*vRatio/hRatio:
        hStepPer = vStepPer*vRatio/hRatio
    else:
        vStepPer = hStepPer*hRatio/vRatio
#    print("hStepPer:", hStepPer)
#    print("vStepPer:", vStepPer)

    #Need to change the calls to initialize the harmonograph below here
    #Set the initial harmonograoh values
    hAxis = hc.hgStepper(hMotor, 0, hAmp, hStepPer, hPos, 0.98, 'horiz')  #0 is the clockwise value, 0.98 is the decay value
    vAxis = hc.hgStepper(vMotor, 0, vAmp, vStepPer, vPos, 0.98, 'vert')


    #Update the parameters for the harmonograph
    hAxis.update_params()
    vAxis.update_params()

    #Stop when size has decayed beyond a given percent of original size
    done = False
    prevDecay = 2
    while not done:
        if returnToMain: done = True
        if hAxis.poke():
            #Did a backlash correction, so need to reset vAxis 
#            print("hAxis backlash")
            vMotor. reset_lastMotorStep()
        if vAxis.poke():
            #Did a backlash correction, so need to reset hAxis
#            print("vAxis backlash")
            hMotor.reset_lastMotorStep()
        decay = hAxis.get_decay()
        prevDecay = decay
        if hAxis.get_decay()*100 < stopPer:  #Comparing value to percent
    	    done = True
#            print("Stopping with a decay value of", hAxis.get_decay()*100, "compared to limit of", stopPer)

        listen()  #Listen to the server to see if should stop running harmonograph

    hMotor.turn_off()
    vMotor.turn_off()



#Function to run the complex harmonograph 
def run_cplx_hgraph(hMotor, vMotor, inputDict):
    #Code to run the simple harmonograph
    global returnToMain
    returnToMain = False
    global s  #This is the socket to listen on
    global minMotorStepInc

#    print("inputDict:", inputDict)

    x1Amp = inputDict['x1Amp']
    x1Per = inputDict['x1Per']
    x2Amp = inputDict['x2Amp']
    x2Per = inputDict['x2Per']
    y1Amp = inputDict['y1Amp']
    y1Per = inputDict['y1Per']
    y2Amp = inputDict['y2Amp']
    y2Per = inputDict['y2Per']
    rotatePer = inputDict['rotatePer']
    stopSize = inputDict['stopSize']
    ampDecay = inputDict['ampDecay']
    x1Init = inputDict['x1Init']
    x2Init = inputDict['x2Init']
    y1Init = inputDict['y1Init']
    y2Init = inputDict['y2Init']
    if 'stepLimit' in inputDict:
        stepLimit = inputDict['stepLimit']
    else:
        stepLimit = 1000000   #A very large number that should not come into play

    #Go to the starting position from current position
#    print("calling go_to with argument", x1Init + x2Init)
    hMotor.go_to(x1Init + x2Init)
    vMotor.go_to(y1Init + y2Init)

    #Erase the harmonograph
    eMotor.set_motorStepInc(10000)
    eMotor.set_clockwise(False)
#    print("Erasing the EAS!")
    eraser.erase(eMotor, eraseSpeed, 1024, 7.5, numShakes, 0.4)
#    print("Done erasing.")
    eMotor.turn_off()

    #Now run the complex harmonograph
    myCplxHgraph = cxhg.cplx_hgraph(hMotor, vMotor, x1Amp, x1Per, y1Amp, y1Per, x2Amp, x2Per, y2Amp, y2Per, rotatePer,
                                    ampDecay, stopSize, x1Init, y1Init, x2Init, y2Init, minMotorStepInc, stepLimit)

    done = False
    while not done:
        done = myCplxHgraph.poke()
        listen()
        if returnToMain: done = True

    hMotor.turn_off()
    vMotor.turn_off()


#Function to run random harmonoraphs until told to stop
def random_hgraph(hMotor, vMotor, inputDict):  #NOTE: input dict is empty for this function

    global returnToMain
    returnToMain = False
    oldDesign = 1000

    while not returnToMain:

        inputList = [[0, {'hPos':0, 'vPos':0, 'hRatio':3, 'vRatio':2, 'hAmp':8000, 'vAmp':3000, 'stopPer':50}],
                     [0, {'hPos':5000, 'vPos':700, 'hRatio':1, 'vRatio':1.03, 'hAmp':6000, 'vAmp':5000, 'stopPer':35}],
                     [0, {'hPos':8500, 'vPos':4250, 'hRatio':2, 'vRatio':1.008, 'hAmp':8500, 'vAmp':4250, 'stopPer':40}],
                     [0, {'hPos':8500, 'vPos':1545, 'hRatio':3, 'vRatio':2, 'hAmp':8500, 'vAmp':5000, 'stopPer':50}],
                     [0, {'hPos':0, 'vPos':0, 'hRatio':2, 'vRatio':1, 'hAmp':7000, 'vAmp':3000, 'stopPer':50}],
                     [0, {'hPos':0, 'vPos':0, 'hRatio':3, 'vRatio':2, 'hAmp':7000, 'vAmp':5000, 'stopPer':50}],
                     [1, {'x1Amp':5000, 'x1Per':800, 'y1Amp':0, 'y1Per':200, 'x2Amp':0, 'x2Per':800, 'y2Amp':0, 'y2Per':400, 'rotatePer':500, 'ampDecay':1, 'stopSize':0.5, 'x1Init':0, 'x2Init':0, 'y1Init':0, 'y2Init':0, 'stepLimit':8000}],
                     [1, {'x1Amp':3000, 'x1Per':900, 'y1Amp':3000, 'y1Per':903, 'x2Amp':3000, 'x2Per':600, 'y2Amp':3000, 'y2Per':600, 'rotatePer':0, 'ampDecay':0.8, 'stopSize':0.7, 'x1Init':3000, 'x2Init':2160, 'y1Init':0, 'y2Init':0}],
                     [1, {'x1Amp':3000, 'x1Per':800, 'y1Amp':3000, 'y1Per':800, 'x2Amp':3000, 'x2Per':404, 'y2Amp':3000, 'y2Per':404, 'rotatePer':0, 'ampDecay':0.8, 'stopSize':0.5, 'x1Init':1500, 'x2Init':1500, 'y1Init':0, 'y2Init':0}],
                     [1, {'x1Amp':3000, 'x1Per':800, 'y1Amp':3000, 'y1Per':800, 'x2Amp':3000, 'x2Per':804, 'y2Amp':3000, 'y2Per':804, 'rotatePer':0, 'ampDecay':0.8, 'stopSize':0.5, 'x1Init':3000, 'x2Init':-3000, 'y1Init':0, 'y2Init':0}],
                     [1, {'x1Amp':3000, 'x1Per':800, 'y1Amp':3000, 'y1Per':800, 'x2Amp':3000, 'x2Per':404, 'y2Amp':3000, 'y2Per':404, 'rotatePer':0, 'ampDecay':0.8, 'stopSize':0.7, 'x1Init':3000, 'x2Init':-2354, 'y1Init':0, 'y2Init':0}]]

        #Select a design
        design = randint(0, len(inputList)-1)
        while design == oldDesign:  #Don't do the same design twice in a row
            design = randint(0, len(inputList)-1)
        oldDesign = design

        if inputList[design][0] == 0:  #This is a simple harmonograph
            run_harmonograph(hMotor, vMotor, inputList[design][1])
        else:  #This is a complex harmonograph
            run_cplx_hgraph(hMotor, vMotor, inputList[design][1])

        #Wait for [15] minutes 
        elapsed = 0
        startTime = time()
        while elapsed < 15*60:  #Number of minutes times 60 seconds per minute
            #listen for stop command
            elapsed = time() - startTime
            listen() #This sets global returnToMain = True if receives a STOP command
            if returnToMain:
                break


#Function to run random harmonoraphs until told to stop
def random_image(hMotor, vMotor, inputDict):  #NOTE: input dict is empty for this function

    global returnToMain
    returnToMain = False
    oldDesign = 1000

    while not returnToMain:

        inputList = listdir("/home/pi/EAS/shade_image/Images/")

        #Select a design
        design = randint(0, len(inputList)-1)
        while design == oldDesign:  #Don't do the same design twice in a row
            design = randint(0, len(inputList)-1)
        oldDesign = design

        fileName = inputList[design]
        fileDict = {'fileName': fileName}

        draw_image(hMotor, vMotor, fileDict)

        print("After draw_image, returnToMain is", returnToMain)

        #Wait for [30] minutes 
        elapsed = 0
        startTime = time()
        while elapsed < 30*60:  #Number of minutes times 60 seconds per minute
            #listen for stop command
            elapsed = time() - startTime
            listen() #This sets global returnToMain = True if receives a STOP command
            if returnToMain:
                break

        print("Out of the timer") 

    print("Ending the random_image routine")


#This is the fiunction to draw an image
def draw_image(hMotor, vMotor, inputDict):

    global returnToMain
    returnToMain = False

    #Create stepper motors that use the basi_stepper library for drawing images
    xMotor = bs.stepper(6, 19, 13, 26, _name='horiz', _backlash=hBacklash)
    yMotor = bs.stepper(4, 27, 17, 22, _name='vert', _backlash=vBacklash)
    xMotor.set_motorStepInc(minMotorStepInc)
    yMotor.set_motorStepInc(minMotorStepInc)

    fileName = inputDict['fileName']

    #Open the file and convert it to black and white
    directory = "/home/pi/EAS/shade_image/Images/"
    im_bw = Image.open(directory + fileName)
    im_bw = im_bw.convert('1', dither=Image.NONE)

    #Resize the image to be no more than the max size the EAS can handle
    im_bw = si.resize(im_bw, si.maxY, si.maxX)

    #Convert the image to a numpy array
    im_bw = np_asarray(im_bw, np_uint8)*255

    #Find  an unshaded region
    (yStart, xStart) = si.get_start(im_bw)
#    print("Start at", yStart, xStart)

    #Shade the first pixel in the image and drawing since this is where the cur$
    im_bw[yStart][xStart] = 100  #First point already shaded since cursor is th$

    #Reset the current position on the motors to match the image coordinate settings
    #(0, 0) for hgraphs is center; (0, 0) for images is top left
    vAdjust = int(im_bw.shape[0]/2)
    hAdjust = int(im_bw.shape[1]/2)
#    print("hAdjust:", hAdjust, "vAdjust:", vAdjust)
    yMotor.set_currPos(vMotor.get_currPos()+vAdjust*si.pixelSizeY)
    xMotor.set_currPos(hMotor.get_currPos()+hAdjust*si.pixelSizeX)
#    print("hCurr:", hMotor.get_currPos)
#    print("vCurr:", vMotor.get_currPos)

    #Move to the starting point for the drawing and erase the EAS
    yMotor.go_to(yStart*si.pixelSizeY)
    xMotor.go_to(xStart*si.pixelSizeX)
    eMotor.set_motorStepInc(10000)
    eMotor.set_clockwise(False)
    eraser.erase(eMotor, eraseSpeed, 1024, 7.5, numShakes, 0.4)
    eMotor.turn_off()

    #Call the function to create the drawing
    returnToMain = si.draw_shaded_image(xMotor, yMotor, yStart, xStart, im_bw, s)

    #Reset the origin to original location (center)
    vMotor.set_currPos(yMotor.get_currPos()-vAdjust*si.pixelSizeY)
    hMotor.set_currPos(xMotor.get_currPos()-hAdjust*si.pixelSizeX)

    #Turn off motors
    clean_up()


#Main program starts here

#Initialize socket variables
host = 'localhost' 
port = 50000
backlog = 5 
size = 1024

#Create the socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((host,port)) 
s.listen(backlog)

#Define the motors to be used
hMotor = sc.stepper(6, 19, 13, 26, _name='horiz', _backlash=hBacklash)
vMotor = sc.stepper(4, 27, 17, 22, _name='vert', _backlash=vBacklash)
eMotor = sc.stepper(12, 20, 16, 21, _name='erase', _backlash=0)

#Move each drawing motor to work out the backlash
hMotor.go_to(400)
hMotor.go_to(0)
vMotor.go_to(400)
vMotor.go_to(0)

hMotor.turn_off()
vMotor.turn_off()

#Create the simple user interface
keepRunning = True

while keepRunning:
    #Listen on the socket server
    functionName, funcInputs = listen()
    if functionName != None:
        func_to_call = getattr(modules[__name__], functionName)
        func_to_call(hMotor, vMotor, funcInputs)



