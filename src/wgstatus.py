#!/usr/bin/env python3
"""
Script to check Wireguard interfaces and transform the output of
`wg show dump` to JSON.

Multiple interfaces are supported.

The following JSON is generated to be read by the client::

    ``
    {
        "updated": "2022-12-08T05:09:15.156042",
        "peers": [
            {
                "interface": "wg0",
                "public_key": "Koooooooooooooooooooooooooooooooooooooooook=",
                "port": 51230,
                "fwmark": null,
                "role": "local"
            },
            {
                "interface": "wg0",
                "public_key": "xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXa=",
                "preshared_key": null,
                "endpoint": "12.123.45.89:38639",
                "allowed_ips": "192.168.78.2/32",
                "latest_handshake": 1670476120,
                "transfer_rx": 41642124,
                "transfer_tx": 98421512,
                "persistent_keepalive": null,
                "role": "remote"
            }
        ]
    }
    ``
"""
import re
import datetime
import time
import logging
import argparse
import subprocess
import json

logger = logging.getLogger(__name__)


def get_remote(values: list) -> dict:
    """Return dictionary of remote peer fields"""
    fields = [
        "public_key",
        "preshared_key",
        "endpoint",
        "allowed_ips",
        "latest_handshake",
        "transfer_rx",
        "transfer_tx",
        "persistent_keepalive",
    ]

    # Multiple interfaces if 9 fields are given
    if len(values) == 9:
        fields.insert(0, "interface")

    peer = dict(zip(fields, values))

    # peer['allowed_ips'] = peer['allowed_ips'].split(',')
    if peer["preshared_key"] == "(none)":
        peer["preshared_key"] = None
    if peer["persistent_keepalive"] == "off":
        peer["persistent_keepalive"] = None
    peer["role"] = "remote"
    return peer


def get_local(values: list) -> dict:
    """Return dictionary of remote peer fields"""
    fields = ["private_key", "public_key", "port", "fwmark"]
    # Multiple interfaces if 5 fields are given
    if len(values) == 5:
        fields.insert(0, "interface")

    peer = dict(zip(fields, values))
    peer.pop("private_key")

    if peer["fwmark"] == "off":
        peer["fwmark"] = None
    peer["role"] = "local"
    return peer


def get_peer(line: str):
    """Field delimiter should be a single TAB"""
    values = list(re.split(r"\s+", line))
    if len(values) <= 5:
        peer = get_local(values)
    elif len(values) <= 9:
        peer = get_remote(values)
    else:
        raise Exception("Unknown format")

    peer = {
        k: int(v)
        if (
            k
            in [
                "port",
                "latest_handshake",
                "transfer_rx",
                "transfer_tx",
                "persistent_keepalive",
            ]
        )
        and (v is not None)
        else v
        for k, v in peer.items()
    }  # numeric strings to integer

    return peer


def wg_output(interface="all") -> list:
    """Parse output of wg interface.

    Based on https://github.com/towalink/wgtrack/blob/main/src/wgtrack/wg_command.py
    """

    # tested with wireguard-tools v1.0.20210914
    cmd = f"wg show {interface} dump"
    logger.info("Executing command: %s", cmd)
    # breakpoint()
    try:
        proc = subprocess.run(
            cmd.split(" "), capture_output=True, text=True, check=True
        )

        peers = []
        for _, line in enumerate(proc.stdout.splitlines()):
            peer = get_peer(line)
            if_ = interface if not "interface" in peer else peer["interface"]
            logger.info("if %s peer %s", if_, peer["public_key"])
            peers.append(peer)

        logger.info("%s peers", str(len(peers)))
        return peers
    except subprocess.CalledProcessError as exc:
        logger.error(exc.stderr)
        raise Exception from exc


def to_json(peers) -> str:
    """Convert dictionary to Json"""
    content = {"updated": datetime.datetime.utcnow().isoformat(), "peers": peers}
    return json.dumps(content, indent=4)


def save_as(content, path):
    """Save contents to path"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


parser = argparse.ArgumentParser()
parser.add_argument("interface", nargs="?", default="all")
parser.add_argument("--log", default="/var/log/wg.json")
parser.add_argument(
    "--loop",
    type=int,
    default=None,
    help="Wait [n] seconds between checking WG interface",
)
parser.add_argument(
    "--debug", action="store_true", help="Print only, do not write log file"
)

args = parser.parse_args()

if args.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

if not args.loop:
    c = to_json(wg_output(args.interface))
    print(c)
else:
    while True:
        save_as(to_json(wg_output(args.interface)), args.log)
        time.sleep(args.loop)
