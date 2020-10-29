SELECT t.ipaddr, d.serial, d.dev, d.dev_state, d.dev_name, d.dev_mac, d.dev_speed, d.bond, d.bond_state, d.bond_mac, d.bond_speed, d.bond_ip, t.switchname, t.port, t.iftype
FROM task t, devicelist d
WHERE d.bond = 'bond0'
AND t.iftype = 'Data'
AND t.ipaddr = d.ipaddr
UNION
SELECT t.ipaddr, d.serial, d.dev, d.dev_state, d.dev_name, d.dev_mac, d.dev_speed, d.bond, d.bond_state, d.bond_mac, d.bond_speed, d.bond_ip, t.switchname, t.port, t.iftype
FROM task t, devicelist d
WHERE d.bond = 'bond1'
AND t.iftype = 'Data Res'
AND t.ipaddr = d.ipaddr