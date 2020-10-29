DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS devicelist;

CREATE TABLE IF NOT EXISTS task(
    task_name TEXT NOT NULL,
    ipaddr TEXT NOT NULL,
    serial TEXT NOT NULL,
    iftype TEXT NOT NULL,
    switchname TEXT NOT NULL,
    port TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS devicelist(
    ipaddr TEXT NOT NULL,
    serial TEXT NOT NULL,
    dev_name TEXT NOT NULL,
    dev_state TEXT NOT NULL,
    dev_addr TEXT NOT NULL,
    dev_mac TEXT NOT NULL,
    dev_speed TEXT NOT NULL,
    bond TEXT NOT NULL,
    bond_state TEXT NOT NULL,
    bond_mac TEXT NOT NULL,
    bond_speed TEXT NOT NULL,
    bond_ip TEXT NOT NULL,
    bond_gate TEXT NOT NULL,
    check_status TEXT
)