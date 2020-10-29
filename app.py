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


@app.route('/result', methods=('GET', 'POST'))
def result():
    taskdate = request.args['taskdate']
    taskname = request.args['taskname']
    results = request.args['results']

    return render_template('result.html', taskdate=taskdate, taskname=taskname, results=results)


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
    taskdate = ''.join(taskdate)
    taskname = ''.join(taskname)

    ''' call the check communication function '''
    checkcomm.check_comm(dbconn)

    os.remove(os.path.join(uploaded_dir, uploaded_file))

    results = dbconn.execute('SELECT t.ipaddr, d.serial, d.dev_name, d.dev_state, d.dev_addr, d.dev_mac, d.dev_speed, '
                             'd.bond, d.bond_state, d.bond_mac, d.bond_speed, d.bond_ip, t.switchname, t.port, t.iftype '
                            'FROM task t, devicelist d WHERE d.bond = "bond0" AND t.iftype = "Data" AND t.ipaddr = d.ipaddr UNION '
                            'SELECT t.ipaddr, d.serial, d.dev_name, d.dev_state, d.dev_addr, d.dev_mac, d.dev_speed, '
                             'd.bond, d.bond_state, d.bond_mac, d.bond_speed, d.bond_ip, t.switchname, t.port, t.iftype '
                            'FROM task t, devicelist d WHERE d.bond = "bond1" AND t.iftype = "Data Res" AND t.ipaddr = d.ipaddr').fetchall()

    dbconn.close()
    #return redirect(url_for('index'))
    #return redirect(url_for('result.html', taskdate=taskdate, taskname=taskname, results=results))
    return render_template('result.html', taskdate=taskdate, taskname=taskname, results=results)


if __name__ == '__main__':
    # http://192.168.1.36:8080/
    app.run(debug=True, host="0.0.0.0", port=8080)