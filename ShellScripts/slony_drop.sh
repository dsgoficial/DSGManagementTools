#!/bin/sh
MASTERDBNAME=slonymaster
SLAVEDBNAME=slonyslave
MASTERHOST=localhost
SLAVEHOST=localhost
REPLICATIONUSER=postgres
CLUSTERNAME=first_cluster
slonik<<_EOF_
cluster name = $CLUSTERNAME;
node 1 admin conninfo = 'dbname=$MASTERDBNAME host=$MASTERHOST user=$REPLICATIONUSER';
node 2 admin conninfo = 'dbname=$SLAVEDBNAME host=$SLAVEHOST user=$REPLICATIONUSER';
drop set (id=2, origin=1);
_EOF_