# Ciao - Hello in Random Languages

A simple, mobile-friendly web app that displays "Hello" in a random language each time you visit.

## Setup

### Prerequisites
- Python 3.8 or higher
- uv (recommended) or pip

### Installation

Using uv (recommended):
```bash
uv pip install -r requirements.txt
```

Using pip:
```bash
pip install -r requirements.txt
```

## Running the App

### Option 1: Flask Version (Recommended)
Requires Flask to be installed (see Installation above):
```bash
python app.py
```
The app will be available at `http://localhost:5000`

### Option 2: Built-in HTTP Server (No Dependencies)
Uses only Python's built-in http.server module:
```bash
python app_builtin.py
```
The app will be available at `http://localhost:5000`

This version is useful for environments where installing external packages is not possible.

## Development

The app randomly selects from 15 different languages each time you visit the page:
- English, Spanish, French, German, Italian
- Portuguese, Dutch, Russian, Japanese, Chinese
- Korean, Arabic, Hindi, Greek, Turkish

Each page load displays "Hello" in a different language with a clean, mobile-friendly interface.

## Production Deployment

### Running as a Webserver on DigitalOcean

The app is currently deployed on a DigitalOcean droplet at **159.223.220.39**.

#### Initial Server Setup

1. **SSH into the droplet:**
   ```bash
   ssh root@159.223.220.39
   ```

2. **Install Python and dependencies:**
   ```bash
   apt update
   apt install -y python3 python3-pip python3-venv git
   ```

3. **Install uv (recommended):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env
   ```

4. **Clone the repository:**
   ```bash
   cd /opt
   git clone <repository-url> ciao
   cd ciao
   ```

5. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

#### Running the App as a Service

1. **Create a systemd service file:**
   ```bash
   nano /etc/systemd/system/ciao.service
   ```

2. **Add the following configuration:**
   ```ini
   [Unit]
   Description=Ciao Flask Application
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/opt/ciao
   Environment="PATH=/root/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
   ExecStart=/usr/bin/python3 app.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**
   ```bash
   systemctl daemon-reload
   systemctl enable ciao
   systemctl start ciao
   ```

4. **Check service status:**
   ```bash
   systemctl status ciao
   ```

#### Setting up Nginx as Reverse Proxy (Optional but Recommended)

1. **Install Nginx:**
   ```bash
   apt install -y nginx
   ```

2. **Create Nginx configuration:**
   ```bash
   nano /etc/nginx/sites-available/ciao
   ```

3. **Add the following configuration:**
   ```nginx
   server {
       listen 80;
       server_name 159.223.220.39;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Enable the site and restart Nginx:**
   ```bash
   ln -s /etc/nginx/sites-available/ciao /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

#### Accessing the App

Once deployed, the app will be accessible at:
- **Direct access:** http://159.223.220.39:5000 (if running Flask directly)
- **With Nginx:** http://159.223.220.39 (on port 80)

#### Updating the App

To update the app after making changes:
```bash
cd /opt/ciao
git pull
systemctl restart ciao
```

#### Viewing Logs

```bash
# Service logs
journalctl -u ciao -f

# Nginx logs (if using reverse proxy)
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Tech Stack
- Python 3.8+
- Flask 3.0.0 (optional - built-in version available)
- Server-side HTML rendering
