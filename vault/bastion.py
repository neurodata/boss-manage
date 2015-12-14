#!/usr/bin/env python3

import subprocess
import shlex
import os
import signal
import sys
import time
from boto3.session import Session
import json
import vault

# Needed to prevent ssh from asking about the fingerprint from new machines
SSH_OPTIONS = "-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

def become_tty_fg():
    """ From: http://stackoverflow.com/questions/15200700/how-do-i-set-the-terminal-foreground-process-group-for-a-process-im-running-und
        Create a new foreground process group for the new process
    """
    os.setpgrp()
    hdlr = signal.signal(signal.SIGTTOU, signal.SIG_IGN)
    tty = os.open('/dev/tty', os.O_RDWR)
    os.tcsetpgrp(tty, os.getpgrp())
    signal.signal(signal.SIGTTOU, hdlr)

def ssh(key, remote, bastion):
    fwd_cmd = "ssh -i {} {} -N -L 2222:{}:22 ec2-user@{}".format(key, SSH_OPTIONS, remote, bastion)
    ssh_cmd = "ssh -i {} {} -p 2222 ubuntu@localhost".format(key, SSH_OPTIONS)
    
    proc = subprocess.Popen(shlex.split(fwd_cmd))
    time.sleep(1) # wait for the tunnel to be setup
    try:
        ret = subprocess.call(shlex.split(ssh_cmd), close_fds=True, preexec_fn=become_tty_fg)
    finally:
        proc.terminate()
        proc.wait()
    
def connect_vault(key, remote, bastion, cmd):
    fwd_cmd = "ssh -i {} {} -N -L 8200:{}:8200 ec2-user@{}".format(key, SSH_OPTIONS, remote, bastion)

    proc = subprocess.Popen(shlex.split(fwd_cmd))
    time.sleep(1) # wait for the tunnel to be setup
    try:
        cmd()
    finally:
        proc.terminate()
        proc.wait()

def create_session(cred_file):
    with open(cred_file, "r") as fh:
        credentials = json.load(fh)
        
    session = Session(aws_access_key_id = credentials["aws_access_key"],
                      aws_secret_access_key = credentials["aws_secret_key"],
                      region_name = 'us-east-1')
    return session
    
def machine_lookup(session, hostname):
    client = session.client('ec2')
    response = client.describe_instances(Filters=[{"Name":"tag:Name", "Values":[hostname]},
                                                  {"Name":"instance-state-name", "Values":["running"]}])\

    item = response['Reservations']
    if len(item) == 0:
        return None
    else:
        item = item[0]['Instances']
        if len(item) == 0:
            return None
        else:
            item = item[0]
            if 'PublicIpAddress' in item:
                return item['PublicIpAddress']
            elif 'PrivateIpAddress' in item:
                return item['PrivateIpAddress']
            else:
                return None
    
def usage():
    vault_keys = "|".join(vault.COMMANDS.keys())
    print("Usage: {} <aws-credentials> <ssh_key> <bastion_hostname> <internal_hostname> (ssh|{})".format(sys.argv[0], vault_keys))
    sys.exit(1)
    
if __name__ == "__main__":
    if len(sys.argv) < 6:
        usage()
    
    cred_file = sys.argv[1]
    key = sys.argv[2]
    bastion = sys.argv[3]
    private = sys.argv[4]
    cmd = sys.argv[5]
    
    session = create_session(cred_file)
    bastion = machine_lookup(session, bastion)
    private = machine_lookup(session, private)
    
    if cmd in ("ssh",):
        ssh(key, private, bastion)
    elif cmd in vault.COMMANDS:
        connect_vault(key, private, bastion, vault.COMMANDS[cmd])
    else:
        usage()