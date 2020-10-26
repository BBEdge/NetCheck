#!/usr/bin/env python

import os, re
import sqlite3
import fnmatch
import pathlib
import xlrd
from paramiko import SSHClient, AuthenticationException, SSHException, AutoAddPolicy


def comm_check():
    line = {}
    d1 = []
    count = 0

    commfile = os.path.join(os.path.abspath(os.getcwd()), ''.join('servers_info.txt'))
    with open(os.path.abspath(commfile), 'r') as ftext:
        lines = ftext.readlines()
        for line in lines:
#            d1.append([])
            uline = line.strip()
            words = uline.split()
            del(words[4])
            del(words[12:])
#            print(range(len(words)))

#            if words[0] == '10.112.50.209':
            if words[0] == '10.112.50.202':
                d1.append([])
#                print(count, words)
                for i in range(len(words)):
                    d1[count].append(words[i])

                count += 1

#        print(len(d1))
         #     ens5f0    UP        bond0     UP
#        print(d1[0][2], d1[0][3], d1[0][7], d1[0][8])

        if (d1[0][3] and d1[0][8]):
            if (d1[0][7] and d1[1][7]) and (d1[0][2] != d1[1][2]):
                print(d1[0][7], 'PASS')
                print(d1[1][7], 'PASS')
            else:
                print(d1[0][7], 'FAIL')
                print(d1[1][7], 'FAIL')

            if (d1[2][7] and d1[2][7]) and (d1[2][2] != d1[3][2]):
                print(d1[2][7], 'PASS')
                print(d1[3][7], 'PASS')
            else:
                print(d1[0][7], 'FAIL')
                print(d1[1][7], 'FAIL')
        else:
            print('DOWN')


def parse_row(taskname, item):
    ''' delete unused element '''
    for element in sorted([1, 2, 3, 4, 5, 8, 9, 10, 13, 14, 15, 16], reverse=True):
        del item[element]

    ''' format output elements '''
    sn = item[0]
    typeif = item[1]
    ipaddr = re.findall(r'(?<=ip_)(?:[0-9]{1,3}\.){3}[0-9]{1,3}|(?<=IP_)(?:[0-9]{1,3}\.){3}[0-9]{1,3}', item[2])
    switchname = item[3]
    port = item[4]
    taskelement = (''.join(taskname) + ',' + ' '.join(ipaddr) + ',' + sn + ',' + typeif + ',' + switchname + ',' + port).split(',')

    return taskelement


def connect(host, user, password, ssh_timeout=120):
    """actually connects to a switch.  returns a paramiko connection"""
    try:
        conn = SSHClient()
        conn.set_missing_host_key_policy(AutoAddPolicy())
        conn.connect(host, username=user, password=password, timeout=ssh_timeout)
    except (AuthenticationException, SSHException) as e:
        print(e)

    return conn


def run_cmd(conn, cmd_list):
    cmdout = []
    for cmd in cmd_list:
        stdin, stdout, stderr = conn.exec_command(cmd)
        stdin.close()

        for item in stdout.readlines():
            print(item)
            cmdout.append(item)

    return cmdout


def write_file(fileout, taskelement):
    header = 'ipddr serial iftype switchname port'.split()

    with open(fileout, 'w') as ftext:
        print('{:16s} {:24s} {:12s} {:30s} {:12s}'.format(*header), file=ftext)

        for item in taskelement:
            print('{:16s} {:24s} {:12s} {:30s} {:12s}'.format(*item), file=ftext)


def main(dbconn):
    dbconn = dbconn
    host = 'localhost'
    user = 'root'
    #    pw = getpass.getpass('Switch password for user %s: ' % user)
    password = '25as75ak'
    cmd_list = ['dmidecode -t 1 | grep Serial | awk -F ":" \'{print $2}\' | tr -d " "',
                'cat /proc/net/dev | awk \'{print $1}\' | grep ":" | grep -v -E "bond|lo" | sed "s/://g"']

    ''' preparation of variables '''
    curpath = pathlib.Path(__file__).parent.absolute()
    dinput = os.path.join(curpath, 'in')
    doutput = os.path.join(curpath, 'out')
    task = []

    ''' preparing task files for parsing '''
    try:
        if os.path.isdir(dinput) and fnmatch.filter(os.listdir(dinput), '*.xlsx'):

            ''' create output dir '''
            if not os.path.exists(doutput):
                try:
                    os.mkdir(doutput)
                except Exception as e:
                    print('Unable to create directory %s.' % doutput, e)

            ''' read files '''
            for files in sorted([f for f in os.listdir(dinput) if os.path.isfile(os.path.join(dinput, f))]):
                taskdate = re.findall(r'(\d{1,2}\.\d{1,2}\.\d{4})', files)
                taskname = re.findall(r'T\d{8}', files)
                fileout = os.path.join(doutput, ''.join(taskdate)) + '_' + ' '.join(taskname) + '.out'

                ''' open xlsx file '''
                wb = xlrd.open_workbook(os.path.join(dinput, files))
                sheet = wb.sheet_by_index(0)
                sheet.cell_value(0, 0)

                ''' read rows from sheet '''
                for i in range(sheet.nrows):
                    item = sheet.row_values(i, 0)
                    if re.match(r'\w+', item[0]) and re.match(r'Data\w*', item[6]):
                        ''' call the data parsing function '''
                        task.append(parse_row(taskname, item))

                ''' sorting elements on serial'''
                task.sort(key=lambda x: (x[2]), reverse=False)

                ''' update ipaddr if empty '''
                for item in task:
                    if (item[1] and item[2]):
                        for row in task:
                            if not row[1] and row[2] == item[2]:
                                row[1] = item[1]

                ''' insert task items to database '''
                with dbconn:
                    try:
                        cursor = dbconn.cursor()
                        for ele in task:
                            cursor.execute("insert into task (task_name, ipddr, serial, iftype, switchname, port) "
                                           "values (?, ?, ?, ?, ?, ?)",
                                           (ele[0], ele[1], ele[2], ele[3], ele[4], ele[5]))
                    except (Exception) as error:
                        print('ERROR: ' + str(error))

                    cursor.execute('SELECT * FROM task')
                    results = cursor.fetchall()
                    for row in results:
                        print(row)

                cursor.close()

                ''' get connection '''
                #                conn = connect(host, user, password)

                ''' running cmd on servers '''
                #                cmdout = run_cmd(conn, cmd_list)

                ''' write elements to file'''
#                write_file(fileout, task)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    ''' init database and connection '''

    DATABASE = 'test.db'
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        dbconn = sqlite3.connect(DATABASE)

#    DATABASE = ":memory:"
#    dbconn = sqlite3.connect(DATABASE)

    with open('templates/schema.sql') as f:
        dbconn.executescript(f.read())

    ''' call basic function '''
    main(dbconn)

    dbconn.close()
#    comm_check()
