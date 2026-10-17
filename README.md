# Send Request To Webhooks
You can send json/discord request to links when you visit the website it hosts.
# NOTE: This only supports ubuntu, centos, debian, Fedora, RHEL
## Examples
Example config (config.yaml):
```
webhook:
  # URL to call when someone visits. Works with a Home Assistant webhook,
  # a Discord webhook, or any other URL that accepts HTTP requests.
  # Home Assistant: use the HA machine's IP, not homeassistant.local.
  url: "http://192.168.1.50:8123/api/webhook/YOUR_WEBHOOK_ID"
  method: GET          # GET or POST (default POST) Use post for discord.
  format: json         # only used when method is POST: "json" or "discord"
  timeout: 5           # seconds to wait for the webhook to respond

visits:
  cooldown_seconds: 60       # don't re-notify the same IP within this many seconds
  only_pages: true           # only count "/" and *.html, not images/css/js
  include_ip: true           # include the visitor's IP in the webhook data
  trust_proxy_headers: false # set true only if behind nginx/Cloudflare/etc.
  # IPs that never trigger the webhook
  ignore_ips: []
  # Example:
  # ignore_ips:
  #   - 192.168.1.10
```
Example compose file (docker-compose.yml or compose.yaml):
```
services:
  visit-notifier:
    image: ghcr.io/windabest/visit-notifier:latest
    container_name: visit-notifier
    ports:
      - "8080:8080"   # host:container. Change the left number if 8080 is taken.
    volumes:
      # Required: your config file.
      - ./config.yaml:/config/config.yaml:ro
      # Optional: serve your own website instead of the built-in example page
      # - ./site:/app/site:ro
    restart: unless-stopped
```
## Instructions
1. Install docker: <p><a title="How To Install Docker Compose" href="https://docs.docker.com/compose/install/linux/#install-using-the-repository" target="_blank">How To Install Docker Compose</a></p>
And install:
```
sudo apt install nano     # For ubuntu/debian
sudo dnf install nano     # For centos/fedora/RHEL
```
3. Create your docker compose container folder (You can create the folder anywhere. Just don't put it in a folder you only have read in):
```
mkdir ~/visit-notifier
```
3. Copy the example Docker Compose File and run:
```
cd ~/visit-notifier
nano docker-compose.yml # Or use compose.yaml
```
Then paste the code in and edit it if you want to. Exit and save with "ctrl+o" and "enter" and "ctrl+x"

4. Copy the example config and run:
```
cd ~/visit-notifier
nano config.yaml
```
Then paste the code in and edit it. Exit and save with "ctrl+o" and "enter" and "ctrl+x"

5. To start it up run:
```
docker compose up -d # Or run "docker compose up" to see the logs.
```
6. Get you local ip address. Run:
```
hostname -I | awk '{print $1}'
```
7. With your local ip address go to the website "YOUR.LOCAL.IP.ADDRESS:8080" (Change "YOUR.LOCAL.IP.ADDRESS" to your local ip address)

## Now to installed it!
