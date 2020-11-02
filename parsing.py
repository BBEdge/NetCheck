import os, re
import xlrd
import fnmatch
import sqlite3


def parse_row(taskname, item):
    ''' delete unused elements '''
    for element in sorted([1, 2, 3, 4, 5, 8, 9, 10, 13, 14, 15, 16], reverse=True):
        del item[element]

    ''' format output elements '''
    sn = item[0]
    iftype = item[1]
    ipaddr = re.findall(r'(?<=ip_)(?:[0-9]{1,3}\.){3}[0-9]{1,3}|(?<=IP_)(?:[0-9]{1,3}\.){3}[0-9]{1,3}', item[2])
    switchname = item[3]
    port = item[4]
    taskelement = (''.join(taskname) + ',' + ' '.join(ipaddr) + ',' + sn + ',' + iftype + ',' + switchname + ',' + port).split(',')

    return taskelement


def parsing_task(dbconn, uploaded_dir):
    task = [] # the list with parsed rows

    ''' preparing files for parsing '''
    try:
        if os.path.isdir(uploaded_dir) and fnmatch.filter(os.listdir(uploaded_dir), '*.xlsx'):

            ''' read files '''
            for files in sorted([f for f in os.listdir(uploaded_dir) if os.path.isfile(os.path.join(uploaded_dir, f))]):
                taskdate = re.findall(r'(\d{1,2}\.\d{1,2}\.\d{4})', files)
                taskname = re.findall(r'T\d{8}', files)

                ''' open xlsx file '''
                wb = xlrd.open_workbook(os.path.join(uploaded_dir, files))
                sheet = wb.sheet_by_index(0)
                sheet.cell_value(0, 0)

                ''' read rows from sheet '''
                for i in range(sheet.nrows):
                    item = sheet.row_values(i, 0)
                    if re.match(r'\w+', item[0]) and re.match(r'Data\w*', item[6]):
                        ''' call the row parsing function '''
                        task.append(parse_row(taskname, item))

                ''' sorting elements on serial '''
                task.sort(key=lambda x:(x[2]), reverse=False)

                ''' update ipaddr if empty '''
                for item in task:
                    if (item[1] and item[2]):
                        for row in task:
                            if not row[1] and row[2] == item[2]:
                                row[1] = item[1]

                ''' insert rows to database'''
                with dbconn:
                    try:
                        cursor = dbconn.cursor()
                        for ele in task:
                            cursor.execute("insert into task (task_name, ipaddr, serial, iftype, switchname, port) "
                                           "values (?, ?, ?, ?, ?, ?)",
                                           (ele[0], ele[1], ele[2], ele[3], ele[4], ele[5]))
                    except sqlite3.Error as error:
                        print('ERROR: ' + str(error))

        return taskdate, taskname

    except Exception as error:
        print(error)