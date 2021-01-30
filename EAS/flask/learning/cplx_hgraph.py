from flask import Flask, request, redirect, url_for
import socket

@app.route("/complex_harmonograph_page", methods=["GET", "POST"])
def complex_harmonogrpah_page():
    headers = {'Content-Type': 'text/html'}
    errors=""

    #This is the code if the method is POST
#    if request.method == "POST":

    #Check to see if a preset was selected


    #This is the code when the method is GET
    return  '''
        <html>
            <body>
                {errors}
                <p>Choose a preset harmonograph figure:</p>
                <form  method="post" action="{p_url}">
                    <input type="radio" name="preset" value="fish"> Fish<br>
                    <input type="radio" name="preset" value="pretzel"> Pretzel<br>
                    <input type="radio" name="preset" value="rosetta"> Rosetta<br>
                    <input type="radio" name="preset" value="two"> Two<br>
                    <input type="radio" name="preset" value="three"> Three<br>
                    <p><input type="submit" value="Draw Preset" /></p>
                </form>
                <p>OR set parameters for your own custom harmonograph:
                <form method="post" action="{c_url}">
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
    '''.format(errors=errors, p_url=url_for("preset_complex_harmonograph_page"), c_url=url_for("complex_harmonograph_page"))


@app.route("/custom_complex_harmongraph", methods=["GET", "POST"])
def cplx_harmongraph():


    output = "run_cplx_hgraph, {"  #This is the function name to send, and start of dictionary
    if preset == "flower":
      output += "'x1Amp': , 'x1Per': , 'y1Amp': , 'y1Per': ,'x2Amp': , 'x2Per': , 'y2Amp': ," + \
                "'y2Per': , 'rotatePer': , 'ampDecay': , 'stopSize':, 'x1Init': , 'y1Init': ," + \
                "'x2Init': , 'y2Init':, 'minStepInc':} "

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
