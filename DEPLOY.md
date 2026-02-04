# Clawdbot Deployment Guide

## Classic Sports Barbershop Chatbot POC

## Prerequisites

- Python 3.8+
- Local Mistral model running at `http://192.168.35.251:8081/v1`
- pip (Python package manager)

## Installation

### 1. Clone/Copy the Project

```bash
cd /home/dee/.openclaw/workspace
mkdir -p clawdbot
# Copy app.py, templates/, static/, local_llm.env to clawdbot/
```

### 2. Install Dependencies

```bash
pip install flask python-dotenv requests
```

### 3. Configure Environment

The `local_llm.env` file is already configured:

```env
LLM_BASE_URL=http://192.168.35.251:8081/v1
LLM_MODEL=mistral
API_PORT=5000
DEBUG=true
```

## Running Locally

### Start the Application

```bash
cd /home/dee/.openclaw/workspace/clawdbot
python app.py
```

The chatbot will be available at:
- **Web Interface**: http://localhost:5000
- **API**: http://localhost:5000/api/chat

### Test the API

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your hours?"}'
```

## Docker Deployment (Recommended)

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### 2. Create requirements.txt

```
flask>=2.0.0
python-dotenv>=1.0.0
requests>=2.28.0
```

### 3. Build and Run

```bash
cd /home/dee/.openclaw/workspace/clawdbot
docker build -t clawdbot .
docker run -d \
  --name clawdbot \
  -p 5000:5000 \
  --env-file local_llm.env \
  clawdbot
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Systemd

Create `/etc/systemd/system/clawdbot.service`:

```ini
[Unit]
Description=Clawdbot - Classic Sports Barbershop Chatbot
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/dee/.openclaw/workspace/clawdbot
EnvironmentFile=/home/dee/.openclaw/workspace/local_llm.env
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable clawdbot
sudo systemctl start clawdbot
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Verifying Deployment

1. **Check Health**: `curl http://localhost:5000/api/health`
2. **Test Chat**: Use the web interface or API
3. **Check Logs**: `docker logs clawdbot` (if using Docker)

## Troubleshooting

### LLM Connection Issues

- Verify Mistral is running: `curl http://192.168.35.251:8081/v1/models`
- Check the base URL in `local_llm.env`
- Ensure firewall allows port 8081

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill it or use a different port
export API_PORT=5001
python app.py
```

### App Won't Start

- Check virtual environment is activated
- Verify all dependencies installed: `pip list`
- Check Python version: `python --version`

## Scaling Considerations

For production, consider:
- **Redis** for session/appointment storage
- **PostgreSQL** for persistent appointments
- **Load balancer** for multiple instances
- **SSL/TLS** certificate for HTTPS
- **Rate limiting** on API endpoints
- **Logging** (e.g., structured logging with ELK stack)

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_BASE_URL` | Local LLM API endpoint | http://192.168.35.251:8081/v1 |
| `LLM_MODEL` | Model name to use | mistral |
| `API_PORT` | Port for Flask app | 5000 |
| `DEBUG` | Enable debug mode | true |

## Next Steps for Production

1. Replace in-memory appointments with database
2. Add appointment confirmation via SMS/email
3. Implement booking calendar with time slots
4. Add admin panel for managing appointments
5. Integrate with payment processing (optional)
6. Add analytics for chat insights
