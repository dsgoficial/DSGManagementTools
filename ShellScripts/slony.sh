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
#--
# define the namespace the replication system uses in our example it is
# slony_example
#--
cluster name = $CLUSTERNAME;
#--
# admin conninfo's are used by slonik to connect to the nodes one for each
# node on each side of the cluster, the syntax is that of PQconnectdb in
# the C-API
# --
node 1 admin conninfo = 'dbname=$MASTERDBNAME host=$MASTERHOST user=$MASTERUSER password=$MASTERPASS';
node 2 admin conninfo = 'dbname=$SLAVEDBNAME host=$SLAVEHOST user=$SLAVEUSER password=$SLAVEPASS';
#--
# init the first node.  This creates the schema
# _$CLUSTERNAME containing all replication system specific database
# objects.
#--
init cluster ( id=1, comment = 'Master Node');
#--
# Slony-I organizes tables into sets.  The smallest unit a node can
# subscribe is a set.  The following commands create one set containing
# all 4 pgbench tables.  The master or origin of the set is node 1.
#--
create set (id=1, origin=1, comment='Replicating cb');
set add table (set id=1, origin=1, id=1, fully qualified name = 'cb.*', comment='Esquema CB');
set add table (set id=1, origin=1, id=1, fully qualified name = 'complexos.*', comment='Esquema Complexos');
set add table (set id=1, origin=1, id=1, fully qualified name = 'public.*', comment='Esquema Public');
#--
# Create the second node (the slave) tell the 2 nodes how to connect to
# each other and how they should listen for events.
#--
store node (id=2, comment = 'Slave node', event node=1);
store path (server = 1, client = 2, conninfo='dbname=$MASTERDBNAME host=$MASTERHOST user=$MASTERUSER password=$MASTERPASS');
store path (server = 2, client = 1, conninfo='dbname=$SLAVEDBNAME host=$SLAVEHOST user=$SLAVEUSER password=$SLAVEPASS');
_EOF_