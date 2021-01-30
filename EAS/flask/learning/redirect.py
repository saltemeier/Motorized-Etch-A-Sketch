from flask import Flask, request, redirect, url_for
import socket
import time

app = Flask(__name__)

count = 0

#@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET"])
def index():
    global count
    count += 1
    headers = {'Content-Type': 'text/html'}

#    if request.method == "POST":
#        return ' ' '
#            <html>
#                <body>
#                    <p>index POST</p>
#                    <p>count = {!r}
#                </body>
#            </html>
#        ' ' '.format(count)

#        time.sleep(5)
#        return redirect(url_for("next"), code=303)

    return '''
        <html>
            <body>
                <p>index GET</p>
                <form  method="post" action="{}">
                    <p><input name="number1" /></p>
                    <p><input name="number2" /></p>
                    <p><input type="submit" value="Go To Next" /></p>
                </form>
            </body>
        </html>
    '''.format(url_for("next"))


#@app.route("/next", methods=["GET", "POST"])
@app.route("/next", methods=["POST"])
def next():
    headers = {'Content-Type': 'text/html'}

#    if request.method == "POST":
#        return ' ' '
#            <html>
#                <body>
#                    <p>next POST</p>
#                    <p>number 1 is {}
#                </body>
#            </html>
#        ' ' '.format(format(request.form["number1"]))


#NOTHING AFTER RETURN IS LOOKED AT, AND FIRST RETURN IS ABOVE THIS!!!
    time.sleep(5)
    #This is where I would be sending data to the server, for example "STOP"
    return redirect(url_for("index"), code=303)


#    return ' ' '
#        <html>
#            <body>
#                <p>next GET</p>
#                <form  method="post" action=".">
#                    <p><input type="submit" value="Go To Index" /></p>
#                </form>
#            </body>
#        </html>
#    ' ' '



