```
usage: reset_asset_groups.py [-h] [-u USER] [-p PASSWORD] [-a API_URL] [-P] [-U PROXY_URL] [-s] [-d]

options:
  -h, --help            show this help message and exit
  -u USER, --user USER  Qualys Username
  -p PASSWORD, --password PASSWORD
                        Qualys Password (use - for interactive input
  -a API_URL, --api_url API_URL
                        Qualys API URL (e.g. https://qualysapi.qualys.eu)
  -P, --proxy_enable    Enable HTTPS proxy for outgoing connection
  -U PROXY_URL, --proxy_url PROXY_URL
                        HTTPS Proxy address
  -s, --simulate        Simulation mode, do not make changes
  -d, --debug           Enable debug output for API calls
```