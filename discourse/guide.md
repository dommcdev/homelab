## Setup

### Step 0: Domain name
Purchase a domain and add a DNS A record pointing to your router's ip. Then ensure the router is port forwarding 80/443 to the machine running the Apache reverse proxy.

### Step 1: Apache Configuration
We need to perform SSL termination. Use the cathsocial.com.ssl.conf file and restart the httpd service. At this point http traffic will be being sent to our 2nd server, i.e. the one that will actually run Discourse

### Step 2: Setup discourse
```bash
# Clone our Discourse configs
git clone https://github.com/discourse/discourse_docker.git /var/discourse

# Clone the discourse repo
git clone https://github.com/discourse/discourse_docker.git /var/discourse
cd /var/discourse

# Copy over our app.yml
cp ~/dev/homelab/discourse/app.yml /var/discourse/containers/app.yml
chmod 700 containers/app.yml
# Don't forget to add a real Resend API key

# Build app
./launcher rebuild app
