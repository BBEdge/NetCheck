import os, sqlite3, itertools


def check_comm(dbconn):
    devicelist = []

    with dbconn:
        try:
            task = dbconn.execute('SELECT ipaddr, serial FROM task WHERE iftype = "Data"').fetchall()
        except sqlite3.Error as error:
            print("ERROR: ", str(error))

    commfile = os.path.join(os.path.abspath(os.getcwd()), ''.join('servers_info.txt'))
    with open(os.path.abspath(commfile), 'r') as ftext:
        lines = ftext.readlines()
        for line in lines:
            uline = line.strip()
            words = uline.split()
            del(words[4])
            del(words[13:])

            ''' create list '''
            devicelist.append(words)

    ''' sorting devicelist'''
    #value = set(map(lambda x:x[0], devicelist))
    devicelist.sort(key=lambda x:(x[0]), reverse=False)

    ''' group list by ipaddr '''
    devkey = lambda x: x[0]
    list_grouped = [list(group) for key, group in itertools.groupby(devicelist, devkey)]

    with dbconn:
        try:
            cursor = dbconn.cursor()

            for g in range(len(list_grouped)):
                for l in range(len(list_grouped[g])):
                    if list_grouped[g][l][3] != 'UP' or list_grouped[g][l][8] != 'UP':
                        list_grouped[g][l].append('FAIL')
                    else:
                        list_grouped[g][l].append('PASS')

                    cursor.execute("insert into devicelist (ipaddr, serial, dev, dev_state, dev_addr, dev_mac, "
                                   "dev_speed, bond, bond_state, bond_mac, bond_speed, bond_ip, bond_gw, state) "
                                   "values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", list_grouped[g][l])

        except sqlite3.Error as error:
                print('ERROR: ' + str(error))


if __name__ == '__main__':
    DATABASE = 'test.db'
    dbconn = sqlite3.connect(DATABASE)
    check_comm(dbconn)