from flask import Flask, request, redirect, url_for
import socket
import time

app = Flask(__name__)

count = 0

@app.route("/", methods=["GET", "POST"])
def harmonograph_page():

    headers = {'Content-Type': 'text/html'}

    if request.method == "POST":

        #First I do error checking on the data

        #If the data is good, I send the code
        #Here I would have the code to send the form data via a socket client

        #Here is the page that woujld be displayed
        return '''
            <html>
                <body>
                    <p>harmonograph POST</p>
                    <p>This is where I would show the data being drawn</p>
                    <p>and display a STOP button.  The button click would redirect to the stop_page</p>
                    <p>using a GET method.</p>
                </body>
            </html>
        '''

        #Then, I would have another IF statement where if data is good, the STOP button is shown
        #If the data is bad, the START button is shown again

    #This is where the GET method code is written
    return '''
        <html>
            <body>
                <p>index GET</p>
                <p>This is where I would show the inout page to get data and a START button.</p>
                <p>The button click would take me to this page using a POST method.
            </body>
        </html>
    '''



@app.route("/stop_page", methods=["GET"])
def next():
    headers = {'Content-Type': 'text/html'}

    #Here I would send the STOP message via a socket client and
    #then redirect to the harmongraph_page with a GET method

   #This is where I would be sending data to the server, for example "STOP"
    return redirect(url_for("harmonograph_page"), code=303)




