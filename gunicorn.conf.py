# Gunicorn configuration for Render deployment
# Increase worker timeout to handle SMTP email batch sending without 502 errors

workers = 1          # Keep at 1 for free-tier Render (512 MB RAM)
threads = 4          # Allow concurrent requests within the single worker process
timeout = 120        # 2-minute timeout per request (prevents 502 on batch emails)
keepalive = 5        # Keep connections alive for 5 seconds
import os
port = os.getenv('PORT', '8000')
bind = f"0.0.0.0:{port}"
