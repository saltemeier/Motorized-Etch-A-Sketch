# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 12:04:10 2020

@author: steve

Prepare image
    Open image file
    Resize image
    Convert to black and white

"""

#import cv2
from PIL import Image
from numpy import ones as np_ones, sqrt as np_sqrt, where as np_where, full as np_full, uint8 as np_uint8, asarray as np_asarray
import select

returnToMain = False
pixelSizeX = 20  #10
pixelSizeY = 20  #10
maxY = 500.0 #270.0 #<=600  This is the vertical size of the rescaled image in pixels
maxX = 750.0 #387.0  #<=1000  This is the horizontal size of the rescaled image in pixels

UP = True
DOWN = False
RIGHT = False
LEFT = True


def listen(s):

    global returnToMain
    size = 1024

    #Listen on the socket server
    ready_to_read, ready_to_write, in_error = \
                   select.select([s], [s], [], 0)
    if len(ready_to_read)>0:
        client, address = s.accept()
        data = client.recv(size)

        #Now process the data received as a string.  Should be a function name $
        data = str(data)
        print("String received:", data)
        if data[:4] == "STOP":
            print("Received STOP command!")
            #Sstop executing
            returnToMain = True

    return


def step_right(hMotor, currPosX):
    #Confirm that position is correct
    if hMotor.get_currPos() != currPosX*pixelSizeX:  #Something is wrong
        print("ERROR: step_right() received an incorrect position value!")
        print("received:", currPosX*pixelSizeX, "expected:", hMotor.get_currPos())
        while True:
            continue

    #Set clockwise and move one step right
    hMotor.set_clockwise(RIGHT)
    while hMotor.poke() != (currPosX+1)*pixelSizeX:
        continue

    return(currPosX+1)


def step_left(hMotor, currPosX):
    #Confirm that position is correct
    if hMotor.get_currPos() != currPosX*pixelSizeX:  #Something is wrong
        print("ERROR: step_left() received an incorrect position value!")
        print("received:", currPosX*pixelSizeX, "expected:", hMotor.get_currPos())
        while True:
            continue

    #Set clockwise and move one step right
    hMotor.set_clockwise(LEFT)
    while hMotor.poke() != (currPosX-1)*pixelSizeX:
        continue

    return(currPosX-1)


def step_up(vMotor, currPosY):
    #Confirm that position is correct
    if vMotor.get_currPos() != currPosY*pixelSizeY:  #Something is wrong
        print("ERROR: step_up() received an incorrect position value!")
        print("received:", currPosY*pixelSizeY, "expected:", vMotor.get_currPos())
        while True:
            continue

    #Set clockwise and move one step right
    vMotor.set_clockwise(UP)
    while vMotor.poke() != (currPosY-1)*pixelSizeY:
        continue

    return(currPosY-1)


def step_down(vMotor, currPosY):
    #Confirm that position is correct
#    print("IN STEP DOWN!!!")
    if vMotor.get_currPos() != currPosY*pixelSizeY:  #Something is wrong
        print("ERROR: step_down() received an incorrect position value!")
        print("received:", currPosY*pixelSizeY, "expected:", vMotor.get_currPos())
        while True:
            continue

    #Set clockwise and move one step right
    vMotor.set_clockwise(DOWN)
    while vMotor.poke() != (currPosY+1)*pixelSizeY:
        continue
#    print("vMotor currPos = ", vMotor.get_currPos())

    return(currPosY+1)


def resize(image, maxHeight, maxWidth):
    print("Original image size:", image.size)
    (width, height) = image.size
    print(maxHeight, height)
    hFactor = maxHeight/height
    print(maxHeight, height, hFactor)
    wFactor = maxWidth/width
    print(maxWidth, width, wFactor)

    factor = min(hFactor, wFactor)
    newHeight = int(factor*height)
    newWidth = int(factor*width)
    newImage = image.resize((newWidth, newHeight))
    print("New image size:", newImage.size)  #Prints width, height, unlike numpy and openCV
    return newImage


def get_start(image):  #Find the first pixel to start the program

    #Find the first colored pixel starting at top left (0, 0)
    (height, width) = image.shape
    found = False
    for i in range(height):
        for j in range(width):
#            print(i,j,image[i][j])
            if image[i][j] == 0:
                yStart = i
                xStart = j
                found = True
                break
        if found: break

    if not found:
        xStart = yStart = -1

    return (yStart, xStart)


def draw_right(image, row, xStart, hMotor, s):  #Draws a line to the right as far as possible

    global returnToMain

    found = False
    xLimit = image.shape[1]
#    print("Moving right max. steps:", (xLimit-1)*10)
    xTemp = xStart
    for i in range(xStart+1, xLimit):
        listen(s)
        if returnToMain:
            return(-1, -1)
        if image[row][i] == 255:  #This is a white pixel
            xStop = i-1
            found = True
            break
        else:
            xTemp = step_right(hMotor, xTemp)
            image[row][i] = 100  #This value indicates it has been colored
    if not found:
        xStop = xLimit-1

    return(row, xStop)


def draw_left(image, row, xStart, hMotor, s):  #Draws a line to the left as far as possible

    global returnToMain

    found = False
    xLimit=0
    xTemp = xStart
    for i in range(xStart-1, xLimit-1, -1):
        listen(s)
        if returnToMain:
            return(-1, -1)
        if image[row][i] == 255:  #This is a white pixel
            xStop = i+1
            found = True
            break
        else:  #Color in the pixel
            xTemp = step_left(hMotor, xTemp)
            image[row][i] = 100  #This value indicates the pixel has been colored
    if not found:
        xStop = xLimit

    return(row, xStop)


def drop_right(image, row, xStart, hMotor, vMotor):  #Searches right for a way to step down one line
    found = False
    xLimit = image.shape[1]-1
    yLimit = image.shape[0]-1
    xTemp = xStart
    for i in range(xStart, xLimit):
        if row == yLimit:
            break
        elif image[row][i] == 255:  #Have hit a white pixel in the current row
            break
        elif image[row+1][i] ==0:  #This is a black pixel
            xStop = i
            found = True
            break


    if not found:
#        print("Drop down right error: stuck on row", row)
        row = -1
        xStop = -1
        return(row, xStop)

    #Move right and then down
    xTemp = xStart
    while xTemp != xStop:
        xTemp = step_right(hMotor, xTemp)

    yTemp = step_down(vMotor, row)

    image[row+1][xStop] = 100  #This value indicates the pixel has been colored
    return(row+1, xStop)


def drop_left(image, row, xStart, hMotor, vMotor):  #Searches in direction for a way to step down one line
    found = False
    xLimit=0
    yLimit = image.shape[0]-1
    for i in range(xStart, xLimit, -1):
        if row == yLimit:
            break
        if image[row][i] == 255:  #Have hit a white pixel in the current row
            break
        elif image[row+1][i] == 0:  #This is a black pixel
            xStop = i
            found = True
            break

    if not found:
#        print("Drop down left error: stuck on row", row)
        row = -1
        xStop = -1
        return(row, xStop)

#    print("In drop left, getting ready to move.")
#    print("Moving to:", row, xStop)
    #Move left and then down
    xTemp = xStart
    while xTemp != xStop:
        xTemp = step_left(hMotor, xTemp)

    yTemp = step_down(vMotor, row)

    image[row+1][xStop] = 100  #This value indicates the pixel has been colored

    return(row+1, xStop)


def shade_current_region(im_bw, yStart, xStart, hMotor, vMotor, s):
    '''This function will shade the current region.
       The function assumes already in the top left portion of the region
    '''

    global returnToMain

    #Keep repeating this until a drop_down function fails
    print("shade_current_region() starting at", yStart, xStart)
    print("returnToMain is", returnToMain)
    while True:
        (yStart, xStart) = draw_right(im_bw, yStart, xStart, hMotor, s)
        if returnToMain:
            return(-1, -1)
#        print("-----------------------------------------") 
#        print("after draw_right, position is", yStart, xStart, vMotor.get_currPos(), hMotor.get_currPos())
        (yTemp, xTemp) = drop_left(im_bw, yStart, xStart, hMotor, vMotor)
        if yTemp == -1:
            break
        else:
            yStart = yTemp
            xStart = xTemp
#        print("after drop left, position is", yStart, xStart, vMotor.get_currPos(), hMotor.get_currPos())
        (yStart, xStart) = draw_right(im_bw, yStart, xStart, hMotor, s)
        if returnToMain:
            return(-1, -1)
#        print("after draw_right, position is", yStart, xStart, vMotor.get_currPos(), hMotor.get_currPos())
        (yStart, xStart) = draw_left(im_bw, yStart, xStart, hMotor, s)
#        print("after draw_left, position is", yStart, xStart, vMotor.get_currPos(), hMotor.get_currPos())
        if returnToMain:
            return(-1, -1)
        (yTemp, xTemp) = drop_right(im_bw, yStart, xStart, hMotor, vMotor)
#        print("temp values are:", yTemp, xTemp)
        if yTemp == -1:
            break
        else:
            xStart = xTemp
            yStart = yTemp
#        print("after drop_right, position is", yStart, xStart, vMotor.get_currPos(), hMotor.get_currPos())
        (yStart, xStart) = draw_left(im_bw, yStart, xStart, hMotor, s)
        if returnToMain:
            return(-1, -1)
#        print("after draw_left, position is", yStart, xStart, vMotor.get_currPos(), hMotor.get_currPos())

    return (yStart, xStart)




def find_unfinished_region(image, currY, currX, targetValue, s):  #Finds a region close to the current position that is not yet colored in
    #Inefficient in that when it gets to an edge, it will keep checking that edge over and over

    global returnToMain

    yLimit, xLimit = image.shape

    #Look for a value of zero while moving in expanding squares from cursor; return the coordinates
    nextXplus = min(xLimit-1, currX+1)  #The upper x value of next area to check
    nextXminus = max(0, currX-1)  #The lower x value of next area to check
    nextYplus = min(yLimit-1, currY+1)  #The upper y value of next area to check
    nextYminus = max(0, currY-1)  #The lower y value of y next area to check

    checkXplus = checkXminus = checkYplus = checkYminus = True

    while (checkXplus or checkXminus or checkYplus or checkYminus):
        listen(s)
        if returnToMain:
            return(-1, -1)
        #Check the columns on other side of range already checked
        for y in range(nextYminus, nextYplus+1): #First value inclusive, second value exclusive
#            print(y, nextXminus, image[y][nextXminus])
#            print(y, nextXplus, image[y][nextXplus])
            if image[y][nextXminus] == targetValue:
                return(y, nextXminus)
            elif image[y][nextXplus] == targetValue:
                return(y, nextXplus)

        #Check the rows above and below the range already checked
        for x in range(nextXminus+1, nextXplus):  #Don't need to check the corners twice
#            print(x, nextYminus, image[nextYminus][x])
#            print(x, nextYplus, image[nextYplus][x])
            if image[nextYminus][x] == targetValue:
                return(nextYminus, x)
            elif image[nextYplus][x] == targetValue:
                return(nextYplus, x)

        #Increment the range to look at
        if nextXplus == xLimit-1: checkXplus = False
        else: nextXplus += 1
        if nextXminus == 0: checkXminus = False
        else: nextXminus -= 1

        if nextYplus == yLimit-1: checkYplus = False
        else: nextYplus += 1
        if nextYminus == 0: checkYminus = False
        else: nextYminus -= 1

    return(-1, -1)


def find_top_left_pixel(image, yVal, xVal):
    '''Given a point in a region, finds the highest pixle, and farthest
       left in that row, in a localized piece of the region.
       Returns the coordinates of that pixel.
    '''

    xLimit = image.shape[1]
#    print("Top left:", yVal, xVal)

    #Move up (smaller y value) rows until cannot move any higher
    canMoveUp = True
    while canMoveUp:
        canMoveUp = False
        while yVal > 0 and image[yVal-1][xVal]  == 0:# or image[xVal, yVal-1] == 100:  #a black pixel
            yVal -= 1
#            print("Moved up to", yVal, ",", xVal)

#        print("Starting left look")
        #Now move left until can move up, if possible
        tempX = xVal
        while tempX > 0 and image[yVal][tempX-1] == 0:# or image[xVal-1][yVal] == 100:
            tempX -= 1
#            print("tempX:", tempX)
            if image[yVal-1][tempX] == 0:# or image[xVal-1][yVal-1] == 100:
                canMoveUp = True
                xVal = tempX
#                print("Moved left to", yVal, ",", xVal)
                break

#        print("Starting right look")
        #If could not move left, try moving right until can move up or as far as possible
        if not canMoveUp and yVal > 0:
            while tempX < xLimit-1 and image[yVal][tempX+1] == 0:# or image[xVal+1][yVal] == 100:
                tempX += 1
#                print("tempX:", tempX)
                if image[yVal-1][tempX] == 0:# or image[xVal+1][yVal-1] == 100:
                    canMoveUp = True
                    xVal = tempX
#                    print("Moved right to", yVal, ",", xVal)
                    break

#    print("Now I am here.")
#    print("xVal:", xVal)
#    print("yVal:", yVal)
#    print(image[xVal-1][yVal])
    #Now move left as far as possible
    while xVal > 0 and image[yVal][xVal-1] == 0:# or image[xVal-1][yVal] == 100:
        xVal -= 1
#        print("Moved to", yVal, ",", xVal)

    return (yVal, xVal)


def create_path_to_point(image, yCurr, xCurr, yDest, xDest, s):
    '''Move to destination without crossing any white spaces
       The algorithm will create new matrix the size of image that has all
       values = 10,000, except the current position will havea a value
       of 0.  Then, every black pixel touching the current position will
       get a value of 1.  Every black pixel touching those pixels will get
       a value of 2, and so on.  Then, the path will be determined by
       starting at the destination and moving to the lowest adjoining value.

       "touching" means sharing an edge, not diagonal.
    '''

    global returnToMain

    if yDest == -1:  #Not looking for a path to a point but just to a connected area
        findConnected = True
    else:
        findConnected = False
    yLimit, xLimit = image.shape
    defaultDist = xLimit*yLimit
    distances = np_ones((yLimit, xLimit))*defaultDist  #Create an array with all values = 100000
    distances[yCurr][xCurr] = 0
    currList = [(yCurr, xCurr, distances[yCurr][xCurr])]
    nextList = []

    atDestination = False
    while not atDestination and currList:  #currList is not empty
        listen(s)
        if returnToMain:
            return([])
        #Keep moving out one step until reach destination
        #or can not move any more steps
        for (y, x, value) in currList:
            #Check all 4 surrounding cells to see if black (0, or 100)
            #If they are, values = currValue + 1, and add to next list
            if y > 0:
                if image[y-1][x] != 255 and distances[y-1][x] == defaultDist:
                    distances[y-1][x] = value+1
                    nextList.append((y-1, x, value+1))
                    if findConnected:
                        if image[y-1][x] == 0:
                            atDestination = True
                            yDest = y-1
                            xDest = x
                    else:
                        if (y-1, x) == (yDest, xDest): atDestination = True
            if y+1 < yLimit:  #Remember, index goes to one value less than the value of shape property
                if image[y+1][x] != 255 and distances[y+1][x] == defaultDist:
                    distances[y+1][x] = value+1
                    nextList.append((y+1, x, value+1))
                    if findConnected:
                        if image[y+1][x] == 0:
                            atDestination = True
                            yDest = y+1
                            xDest = x
                    else:
                        if (y+1, x) == (yDest, xDest): atDestination = True
            if x > 0:
                if image[y][x-1] != 255 and distances[y][x-1] == defaultDist:
                    distances[y][x-1] = value+1
                    nextList.append((y, x-1, value+1))
                    if findConnected:
                        if image[y][x-1] == 0:
                            atDestination = True
                            yDest = y
                            xDest = x-1
                    else:
                        if (y, x-1) == (yDest, xDest): atDestination = True
            if x+1 < xLimit:
                if image[y][x+1] != 255 and distances[y][x+1] == defaultDist:
                    distances[y][x+1] = value+1
                    nextList.append((y, x+1, value+1))
                    if findConnected:
                        if image[y][x+1] == 0:
                            atDestination = True
                            yDest = y
                            xDest = x+1
                    else:
                        if (y, x+1) == (yDest, xDest): atDestination = True

        #Now, set currList = nextList and nextList = []
        currList = nextList
        nextList = []

    if not atDestination:
        if findConnected:
            print("FAILED TO CREATE A PATH FROM", yCurr,",", xCurr, "to a connected, unshaded region")
        else:
            print("FAILED TO CREATE A PATH FROM", yCurr,",", xCurr, "to", yDest,",", xDest)
        return([])

    #Now, create the path and return it.  Start at destination and move
    #backwards to lowest value with preference being horizontal, then vertical
    ##and then diagonal until get to (xCurr, yCurr)
    #temp is current position, next is best next position found so far
    #NOTE: Changed so preference is to keep going in a straight line in order to keep the
    #      paths more on the inside of shaded regions instead of along the edges
    nextX = tempX = xDest
    nextY = tempY = yDest
    nextValue = distances[tempY][tempX]
    pathPoint = (yDest, xDest)
    path = [pathPoint]
    preferHorizontal = True  #True means move horizontally instead of vertically if otherwise indifferent

    while pathPoint != (yCurr, xCurr):  #Have not traced path back to current position
        listen(s)
        if returnToMain:
            return([])
        found = False
        if preferHorizontal:  #Check horizontal first
            #Check adjacent cells to find lowest value
            if tempX > 0: #Can look to the left
                if distances[tempY][tempX-1] < nextValue:
                    nextX = tempX-1
                    nextY = tempY
                    nextValue = distances[nextY][nextX]
                    found = True
                    preferHorizontal = True
            if tempX+1 < xLimit and not found: #Can look to the right
                if distances[tempY][tempX+1] < nextValue:
                    nextX = tempX+1
                    nextY = tempY
                    nextValue = distances[nextY][nextX]
                    found = True
                    preferHorizontal = True
            if tempY+1 < yLimit and not found:
                if distances[tempY+1][tempX] < nextValue:
                    nextX = tempX
                    nextY = tempY+1
                    nextValue = distances[nextY][nextX]
                    found = True
                    preferHorizontal = False
            if tempY > 0 and not found:
                if distances[tempY-1][tempX] < nextValue:
                    nextX = tempX
                    nextY = tempY-1
                    nextValue = distances[nextY][nextX]
                    found = True
                    preferHorizontal = False
        else:  #Prefer vertical
            #Check adjacent cells to find lowest value
            if tempY+1 < yLimit:
                if distances[tempY+1][tempX] < nextValue:
                    nextX = tempX
                    nextY = tempY+1
                    nextValue = distances[nextY][nextX]
                    found = True
                    preferHorizontal = False
            if tempY > 0 and not found:
                if distances[tempY-1][tempX] < nextValue:
                    nextX = tempX
                    nextY = tempY-1
                    nextValue = distances[nextY][nextX]
                    found = True
                    preferHorizontal = False
            if tempX > 0 and not found: #Can look to the left
                if distances[tempY][tempX-1] < nextValue:
                    nextX = tempX-1
                    nextY = tempY
                    nextValue = distances[nextY][nextX]
                    found = True
                    preferHorizontal = True
            if tempX+1 < xLimit and not found: #Can look to the right
                if distances[tempY][tempX+1] < nextValue:
                    nextX = tempX+1
                    nextY = tempY
                    nextValue = distances[nextY][nextX]
                    found = True
                    preferHorizontal = True

        if found:
            tempX = nextX
            tempY = nextY
            pathPoint = (nextY, nextX)
            path.append(pathPoint)
        else: #Did not find a next point
            print("Error: unable to trace path back to current destination")
            print("Stuck at point", tempY, tempX)
            return []

    return path


def follow_path(hMotor, vMotor, path, im_bw, s):
    '''Cause the Etch-A-Sketch to follow the given path
    '''

#    print("path:", path)
    global returnToMain

    #Draw along the path. Last point in the list is the current location
    for index in range(len(path)-2, -1, -1):
        listen(s)
        if returnToMain:
            return
#        print("Moving from point", path[index+1][0], ",", path[index+1][1], "to", path[index][0], ",", path[index][1])
        if path[index][0] - path[index+1][0] == 1:  #Move DOWN one
#            print("Stepping down")
            yTemp = step_down(vMotor, path[index+1][0])
        elif path[index][0] - path[index+1][0] == -1:  #Move UP one
            yTemp = step_up(vMotor, path[index+1][0])
        elif path[index][1] - path[index+1][1] == 1:  #Move RIGHT one
            xTemp = step_right(hMotor, path[index+1][1])
        elif path[index][1] - path[index+1][1] == -1:  #Move LEFT one
            xTemp = step_left(hMotor, path[index+1][1])
        else:  #Error
            print("Error tryring to follow the path!!!!!")

    for point in reversed(path):
        im_bw[point[0]][point[1]] = 100;  #Flag the point as visited


def connect_closest_black_pixel(image, yDest, xDest, s):

    #Find the closest black pixel to the detached region
    #A pixel is a border pixel if it has a white pixel in one of it's four direct neighbors
    #When looking for another boarder pixel next to the current one, always move counterclockwise
    #from a white square.  e.g. if white square is at top of current pixel, check left pixel
    #next, then down if left is not a border, then right if left is not a border
    #NOTE: This is a wek algorithm since you could have a peninsula one pixel think pointing
    #left, and this alogrithm would stop at the end of that peninsula

    global returnToMain
    yLimit, xLimit = image.shape
    currX = xDest
    currY = yDest
    best=(0, 0, 0, 0, 1000000)
    stepIndex = 3  #Initial calue means will check up first at starting point
    done = False
    debug = False
 #   if yDest == 169 and xDest == 100:
 #       debug = True

    if debug:
        print(image[160:175, 90:110 ])

#    print("Starting to look at", yDest, ",", xDest)

    count = 0
    while not done:

        listen(s)
        if returnToMain:
            return(-1, -1)

        #Find the closest already shaded point to a given destination point
        if count%10 == 0:  #Just check every 10th pixel to save time
            closeY, closeX = find_unfinished_region(image, currY, currX, 100, s)  #100 is value of image cells that are already shaded

            distance = np_sqrt((closeX-currX)**2 + (closeY-currY)**2)
            if distance < best[4]:
                best = (currY, currX, closeY, closeX, distance)
#                 print("Best:", best)

        #Find the next border cell to check
        currY, currX, stepIndex = find_next_border_cell(image, currY, currX, stepIndex)

        if debug: print("Checking:", currY, currX )

        if (currY == yDest) and (currX == xDest):  #Back where started from
            done = True

        count += 1

    if debug:
        print("best is", best)

    #When here, done equals true
    #Add a line to the image so these two points are now connected
    if best[4] == 1000000:
        print("find_closest_shaded_pixel routine failed")
        return (-1, -1)
    else:  #Draw a line in the image to connect areas and return True
        stopY = best[0]
        stopX = best[1]
        startY = best[2]
        startX = best[3]
        if stopX == startX:
            slope = 1000000
        else:
            slope = abs(float(stopY-startY)/float(stopX-startX))

        if debug:
            print("Creating a line from", startY, startX, "to", stopY, stopX)
            print("Slope is", slope)

        if stopY < startY: yInc = -1
        else: yInc = 1
        if stopX < startX: xInc = -1
        else: xInc = 1

        if debug:
            print("startY", startY)
            print("yInc", yInc)

        while (startY != stopY) or (startX != stopX):
            if startX == stopX:  #Just move y to it's position
                while startY != stopY:
                    startY += yInc
                    image[startY][startX] = 0  #Color it black
            elif  startY == stopY:  #Just move x to it's position
                while startX != stopX:
                    startX += xInc
                    image[startY][startX] = 0  #color it black
            else:
                while abs((stopY-startY)/(stopX-startX)) >= slope:
                    startY += yInc
                    if debug and yDest-startY < 15:
                        print("startY:", startY)
                        print("Shaded pixel", startY, startX)
                    image[startY][startX] = 0  #Color it black

                while abs((stopY-startY)/(stopX-startX)) < slope:
                    startX += xInc
                    image[startY][startX] = 0  #Color it black
                    if startX == stopX:
                        break

        if debug:
            print(image[160:175, 90:110 ])

        return (stopY, stopX)


def find_next_border_cell(image, yPos, xPos, index):
    #Given a border cell and index, it finds the next border cell moving counterclockwise
    yLimit = image.shape[0]-1
    xLimit = image.shape[1]-1

    #Create increments (y, x) for left, down, right, and up moves
    steps = ((0, -1), (1, 0), (0, 1), (-1, 0))

#    print("In find_next...", yPos, xPos, index)

    #Find the next border cell
    for i in range(4):
        nextY = yPos + steps[index][0]
        nextX = xPos + steps[index][1]
#        print("Checking border:", nextY, nextX, index, image[nextY][nextX])
        if nextY > 0 and nextY < yLimit:
            if nextX > 0 and nextX < xLimit:
                if image[nextY, nextX] == 0:  #0 indicates the pixel is black
                    return(nextY, nextX, (index+3)%4)

        index = (index + 1 ) % 4

    print("Error: no adjoining border cell could be found")
    return (yPos, xPos, index+1)


##########Main program starts here##########

def draw_shaded_image(hMotor, vMotor, yStart, xStart, im_bw, s):

#Returns True if stopped early, False if completed image

    global returnToMain

    #Shade region and find next region
    done = False
    returnToMain = False
    while not done:

        #Find the/a top left pixel in current region
        (yDest, xDest) = find_top_left_pixel(im_bw, yStart, xStart)
        print("Top left pixel is", yDest, xDest)

        if returnToMain:
            return(True)

        #Create a path to the top left pixel
        if yStart != yDest or xStart != xDest:
            path = create_path_to_point(im_bw, yStart, xStart, yDest, xDest, s)
            if len(path) == 0:
                print("Failed to create a path to the top left pixel")
                print(yStart, xStart, "->", yDest, xDest)
                done = True
                break
            else: #Follow path to top left pixel
                print("Created path of length", len(path), "from", yStart, xStart, "->", yDest, xDest)
                follow_path(hMotor, vMotor, path, im_bw, s)
                (yStart, xStart) = path[0]

        if returnToMain:
            return(True)

        #Now shade this region starting at the top left pixel
        print("Shading region starting at", yStart, xStart)
        yStart, xStart = shade_current_region(im_bw, yStart, xStart, hMotor, vMotor, s)
        print("Current position after shading is", yStart, ",", xStart)

        if returnToMain:
            print("Returning 1")
            return(True)

        #Find a path to nearest connected, unshaded region, if possible, or unconeccted, unshaded region otherwise
        path = create_path_to_point(im_bw, yStart, xStart, -1, -1, s)  #The -1 value means not a path to a point but a path to nearest unshaded region
        print("Path of length", len(path), "created to a connected region")
        if returnToMain:
            print("Returning 2")
            return(True)
        if len(path) > 0:
            follow_path(hMotor, vMotor, path, im_bw, s)
            (yStart, xStart) = path[0]

        else:  #Create and follow a path to an unconnected, unshaded region
            (yDest, xDest) = find_unfinished_region(im_bw, yStart, xStart, 0, s)  #Zero is value of black cells not yet shaded
            print("Point in unconeccted, unfinished region is", yDest, ",", xDest)
#        print(im_bw[(yDest-5):(yDest+5), (xDest-5):(xDest+5)])
            if yDest == -1 or returnToMain:  #Could not find either a connected or unconnected, unfinished region
                print("Returning 3")
                if returnToMain:
                    return(True)
                else:  #Simply finished
                    return(False)

            (yDest2, xDest2) = connect_closest_black_pixel(im_bw, yDest, xDest, s) #Create a connection in the image
            if yDest2 == -1 or returnToMain:  #Indicates failure
                print("Failed to connect a range")
                print("Returning 4")
                return(True)
            else:  #Create a path to the point yDest2, xDest2 in the now connected region
                path = create_path_to_point(im_bw, yStart, xStart, yDest2, xDest2, s)
                if len(path) == 0 or returnToMain:
                    print("Failed to create a path to a previously unconnected region")
                    print("Returning 5")
                    return(True)
                else: #Follow path to previously unconnected region
                    follow_path(hMotor, vMotor, path, im_bw, s)
                    (yStart, xStart) = path[0]

        if returnToMain:
            print("Returning 6")
            return(True)

        print("------------------------")
        print("Restarting the Main loop")


    print("Returning 7")
    return(False)
