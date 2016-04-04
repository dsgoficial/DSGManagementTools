#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os
import time
import psycopg2
# Import modules for CGI handling 
import cgi, cgitb
cgitb.enable()

# Create instance of FieldStorage 
form = cgi.FieldStorage()

# Get data from fields
masterdb = form.getvalue('MASTERDBNAME')
slavedb = form.getvalue('SLAVEDBNAME')
masterhost = form.getvalue('MASTERHOST')
slavehost = form.getvalue('SLAVEHOST')
masterport = form.getvalue('MASTERPORT')
slaveport = form.getvalue('SLAVEPORT')
masteruser = form.getvalue('MASTERUSER')
masterpass = form.getvalue('MASTERPASS')
slaveuser = form.getvalue('SLAVEUSER')
slavepass = form.getvalue('SLAVEPASS')
clustername = form.getvalue('CLUSTERNAME')
dbversion = form.getvalue('DBVERSION')

def updatePostgresUsers():
    sql = '''SELECT rolname, \'CREATE ROLE \' || rolname || \';\',
               \'ALTER ROLE \' || rolname || \' WITH \' ||
               CASE WHEN rolsuper=\'t\' THEN \'SUPERUSER\'
                    WHEN rolsuper=\'f\' THEN \'NOSUPERUSER\'
               END || \' \' ||
               CASE WHEN rolinherit=\'t\' THEN \'INHERIT\'
                    WHEN rolinherit=\'f\' THEN \'NOINHERIT\'
               END || \' \' ||
               CASE WHEN rolcreaterole=\'t\' THEN \'CREATEROLE\'
                    WHEN rolcreaterole=\'f\' THEN \'NOCREATEROLE\'
               END || \' \' ||       
               CASE WHEN rolcreatedb=\'t\' THEN \'CREATEDB\'
                    WHEN rolcreatedb=\'f\' THEN \'NOCREATEDB\'
               END || \' \' ||       
               CASE WHEN rolcanlogin=\'t\' THEN \'LOGIN\'
                    WHEN rolcanlogin=\'f\' THEN \'NOLOGIN\'
               END || \' \' ||       
               CASE WHEN rolreplication=\'t\' THEN \'REPLICATION\'
                    WHEN rolreplication=\'f\' THEN \'NOREPLICATION\'
               END || \' PASSWORD \'\'\' ||
               rolpassword || \'\'\';'        
            FROM pg_authid where rolcanlogin = \'t\' and rolname <> \'postgres\';
        '''
    try:
        conn = psycopg2.connect(database='postgres', user=slaveuser, password=slavepass, port=slaveport, host=slavehost)
    except psycopg2.Error as e:
        msg = 'Erro durante a conexão com a máquina (IP:%s).\n Descrição: %s' % (slavehost, e.pgerror)
        message(msg)
        return False
        
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    users = []
    creates = []
    alters = []
    for row in rows:
        users.append(row[0])
        creates.append(row[1])
        alters.append(row[2])
        
    cur.close()
    conn.close()
        
    try:
        conn = psycopg2.connect(database="postgres", user=masteruser, password=masterpass, port=masterport, host=masterhost)
    except psycopg2.Error as e:
        msg = 'Erro durante a conexão com a máquina (IP:%s).\n Descrição: %s' % (masterhost, e.pgerror)
        message(msg)
        return False
    
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    myusers = []
    for row in rows:
        myusers.append(row[0])
        
    for i in range(len(users)):
        user = users[i]
        if user not in myusers:
            cur.execute(creates[i])
            cur.execute(alters[i])
        else:
            cur.execute(alters[i])
    
    conn.commit()
    cur.close()
    conn.close()
    
    return True    

def updateScript(name, masterdb, slavedb, masterhost, slavehost, masterport, slaveport, masteruser, masterpass, slaveuser, slavepass, cluster):
    script = open(name, 'r')
    scriptData = script.read()
    script.close()

    newData = scriptData.replace('[masterdbname]', masterdb)
    newData = newData.replace('[slavedbname]', slavedb)
    newData = newData.replace('[masterhost]', masterhost)
    newData = newData.replace('[slavehost]', slavehost)
    newData = newData.replace('[masterport]', masterport)
    newData = newData.replace('[slaveport]', slaveport)
    newData = newData.replace('[masteruser]', masteruser)
    newData = newData.replace('[masterpass]', masterpass)
    newData = newData.replace('[slaveuser]', slaveuser)
    newData = newData.replace('[slavepass]', slavepass)
    newData = newData.replace('[clustername]', cluster)
    
    split = name.split('.')
    newname = split[0]+'_temp.'+split[1]
    
    script = open(newname, 'w')
    script.write(newData)
    script.close()
    
    return newname
    
def runProcess(cmd):
    args = cmd.split()
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    out, err = p.communicate()
    rc = p.returncode
    return rc, out, err
            
def runCall(cmd):
    subprocess.call(cmd, shell=True)
    
def message(msg):
    # HTML return
    print "Content-type:text/plain"
    print
    print msg

#updating users
if updatePostgresUsers():    
    # Updating scripts
    if dbversion == '2.1.3':
        slony = 'slony_213.sh'
    elif dbversion == 'FTer_2a_Ed':
        slony = 'slony_fter.sh'
    else:
        message('Problema na criação do cluster: Versão de bancos incompatível com o plugin (Use somente EDGV 2.1.3 ou FTer_2a_Ed)')
        
    slony_temp = updateScript(slony, masterdb, slavedb, masterhost, slavehost, masterport, slaveport, masteruser, masterpass, slaveuser, slavepass, clustername)
     
    # Configuring slony and subscribing
    cmd = 'sh {}'.format(slony_temp)
    rc, out, err = runProcess(cmd)
    if rc == 0:        
        msg = 'Cluster %s configurado com sucesso!' % clustername
        message(msg)
    else:
        msg = 'Problema na criação do Cluster %s!' % clustername
        if out:
            msg += '\n Saída: %s' % str(out)
        if err:
            msg += '\n Erro: %s' % str(err)            
        message(msg)
        