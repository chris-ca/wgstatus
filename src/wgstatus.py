#!/usr/bin/env python3
#####################################################################################################################
# Script Name     : .py 
# Description     : 
# 
# 
# 
# Requires        : 
# Arguments       :  
# Run Information : This script is run manually|via crontab.
# Author          : Chris, 2020
# Output          : 
#####################################################################################################################
import re, datetime, time, argparse
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

def get_remote(values, interface='all'):
    """ The fields in order they appear in the wg output """
    fields = ['public_key', 'preshared_key', 'endpoint', 'allowed_ips', 'latest_handshake', 'transfer_rx', 'transfer_tx', 'persistent_keepalive']
    if len(values) == 9:
        fields.insert(0, 'interface')
    peer = dict(zip(fields, values))

    #peer['allowed_ips'] = peer['allowed_ips'].split(',')
    if peer['preshared_key'] == '(none)':
        peer['preshared_key'] = None
    if peer['persistent_keepalive'] == 'off':
        peer['persistent_keepalive'] = None
    peer['role'] = 'remote'
    return peer

def get_local(values):
    """ The fields in order they appear in the wg output """
    fields = ['private_key', 'public_key', 'port', 'fwmark']
    if len(values) == 5:
        fields.insert(0, 'interface')

    peer = dict(zip(fields, values))
    peer.pop('private_key')

    if peer['fwmark'] == 'off':
        peer['fwmark'] = None
    peer['role'] = 'local'
    return peer

def get_peer(line):
    """ Field delimiter should be a single TAB """
    values = [item for item in re.split(r'\s+', line)]
    if len(values) <= 5:
        peer = get_local(values)
    elif len(values) <= 9:
        peer = get_remote(values)
    else:
        raise Exception('Unknown format')

    peer = { k: int(v) if (k in ['port','latest_handshake', 'transfer_rx', 'transfer_tx', 'persistent_keepalive']) and (v is not None) else v
                 for k, v in peer.items() } # numeric strings to integer

    return peer

def wg_output(interface='all'):
    '''Parses the given output of the WireGuard command and stores it'''
    ''' based on https://github.com/towalink/wgtrack/blob/main/src/wgtrack/wg_command.py '''

    # tested with wireguard-tools v1.0.20210914 
    cmd = f"wg show {interface} dump" 
    logger.info("Executing command: "+ cmd)
    proc  = subprocess.run(cmd.split(' '), capture_output=True, text=True)

    if proc.returncode > 0:
        logger.error(proc.stderr)
        raise Exception(proc.stderr)

    peers = []
    for i, line in enumerate(proc.stdout.splitlines()):
        peer = get_peer(line)
        if_ = interface if not 'interface' in peer else peer['interface']
        logger.info('if {} peer {}'.format(if_, peer['public_key']))
        peers.append(peer)

    logger.info('{} peers'.format(str(len(peers))))
    return peers

def to_json(peers):
    content = {
        'updated' : datetime.datetime.utcnow().isoformat(),
        'peers'   : peers
    }
    return json.dumps(content, indent=4)

def save_as(content, path):
    with open(path, 'w') as f:
        f.write(content)

parser = argparse.ArgumentParser()
parser.add_argument("interface", nargs='?', default='all')
parser.add_argument("--log", default='/var/log/wg.json')
parser.add_argument("--loop", type=int, default=None)
parser.add_argument("--debug", action="store_true", help="Print only, do not write log file")

args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.INFO)

if not args.loop:
    c = to_json(wg_output(args.interface))
    print(c)
else:
    while True:
        save_as(to_json(wg_output(args.interface)), args.log)
        time.sleep(args.loop)
