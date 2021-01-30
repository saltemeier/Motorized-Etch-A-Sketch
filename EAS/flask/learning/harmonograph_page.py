from flask import Flask, request
from aFunction import do_calculation

app = Flask(__name__)
#app.config["DEBUG"] = True

@app.route("/", methods=["GET", "POST"])
def adder_page():
    headers = {'Content-Type': 'text/html'}
    errors=""
    if request.method == "POST":
        goodData = True

        #Check values for height and width
        height = None
        width = None
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
            hRatio = int(request.form["hRatio"])
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["hRatio"])
            goodData = False


        #If data is good, construct the data string, attach to the server, and send the info
        if goodData:
            output = "run_harmonograph, {"  #This is the function name to send, and start of dictionary
            output += "'hPos':" + str(hStart) + ", 'vPos':" + str(vStart)
            output += ",' hRatio':" + str(hRatio) + ", 'vRatio':" + str(vRatio)
            output += ",' hAmp':" + str(width) + ", 'vAmp':" + str(height) + "}"

            host = 'localhost'
            port = 50000

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect((host,port)) 
            s.send(bytes(output))
            s.close() 

            #Now return a page with a stop button on it - this should just be a pointer that points it to a new page with a stop button
            return '''
                <html>
                    <body>
                        <p>The result is  {result}</p>
                        <p><a href="/">Click here to calculate again</a>
                    </body>
                </html>
            '''.format(result=result)

    return  '''
        <html>
            <body>
                {errors}
                <p>Choose a preset harmonograph figure (not active yet):</p>
                <form  method="post" action=".">
                    <input type="radio" name="preset" value="fish"> Fish<br>
                    <input type="radio" name="preset" value="pretzel"> Pretzel<br>
                    <input type="radio" name="preset" value="one"> One<br>
                    <input type="radio" name="preset" value="two"> Two<br>
                    <input type="radio" name="preset" value="three"> Three<br>
                    <p><input type="submit" value="Draw Preset" /></p>
                </form>
                <p>OR set parameters for your own custom harmonograph:
                <form method="post" action=".">
                    <p>Vertical Amplitude <input name="height" size="6" maxlength="4" /> Max value is 6500; integer only</p>
                    <p>Horizontal Amplitude <input name="width" size="6" maxlength="4" /> Max value is 9500; integer only</p>
                    <p>Horizontal Start <input name="hStart" size="6" maxlength="4" /> Between -Horizontal Amplitude and +Horizontal Amplitude
                    <p>Vertical Start <input name="vStart" size="6" maxlength="4" /> Between -Vertical Amplitude and +Vertical Amplitude
                    <p>Ratio of periods - height : width <input name="h_ratio" size="6" maxlength="6" /> : <input name="w_ratio" size="6" maxlength="6" /> Decimals okay</p>
                    <input type="submit" value="Draw Custom" /></p>
                </form>
            </body>
        </html>
    '''.format(errors=errors)

