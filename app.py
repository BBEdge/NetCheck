#!/usr/bin/env python
import os

from flask import Flask, render_template, request, redirect, url_for

import initdb
import parsing
import checkcomm

UPLOAD_FOLDER = 'upload'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)


@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename))

    uploaded_dir = app.config['UPLOAD_FOLDER']
    uploaded_file = uploaded_file.filename

    #print(os.path.join(uploaded_dir, uploaded_file))
    ''' call the database init function '''
    dbconn = initdb.init_db()

    ''' call the excel data parsing function '''
    taskdate, taskname = parsing.parsing_task(dbconn, uploaded_dir)

    ''' call the check communication function '''
    checkcomm.check_comm(dbconn)

    os.remove(os.path.join(uploaded_dir, uploaded_file))

    return redirect(url_for('index'))


if __name__ == '__main__':
    # http://192.168.1.36:8080/
    app.run(debug=True, host="0.0.0.0", port=8080)