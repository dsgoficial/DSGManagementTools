#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import os
import psycopg2
# Import modules for CGI handling 
import cgi, cgitb
cgitb.enable()

separador = '_to_'

def message(msg):
    # HTML return
    print "Content-type:text/plain"
    print
    print msg

def checkSync(line):
    split =  line.split(' ')
    cluster = split[2]
    dbname = str(split[3].split('=')[1]).strip()
    dbuser = str(split[4].split('=')[1]).strip()
    dbhost = str(split[5].split('=')[1]).strip()
    dbport = str(split[6].split('=')[1]).strip()
    dbpass = str(split[7].split('=')[1]).strip()

    try:
        conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpass, port=dbport, host=dbhost)
    except psycopg2.Error as e:
        msg = 'Erro durante a conexão com a máquina (IP:%s | Banco:%s | Cluster: %s).\n Descrição: %s' % (dbhost, dbname, cluster, e.pgerror)
        message(msg)
        return False, None, None
    
    cur = conn.cursor()
    sql = 'SELECT ev_seqno, to_char(ev_timestamp, \'YYYY-MM-DD  HH24:MI:SS\') FROM _'+cluster+'.sl_event WHERE ev_type = \'SYNC\' ORDER BY ev_seqno DESC LIMIT 1'
    cur.execute(sql)
    rows = cur.fetchall()
    ev_seqno = None
    ev_timestamp = None
    for row in rows:
        ev_seqno = str(row[0])
        ev_timestamp = str(row[1])
        
    cur.close()
    conn.close()
    
    return True, ev_seqno, ev_timestamp

def runCall(cmd):
    subprocess.call(cmd, shell=True)    
    
def getRunningDaemons():
    listdaemons = 'ps -aux |grep -E \'/usr/bin/slon.*'+separador+'\'|grep -v grep | awk \'{print \"\"$8\" \"$11\" \"$12\" \"$13\" \"$14\" \"$15\" \"$16\" \"$17\"\"}\' > running_daemons.log'
    runCall(listdaemons)
    
    daemons = open('running_daemons.log', 'r')
    lines = daemons.readlines()
    daemons.close()
    return lines

def makeResponse(lines):
    if len(lines) == 0:
        return 'Nada sendo replicado'
    
    response = ''
    current_cluster = ''
    for i in range(len(lines)):
        line = lines[i]
        clustername = line.split(' ')[2]
        
        if current_cluster == clustername:
            continue
        
        split = clustername.split(separador)
        de = split[0]
        para = split[1]
        response += 'Replicando de '+de+' para '+para
        
        success, ev_seqno, ev_timestamp = checkSync(line)
        if not success:
            return
        if ev_seqno and ev_timestamp:
            response += ' (Último Sincronismo em: '+ev_timestamp+')'
        else:
            response += ' (Cópia em andamento...)'
        
        if i != len(lines)-1:
            response += '*'
            
        current_cluster = clustername
    return response

response = makeResponse(getRunningDaemons())

# HTML return
print "Content-type:text/plain"
print 
print response