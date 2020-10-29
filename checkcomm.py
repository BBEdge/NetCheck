import os, sqlite3

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

            devicelist.append(words)


    with dbconn:
        try:
            cursor = dbconn.cursor()
            for ele in devicelist:
                cursor.execute("insert into devicelist (ipaddr, serial, dev_name, dev_state, dev_addr, dev_mac, "
                               "dev_speed, bond, bond_state, bond_mac, bond_speed, bond_ip, bond_gate) "
                               "values (?,?,?,?,?,?,?,?,?,?,?,?,?)", ele)
        except sqlite3.Error as error:
                print('ERROR: ' + str(error))


if __name__ == '__main__':
    DATABASE = 'test.db'
    dbconn = sqlite3.connect(DATABASE)
    check_comm(dbconn)