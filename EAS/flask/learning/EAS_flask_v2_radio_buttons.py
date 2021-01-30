from flask import Flask, request, redirect, url_for
import socket

app = Flask(__name__)
#app.config["DEBUG"] = True


@app.route("/", methods=["GET", "POST"])
def index():
    headers = {'Content-Type': 'text/html'}

    #This is the code if the method is POST
    if request.method == "POST":
        if request.form["mode"] == "hgraph":
            return redirect(url_for("harmonograph_page"))

        else:
            return  '''
                <html>
                    <body>
                        <p>You must select a valid mode</p><p></p>
                        <p>Choose the mode you want to run:</p>
                        <form  method="post" action=".">
                            <input type="radio" name="mode" value="hgraph"> Draw a simple harmongraph figure<br>
                            <input type="radio" name="mode" value="clock"> Convert the Etch-A-Sketch into a clock (not functional yet)<br>
                            <input type="radio" name="mode" value="image"> Draw an image from a file (not functional yet)<br>
                            <p><input type="submit" value="Submit" /></p>
                        </form>
                    </body>
                </html>
            '''



    #This is code if the method is GET
    return  '''
        <html>
            <body>
                <p>Choose the mode you want to run:</p>
                <form  method="post" action=".">
                    <input type="radio" name="mode" value="hgraph"> Draw a simple harmongraph figure<br>
                    <input type="radio" name="mode" value="clock"> Convert the Etch-A-Sketch into a clock (not functional yet)<br>
                    <input type="radio" name="mode" value="image"> Draw an image from a file (not functional yet)<br>
                    <p><input type="submit" value="Submit" /></p>
                </form>
            </body>
        </html>
    '''



@app.route("/harmonograph", methods=["GET", "POST"])
def harmonograph_page():
    headers = {'Content-Type': 'text/html'}
    errors=""

    #This is the code if the method is POST
    if request.method == "POST":
        goodData = True

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


        #If data is good, construct the data string, attach to the server, and send the info
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
            s.send(bytes(output))
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



    #This is the code when the method is GET
    return  '''
        <html>
            <body>
                {errors}
                <p>Choose a preset harmonograph figure (not active yet):</p>
                <form  method="post" action="{h_url}">
                    <input type="radio" name="preset" value="fish"> Fish<br>
                    <input type="radio" name="preset" value="pretzel"> Pretzel<br>
                    <input type="radio" name="preset" value="one"> One<br>
                    <input type="radio" name="preset" value="two"> Two<br>
                    <input type="radio" name="preset" value="three"> Three<br>
                    <p><input type="submit" value="Draw Preset" /></p>
                </form>
                <p>OR set parameters for your own custom harmonograph:
                <form method="post" action="{h_url}">
                    <p>Vertical Amplitude <input name="height" size="4" maxlength="4" value="6500" /> Max value is 6500; integer only</p>
                    <p>Horizontal Amplitude <input name="width" size="4" maxlength="4" value="9500" /> Max value is 9500; integer only</p>
                    <p>Vertical Start <input name="vStart" size="4" maxlength="4" value="0" /> Between -Vertical Amplitude and +Vertical Amplitude
                    <p>Horizontal Start <input name="hStart" size="4" maxlength="4" value="0" /> Between -Horizontal Amplitude and +Horizontal Amplitude
                    <p>Ratio of periods - vertical : horizontal <input name="vRatio" size="4" maxlength="6" /> : <input name="hRatio" size="4" maxlength="6" /> Decimals okay</p>
                    <p>Stop when drawing has decayed to <input name="stopPer" size="1" maxlength="2" value="50" />% of original size</p>
                    <input type="submit" value="Draw Custom" /></p>
                </form>
            </body>
        </html>
    '''.format(errors=errors, h_url=url_for("harmonograph_page"))


@app.route("/stop", methods=["GET"])
def stop_page():
    headers = {'Content-Type': 'text/html'}

    #Connect to program via socket and send STOP signal
    host = 'localhost'
    port = 50000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send(b'STOP')
    s.close()

    #Return to the main webpage
    return redirect(url_for('index'))


