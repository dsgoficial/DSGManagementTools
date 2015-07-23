#!/bin/sh
MASTERDBNAME=[masterdbname]
SLAVEDBNAME=[slavedbname]
MASTERHOST=[masterhost]
SLAVEHOST=[slavehost]
MASTERUSER=[masteruser]
MASTERPASS=[masterpass]
SLAVEUSER=[slaveuser]
SLAVEPASS=[slavepass]
CLUSTERNAME=[clustername]
slonik<<_EOF_
cluster name = $CLUSTERNAME;
node 1 admin conninfo = 'dbname=$MASTERDBNAME host=$MASTERHOST user=$MASTERUSER password=$MASTERPAS';
node 2 admin conninfo = 'dbname=$SLAVEDBNAME host=$SLAVEHOST user=$SLAVEUSER password=$SLAVEPASS';
drop set (id=2, origin=1);
_EOF_