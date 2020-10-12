import os, re
import fnmatch
import pathlib
import xlrd
from paramiko import SSHClient, AuthenticationException, SSHException, AutoAddPolicy


def parse_row(item):
    ''' '''
    ''' delete unused element '''
    for element in sorted([1, 2, 3 , 4, 5, 8, 9, 10, 13, 14, 15, 16], reverse = True):
        del item[element]

    ''' format output elements '''
    sn = item[0]
    typeif = item[1]
    ipaddr = re.findall(r'(?<=ip_)(?:[0-9]{1,3}\.){3}[0-9]{1,3}|(?<=IP_)(?:[0-9]{1,3}\.){3}[0-9]{1,3}', item[2])
    if not ipaddr:
#        ipaddr = '--//--'
        ipaddr = ipaddr
    switchname = item[3]
    port = item[4]
    taskelement = (''.join(ipaddr) + ',' + sn + ',' + typeif + ',' + switchname + ',' + port).split(',')
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


def main():
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
    taskelement = []

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
                tasknumb = re.findall(r'T\d{8}', files)
                fileout = os.path.join(doutput, ''.join(taskdate)) + '_' + ' '.join(tasknumb) + '.out'

                ''' open xlsx file '''
                wb = xlrd.open_workbook(os.path.join(dinput, files))
                sheet = wb.sheet_by_index(0)
                sheet.cell_value(0, 0)

                ''' read rows from sheet '''
                for i in range(sheet.nrows):
                    item = sheet.row_values(i, 0)
                    if re.match(r'\w+', item[0]) and re.match(r'Data\w*', item[6]):
                        ''' call the data parsing function '''
                        taskelement.append(parse_row(item))

                ''' sorting elements '''
                taskelement.sort(key=lambda x: (x[1]), reverse=False)

                ''' get connection '''
#                conn = connect(host, user, password)

                ''' running cmd on servers '''
#                cmdout = run_cmd(conn, cmd_list)

                ''' write elements to file'''
                write_file(fileout, taskelement)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    ''' call basic function '''
    main()