# Wgstatus

Wgstatus is Python/HTML based script to display the connectivity of peers with local wireguard interfaces.

The server side script will transform the output of `wg show` into JSON:

```json
{
    "updated": "2022-12-08T05:09:15.156042",
    "peers": [
        {
            "interface": "wg0",
            "public-key": "Koooooooooooooooooooooooooooooooooooooooook=",
            "port": 51230,
            "fwmark": null,
            "role": "local"
        },
        {
            "interface": "wg0",
            "public-key": "xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXa=",
            "preshared-key": null,
            "endpoint": "12.123.45.89:38639",
            "allowed-ips": "192.168.78.2/32",
            "latest-handshake": 1670476120,
            "transfer-rx": 41642124,
            "transfer-tx": 98421512,
            "persistent-keepalive": null,
            "role": "remote"
        }
    ]
}
```

The client side will display 
## Development Goals
- Display data from `wg` without having to invoke `wg` by the web server process
- Lean: No use of frontend libraries such as vue.js or bootstrap
- Exercise: Implement a websocket or HTTP PUSH for "real time" updates
- No (web) server side scripting 

## Installation
```bash
pip install ... #FIXME
```

## Usage
Create a systemd service file and copy it to `/etc/systemd/system/wgstatus.service`

```ini
[Unit]
Description=Wireguard status service
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /usr/local/bin/wgstatus.py

[Install]
WantedBy=multi-user.target
```
