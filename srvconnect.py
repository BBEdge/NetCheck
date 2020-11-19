import os
import sqlite3
import getpass
import hashlib
import configparser

from paramiko import SSHClient, AuthenticationException, SSHException, AutoAddPolicy

file = 'app.ini'
cmd_list = ['pwd']
config = configparser.ConfigParser()


def parameters(file):
    ''' set parameters '''
    user = input('Please Enter user name for server access: ')
    password = getpass.getpass('Please Enter a password for server access: ').encode('utf-8')
    #password = hashlib.sha256(password).hexdigest()
    password = hashlib.md5(password).hexdigest()

    config.add_section('server')
    config.set('server', 'host', 'localhost')
    config.set('server', 'user', user)
    config.set('server', 'password', password)

    ''' write parameters to file '''
    with open(file, 'w', encoding='utf8') as cf:
        config.write(cf)

    cf.close()


def connect(dbconn, ssh_timeout=10):
    ''' get parameters from file'''
    config.read('app.ini')
    #host = config.get('server', 'host')
    user = config.get('server', 'user')
    password = config.get('server', 'password')

    with dbconn:
        try:
            ipaddr = dbconn.execute('SELECT ipaddr FROM task WHERE iftype = "Data"')
        except sqlite3.Error as error:
            print("ERROR: ", str(error))


    for row in ipaddr:
        host = row[0]
        print(host)
        ''' actually connects to a switch.  returns a paramiko connection '''
        try:
            conn = SSHClient()
            conn.set_missing_host_key_policy(AutoAddPolicy())
            conn.connect(host, username=user, password=password, timeout=ssh_timeout)

        # Obtain session
        #session = client.get_transport().open_session()
        # Forward local agent
        #AgentRequestHandler(session)
        # Commands executed after this point will see the forwarded agent on
        # the remote end.
        #session.exec_command("git clone https://my.git.repository/")

        except (AuthenticationException, SSHException, TimeoutError) as error:
            print('ERROR:   ', error)
            return error

    #return conn


def run_cmd(conn, cmd_list):
    cmdout = []
    for cmd in cmd_list:
        stdin, stdout, stderr = conn.exec_command(cmd)
        stdin.close()

        for item in stdout.readlines():
            print(item)
            cmdout.append(item)

    return cmdout


if __name__ == '__main__':
    ''' create parameters file '''
    if not os.path.exists(file):
        parameters(file)