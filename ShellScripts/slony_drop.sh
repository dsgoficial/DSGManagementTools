#!/bin/sh
MASTERDBNAME=lcmaster
SLAVEDBNAME=lcslave
MASTERHOST=localhost
SLAVEHOST=10.67.198.233
MASTERUSER=postgres
MASTERPASS=postgres
SLAVEUSER=postgres
SLAVEPASS=postgres
CLUSTERNAME=lc_cluster
slonik<<_EOF_
cluster name = $CLUSTERNAME;
node 1 admin conninfo = 'dbname=$MASTERDBNAME host=$MASTERHOST user=$MASTERUSER password=$MASTERPAS';
node 2 admin conninfo = 'dbname=$SLAVEDBNAME host=$SLAVEHOST user=$SLAVEUSER password=$SLAVEPASS';
drop set (id=2, origin=1);
_EOF_