import os
from flask import Flask, request, redirect, url_for, render_template
import socket
from os import listdir


app = Flask(__name__)
errors = ""


#######Main index page where user selects overall mode for EAS######
@app.route("/", methods=["GET", "POST"])
def index():
    headers = {'Content-Type': 'text/html'}

    return  '''
        <html>
            <body>
                <p>Choose the mode you want to run:</p><p>&nbsp</p>
                <form method =  "get" action="{}">
                    <p><input type="submit" value="Simple Harmonograph" /> This will create simple harmonograph figures based on two periodic oscillators</p>
                    <p>&nbsp </p>
                </form>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Complex Harmonograph" /> This will simulate complex harmonograph figures based on up to four oscillators
                                                                            and will also allow the 'drawing surface' to rotate.</p>
                    <p>&nbsp</p>
                </form>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Random Harmonographs" /> This will draw random harmonograph designs, simple and complex, from a list of preset designs</p>
                    <p>&nbsp</p>
                </form>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Images" /> Use the Etch-A-Sketch to draw preloaded images.</p>
                    <p>&nbsp</p>
                </form>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Random Images" /> This will draw random images from a directory of saved images</p>
                    <p>&nbsp</p>
                </form>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Random Images and Harmonographs" /> This will draw random images AND harmonographs</p>
                    <p>&nbsp</p>
                </form>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Reset Origin" /> Press this to set the current Etch-A-Sketch position to be (0, 0). Make sure the stylus is centered on the Etch-A-Sketch before pressing. </p>
                    <p>&nbsp</p>
                </form>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Shut Down" /> Press this to power down the Raspberry Pi. </p>
                    <p>&nbsp</p>
                </form>
            </body>
        </html>
    '''.format(url_for("harmonograph_page"), url_for("complex_harmonograph_page"), url_for("random_harmonograph"), url_for("images_page"), url_for("random_images"), url_for("random"), url_for("reset_origin"), url_for("shut_down_pi"))


######Simple harmonograph page where user selects a preset or custom values######
####################This code also validates data entered########################

@app.route("/harmonograph", methods=["GET", "POST"])
def harmonograph_page():
    global errors
    headers = {'Content-Type': 'text/html'}

    #This is the code if the method is POST
    if request.method == "POST":
        goodData = True
        errors=""  #No errors because just a reset of parameters from a preset radio button

        #Check to see if running a preset - POST means have selected a preset
        preset = None
        try:
            preset = request.form["preset"]
        except:
            preset = None

        print("Preset is", preset)
        print(preset == "fish")

        if preset == "fish":
            hStart=0; vStart=0; hRatio=3; vRatio=2; width=8000; height=3000; stopPer=50
        elif preset == "evil eye":
            hStart=5000; vStart=700; hRatio=1; vRatio=1.03; width=6000; height=5000; stopPer=35
        elif preset == "wings":
            hStart=8500; vStart=-4250; hRatio=2; vRatio=1.008; width=8500; height=4250; stopPer=40
        elif preset == "fish two":
            hStart=8500; vStart=1545; hRatio=3; vRatio=2; width=8500; height=5000; stopPer=50
        elif preset == "infinity":
            hStart=0; vStart=0; hRatio=2; vRatio=1; width=7000; height=3000; stopPer=50
        elif preset == "pretzel":
            hStart=0; vStart=0; hRatio=3; vRatio=2; width=7000; height=5000; stopPer=50

    else: #This is the code when the method is GET - use default values
        hStart=0; vStart=0; hRatio=3; vRatio=2; width=8000; height=5000; stopPer=50

    print("height = ", height)
    #This is the page that is shown regardless of whether the method is GET or POST
    return  '''
        <html>
            <body>
                {errors}
                <p>Choose a preset harmonograph figure:</p>
                <form  method="post" action="{h_url}">
                    <input onchange='this.form.submit();' type="radio" name="preset" value="fish"> Fish <br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="evil eye"> Evil Eye<br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="wings"> Wings<br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="fish two"> Fish Two<br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="infinity"> Infinity<br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="pretzel"> Pretzel<br>
                </form>
                <p>OR set your own parameters for your own custom harmonograph:
                <form method="post" action="{g_url}">
                    <p>Vertical Amplitude <input name="height" size="4" maxlength="4" value="{_height}" /> Max value is 6500; integer only</p>
                    <p>Horizontal Amplitude <input name="width" size="4" maxlength="4" value="{_width}" /> Max value is 9500; integer only</p>
                    <p>Vertical Start <input name="vStart" size="4" maxlength="4" value="{_vStart}" /> Between -Vertical Amplitude and +Vertical Amplitude
                    <p>Horizontal Start <input name="hStart" size="4" maxlength="4" value="{_hStart}" /> Between -Horizontal Amplitude and +Horizontal Amplitude
                    <p>Ratio of periods - vertical : horizontal <input name="vRatio" size="4" maxlength="6" value="{_vRatio}" /> : <input name="hRatio" size="4" maxlength="6" value="{_hRatio}" /> Decimals okay</p>
                    <p>Stop when drawing has decayed to <input name="stopPer" size="1" maxlength="2" value="{_stopPer}" />% of original size</p>
                    <input type="submit" value="Draw!" /></p>
                </form>
            </body>
        </html>
    '''.format(errors=errors, h_url=url_for("harmonograph_page"), g_url=url_for("run_harmonograph"), _height=height, _width=width, _vStart=vStart, _hStart=hStart,
              _vRatio=vRatio, _hRatio=hRatio, _stopPer=stopPer)



@app.route("/run_harmonograph", methods=["POST"])
def run_harmonograph():
    '''This code will validate the data entered. If it is good, it will run the harmonograph.
       If it is not valid, it wil return the user to the data input page for the harmonograph.
    '''

    global errors
    goodData = True

    #Get the input values and check them

    #Check values for height and width and stop percent
    height = None
    width = None
    stopPer = None
    try:
        height = int(request.form["height"])
    except:
        errors += "<p>{!r} is not an integer.</p>\n".format(request.form["height"])
        goodData = False

    try:
        width = int(request.form["width"])
    except:
        errors += "<p>{!r} is not an integer.</p>\n".format(request.form["width"])
        goodData = False

    try:
        stopPer = int(request.form["stopPer"])
    except:
        errors += "<p>{!r} is not an integer.</p>\n".format(request.form["stopPer"])
        goodData = False

    if height != None:
        if height > 6500 or height < 0:
            errors += "<p>Height must be between 0 and 6500. {!r} is not.</p>\n".format(request.form["height"])
            goodData = False
    if width != None:
        if width > 9500 or width < 0:
            errors += "<p>Width must be between 0 and 9500. {!r} is not</p>\n".format(request.form["width"])
            goodData = False

    #Check values for starting position
    hStart = None
    vStart = None
    try:
        vStart = int(request.form["vStart"])
    except:
        errors += "<p>{!r} is not an integer.</p>\n".format(request.form["vStart"])
        goodData = False

    try:
        hStart = int(request.form["hStart"])
    except:
        errors += "<p>{!r} is not an integer.</p>\n".format(request.form["hStart"])
        goodData = False

    if vStart != None:
        if vStart > height or vStart < -height:
            errors += "<p>Vertical Start must be between -{!r} and {!r}. {!r} is not.</p>\n".format(request.form["height"], request.form["height"], request.form["hStart"])
            goodData = False
    if hStart != None:
        if hStart > width or hStart < -width:
            errors += "<p>Horizontal Start must be between -{!r} and {!r}. {!r} is not.</p>\n".format(request.form["width"], request.form["width"], request.form["vStart"])
            goodData = False

    #Check the values for the ratio of horizontal and vertical periods
    hRatio = None
    vRatio = None
    try:
        vRatio = float(request.form["vRatio"])
    except:
        errors += "<p>{!r} is not a number.</p>\n".format(request.form["vRatio"])
        goodData = False

    try:
        hRatio = float(request.form["hRatio"])
    except:
        errors += "<p>{!r} is not a number.</p>\n".format(request.form["hRatio"])
        goodData = False


    #Now, if data is good, construct the data string, attach to the server, and send the info
    if goodData:
        output = "run_harmonograph, {"  #This is the function name to send, and start of dictionary
        output += "'hPos':" + str(hStart) + ", 'vPos':" + str(vStart)
        output += ", 'hRatio':" + str(hRatio) + ", 'vRatio':" + str(vRatio)
        output += ", 'hAmp':" + str(width) + ", 'vAmp':" + str(height) 
        output += ", 'stopPer':" + str(stopPer) + "}"

        host = 'localhost'
        port = 50000

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((host,port)) 
        s.send(output.encode())
        s.close() 

        #Now return a page with a stop button on it
        return '''
            <html>
                <body>
                    <p>Vertical Amplitude: {}</p>
                    <p>Horizontal Amplitude: {}</p>
                    <p>Vertical Start: {}</p>
                    <p>Horizontal Start: {}</p>
                    <p>Ratio of Periods (vertical : horiztonal) is {} : {}</p>
                    <p>Will stop automatically when drawing has decayed to {}% of original size.
                    <form method =  "get" action= "{}">
                        <p><input type="submit" value="Stop Drawing" /></p>
                    </form>
                </body>
            </html>
        '''.format(height, width, vStart, hStart, vRatio, hRatio, stopPer,  url_for("stop_page"))


    else: #Data is not good so go back tp the harmonograph_page
        return redirect(url_for('harmonograph_page'))


######Function to run random harmonograph designs from presets
@app.route("/random", methods=["GET"])
def random_harmonograph():
    headers = {'Content-Type': 'text/html'}

    output = "random_hgraph, {'junk':0}"  #This is the function name to send, and an empty dictionary

    host = 'localhost'
    port = 50000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send(output.encode())
    s.close()

    #Now return a page with a stop button on it
    return '''
        <html>
            <body>
                <p>Running random harmonograph designs from a preset list</p>
                <p>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Stop Drawing" /></p>
                </form>
            </body>
        </html>
    '''.format(url_for("stop_page"))


######Stop function that stops drawing and returns to main######
@app.route("/stop", methods=["GET"])
def stop_page():
    headers = {'Content-Type': 'text/html'}

    #Connect to program via socket and send STOP signal
    host = 'localhost'
    port = 50000

    print("In the stopping code.")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send("STOP".encode())
    s.close()

    #Return to the main webpage
    return redirect(url_for('index'))


######Reset origin function that sets the current Etch-A-sketch position (should be centered) to be (0, 0)######
@app.route("/reset_origin", methods=["GET"])
def reset_origin():
    headers = {'Content-Type': 'text/html'}

    #Connect to program via socket and send STOP signal
    host = 'localhost'
    port = 50000

    print("In the reset_origin function")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send("reset_origin, {'junk': 0}".encode())
    s.close()

    #Return to the main webpage
    return redirect(url_for('index'))


######Reset origin function that sets the current Etch-A-sketch position (should be centered) to be (0, 0)######
@app.route("/shut_down_pi", methods=["GET"])
def shut_down_pi():
    from subprocess import call
    call("sudo shutdown -h now", shell=True)

######Complex harmonograph page where user selects presets or custom values######
#################Page also validates data from custom entry######################

@app.route("/complex_harmonograph_page", methods=["GET", "POST"])
def complex_harmonograph_page():
    headers = {'Content-Type': 'text/html'}
    errors=""

    #This is the code if the method is POST
    if request.method == "POST":
        goodData = True

        #Check to see if running a preset - POST means have selected a preset
        preset = None
        try:
            preset = request.form["preset"]
        except:
            preset = None

        if preset == "rosetta":
            x1Amp=5000; x1Per=800; y1Amp=0; y1Per=200; x2Amp=0; x2Per=800; y2Amp=0; y2Per=400; rotatePer=500; ampDecay=1.0; stopSize=50;
            x1Init=0; x2Init=0; y1Init=0; y2Init=0;
        elif preset == "star":
            x1Amp=3000; x1Per=900; y1Amp=3000; y1Per=903; x2Amp=3000; x2Per=600; y2Amp=3000; y2Per=600; rotatePer=0; ampDecay=0.8; stopSize=70; 
            x1Init=3000; x2Init=-2160; y1Init=0; y2Init=0;
        elif preset == "looper":
            x1Amp=3000; x1Per=800; y1Amp=3000; y1Per=800; x2Amp=3000; x2Per=404; y2Amp=3000; y2Per=404; rotatePer=0; ampDecay=0.8; stopSize=50;
            x1Init=1500; x2Init=1500; y1Init=0; y2Init=0;
        elif preset == "toroid":
            x1Amp=3000; x1Per=800; y1Amp=3000; y1Per=800; x2Amp=3000; x2Per=804; y2Amp=3000; y2Per=804; rotatePer=0; ampDecay=0.8; stopSize=50;
            x1Init=3000; x2Init=-3000; y1Init=0; y2Init=0;
        elif preset == "tristar":
            x1Amp=3000; x1Per=800; y1Amp=3000; y1Per=800; x2Amp=3000; x2Per=404; y2Amp=3000; y2Per=404; rotatePer=0; ampDecay=0.8; stopSize=70;
            x1Init=3000; x2Init=-2354; y1Init=0; y2Init=0;


    else: #This is the code when the method is GET - use default values
        x1Amp='7500'; x1Per=800; y1Amp=5000; y1Per=400; x2Amp=0; x2Per=800; y2Amp=0; y2Per=400; rotatePer=500; ampDecay=0.9; stopSize=70;
        x1Init=0; x2Init=0; y1Init=0; y2Init=0;


    return  '''
        <html>
            <body>
                {errors}
                <p>Choose a preset harmonograph figure:</p>
                <form  method="post" action="{h_url}">
                    <input onchange='this.form.submit();' type="radio" name="preset" value="rosetta"> Rosetta<br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="star"> Star<br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="looper"> Looper<br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="toroid"> Toroid<br>
                    <input onchange='this.form.submit();' type="radio" name="preset" value="tristar"> Tri star<br>
                </form>
                <p>OR set your own parameters for your own custom harmonograph:
                <form method="post" action="{g_url}">
                    <p>First Horizontal Oscillator: &nbsp Amplitude <input name="x1Amp" size="4" maxlength="4" value="{_x1Amp}" />  Period <input name="x1Per" size="4" maxlength="4" value="{_x1Per}" />
                       Initial Position <input name="x1Init" size="4" maxlength="4" value="{_x1Init}" /></p>
                    <p>Second Horizontal Oscillator: Amplitude <input name="x2Amp" size="4" maxlength="4" value="{_x2Amp}" />  Period <input name="x2Per" size="4" maxlength="4" value="{_x2Per}" /></p>
                       Initial Position <input name="x2Init" size="4" maxlength="4" value="{_x2Init}" /></p>
                    <p>First Vertical Oscillator: &nbsp Amplitude <input name="y1Amp" size="4" maxlength="4" value="{_y1Amp}" />  Period <input name="y1Per" size="4" maxlength="4" value="{_y1Per}" /></p>
                       Initial Position <input name="y1Init" size="4" maxlength="4" value="{_y1Init}" /></p>
                    <p>Second Vertical Oscillator: Amplitude <input name="y2Amp" size="4" maxlength="4" value="{_y2Amp}" />  Period <input name="y2Per" size="4" maxlength="4" value="{_y2Per}" /></p>
                       Initial Position <input name="y2Init" size="4" maxlength="4" value="{_y2Init}" /></p>
                    <p>Rotational Period <input name="rotatePer" size="4" maxlength="4" value="{_rotatePer}" /> Integer only</p>
                    <p>Decay Rate <input name="ampDecay" size="4" maxlength="4" value="{_ampDecay}" /> Between -Horizontal Amplitude and +Horizontal Amplitude
                    <p>Stop when drawing has decayed to <input name="stopSize" size="1" maxlength="2" value="{_stopSize}" />% of original size</p>
                    <input type="submit" value="Draw!" /></p>
                </form>
            </body>
        </html>
    '''.format(errors=errors, h_url=url_for("complex_harmonograph_page"), g_url=url_for("run_complex_harmonograph"), _x1Amp=x1Amp, _x1Per=x1Per, _x1Init=x1Init, _x2Amp=x2Amp, _x2Per=x2Per, 
              _x2Init=x2Init, _y1Amp=y1Amp, _y1Per=y1Per, _y1Init=y1Init, _y2Amp=y2Amp, _y2Per=y2Per, _y2Init=y2Init, _rotatePer=rotatePer, _ampDecay=ampDecay, _stopSize=stopSize)


@app.route("/run_complex_harmonograph", methods=["GET", "POST"])
def run_complex_harmonograph():
    '''This code will validate the data entered. If it is good, it will run the complex harmonograph.
       If it is not valid, it wil return the user to the data input page for the complex harmonograph.
    '''

    goodData = True

    #Get the input values
    #Check values (saving for later - maybe using a function below)
    x1Amp = int(request.form['x1Amp'])
    x1Per = int(request.form['x1Per'])
    x1Init = int(request.form['x1Init'])
    x2Amp = int(request.form['x2Amp'])
    x2Per = int(request.form['x2Per'])
    x2Init = int(request.form['x2Init'])
    y1Amp = int(request.form['y1Amp'])
    y1Per = int(request.form['y1Per'])
    y1Init = int(request.form['y1Init'])
    y2Amp = int(request.form['y2Amp'])
    y2Per = int(request.form['y2Per'])
    y2Init = int(request.form['y2Init'])
    rotatePer = int(request.form['rotatePer'])
    ampDecay = float(request.form['ampDecay'])
    stopSize = int(request.form['stopSize'])

    #Now, if data is good (either preset or custom), construct the data string, attach to the server, and send the info
    if goodData:
        output = "run_cplx_hgraph, {"  #This is the function name to send, and start of dictionary
        output += "'x1Amp':" + str(x1Amp) + ", 'x1Per':" + str(x1Per) + ", 'y1Amp':" + str(y1Amp) + ", 'y1Per':" + str(y1Per)
        output += ", 'x2Amp':" + str(x2Amp) + ", 'x2Per':" + str(x2Per) + ", 'y2Amp':" + str(y2Amp) + ", 'y2Per':" + str(y2Per)
        output += ", 'rotatePer':" + str(rotatePer) + ", 'ampDecay':" + str(ampDecay) + ", 'stopSize':" + str(stopSize/100.0)
        output += ", 'x1Init':" + str(x1Init) + ", 'x2Init':" + str(x2Init) + ", 'y1Init':" + str(y1Init) 
        output += ", 'y2Init':" + str(y2Init) + "}"
        host = 'localhost'
        port = 50000

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((host,port)) 
        s.send(output.encode())
        s.close() 

        #Now return a page with a stop button on it
        return '''
            <html>
                <body>
                    <p>First Horizontal Oscillator - Amplitude:{}, Period: {}, Initial Position: {} </p>
                    <p>Second Horizontal Oscillator - Amplitude:{}, Period: {}, Initial Position: {} </p>
                    <p>First Vertical Oscillator - Amplitude:{}, Period: {}, Initial Position: {} </p>
                    <p>Second Vertical Oscillator - Amplitude:{}, Period: {}, Initial Position: {} </p>
                    <p>Rotational Period: {}</p>
                    <p>Decay Rate: {}</p>
                    <p>Will stop automatically when drawing has decayed to {}% of original size.
                    <form method =  "get" action= "{h_url}">
                        <p><input type="submit" value="Stop Drawing" /></p>
                     </form>
                </body>
            </html>
        '''.format(x1Amp, x1Per, x1Init, x2Amp, x2Per, x2Init, y1Amp, y1Per, y1Init, y2Amp, y2Per, y2Init, rotatePer, ampDecay, stopSize, h_url=url_for("stop_page"))


##############Images page where user selects preset images to draw###############

@app.route("/images_page", methods=["GET"])
def images_page():
    headers = {'Content-Type': 'text/html'}

    imagePath = "/home/pi/EAS/shade_image/Images/"

    fileList = listdir(imagePath)
    fileWithPath = []
    for fileName in fileList:
        fileWithPath.append("static/Images/" + fileName) #created a soft link from static/Images to EAS/shade_image/Images
#    print (fileList)
#    print (fileWithPath)

    return render_template("images.html", fileWithPath=fileWithPath)


@app.route("/draw_image", methods=["GET", "POST"])
def draw_image():

    data = request.form
    fullName = data['image']
    fileName = fullName[fullName.rfind("/")+1:]
    name = fileName.split(".")[0]
    print("data is", data)
    print("fileName is", fileName)
    output = "draw_image, {'fileName':'" + fileName + "'}"  #Routine to run and inout dictionary

    #Connect to program via socket and send STOP signal
    host = 'localhost'
    port = 50000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((host,port)) 
    s.send(output.encode())
    s.close() 

    #Now return a page with a stop button on it
    return '''
        <html>
            <body>
                <p>Drawing {}</p>
                <p>
                <img src="{}">
                <p>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Stop Drawing" /></p>
                </form>
            </body>
        </html>
    '''.format(name, fullName, url_for("stop_page"))



######Function to draw random images saved in the Images folder
@app.route("/random_images", methods=["GET"])
def random_images():
    headers = {'Content-Type': 'text/html'}

    output = "random_image, {'junk':0}"  #This is the function name to send, and an empty dictionary

    host = 'localhost'
    port = 50000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send(output.encode())
    s.close()

    #Now return a page with a stop button on it
    return '''
        <html>
            <body>
                <p>Drawing random images from a directory of saved images</p>
                <p>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Stop Drawing" /></p>
                </form>
            </body>
        </html>
    '''.format(url_for("stop_page"))


######Function to draw random images AND harmonographsr
@app.route("/random", methods=["GET"])
def random():
    headers = {'Content-Type': 'text/html'}

    output = "random, {'junk':0}"  #This is the function name to send, and an empty dictionary

    host = 'localhost'
    port = 50000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send(output.encode())
    s.close()

    #Now return a page with a stop button on it
    return '''
        <html>
            <body>
                <p>Drawing random images AND harmonographs</p>
                <p>
                <form method =  "get" action= "{}">
                    <p><input type="submit" value="Stop Drawing" /></p>
                </form>
            </body>
        </html>
    '''.format(url_for("stop_page"))


#####################Simple function for checking inputs###########################
def verify(name, dtype, min, max):

    if dtype == 'int':
        valType = 'integer'
        try:
            value = int(dtype)
        except:
            value = None
    else:
        valType = 'number'
        try:
            value = float(dtype)
        except:
            value = None

    if value == None or value < min or value > max:
        return None, name + " must be a number between " + min + " and " + max + "."
    else:
        return value, ""
