# Wgstatus

Wgstatus is Python/HTML based script to display the connectivity of peers on a Wireguard interface in a web browser

### Prerequisites

On the machine running the monitored wireguard interface:
- Python is installed
- A web server is running to host the HTML file (or else, start a web server with `python3 -m http.server -d /var/www/html --bind 192.168.78.1 8080`)

## Installation

- Copy script to permanent location, e.g. `sudo cp wgstatus.py /usr/local/bin`
- Create a systemd service file and copy it to `/etc/systemd/system/wgstatus.service`
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

## Development Goals

- Display data from `wg` without having to invoke `wg` by the web server process
- Lean: No use of frontend libraries such as vue.js or bootstrap
- No web server side scripting 

