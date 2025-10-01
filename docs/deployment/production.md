# Production Deployment Guide

This guide covers deploying the 3D Store application to a production environment.

## 🚀 Overview

The 3D Store application consists of:
- **Backend**: Flask API server
- **Frontend**: Angular 20 application
- **Database**: PostgreSQL
- **Cache**: Redis
- **File Storage**: AWS S3 or similar

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   Web Server    │────│   Application   │
│   (Nginx)       │    │   (Nginx)       │    │   (Flask)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Frontend      │
                       │   (Angular)     │
                       └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │  PostgreSQL │ │    Redis    │ │   AWS S3    │
        │  Database   │ │    Cache    │ │File Storage │
        └─────────────┘ └─────────────┘ └─────────────┘
```

## 🛠️ Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04 LTS or CentOS 8
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 100GB+ SSD
- **Network**: 1Gbps connection

### Software Requirements
- Python 3.8+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Nginx
- Docker (optional)
- Certbot (for SSL)

## 🔧 Backend Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.8 python3.8-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx
sudo apt install nginx -y
```

### 2. Database Setup

```bash
# Create database user
sudo -u postgres createuser --interactive
# Enter username: 3dstore
# Enter role: y
# Enter superuser: n

# Create database
sudo -u postgres createdb 3dstore

# Set password
sudo -u postgres psql
ALTER USER 3dstore PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE 3dstore TO 3dstore;
\q
```

### 3. Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/3dstore
sudo chown $USER:$USER /opt/3dstore

# Clone repository
cd /opt/3dstore
git clone https://github.com/maz1987in/3D-Store.git .

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp env_production .env
nano .env
```

### 4. Environment Configuration

```bash
# .env file
DATABASE_URL=postgresql://3dstore:secure_password@localhost/3dstore
JWT_SECRET_KEY=your_super_secret_jwt_key_here
UPLOAD_FOLDER=/opt/3dstore/uploads
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=production
FLASK_DEBUG=False

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=3dstore-files
AWS_REGION=us-east-1

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### 5. Database Migration

```bash
# Run migrations
alembic upgrade head

# Create admin user
python create_admin.py
```

### 6. Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/3dstore-backend.service
```

```ini
[Unit]
Description=3D Store Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/3dstore/backend
Environment=PATH=/opt/3dstore/backend/venv/bin
ExecStart=/opt/3dstore/backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable 3dstore-backend
sudo systemctl start 3dstore-backend
```

## 🎨 Frontend Deployment

### 1. Build Angular Application

```bash
# Install dependencies
cd frontend
npm install

# Build for production
ng build --prod

# Copy build files to web server
sudo cp -r dist/3dstore/* /var/www/html/
```

### 2. Nginx Configuration

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/3dstore
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Frontend
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /3dstore/api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # File uploads
    client_max_body_size 100M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/3dstore /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring

### 1. Log Management

```bash
# Backend logs
sudo journalctl -u 3dstore-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Health Checks

```bash
# Create health check script
sudo nano /opt/3dstore/health_check.sh
```

```bash
#!/bin/bash
# Check if backend is running
if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "Backend is down, restarting..."
    sudo systemctl restart 3dstore-backend
fi

# Check if database is accessible
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "Database is down!"
    exit 1
fi
```

```bash
# Make executable
sudo chmod +x /opt/3dstore/health_check.sh

# Add to crontab
sudo crontab -e
# Add: */5 * * * * /opt/3dstore/health_check.sh
```

## 🔄 Backup Strategy

### 1. Database Backup

```bash
# Create backup script
sudo nano /opt/3dstore/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/3dstore/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="3dstore_backup_$DATE.sql"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U 3dstore 3dstore > $BACKUP_DIR/$BACKUP_FILE
gzip $BACKUP_DIR/$BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### 2. File Backup

```bash
# Backup uploads directory
rsync -av /opt/3dstore/uploads/ /backup/uploads/
```

## 🚀 Docker Deployment (Alternative)

### 1. Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://3dstore:password@db:5432/3dstore
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=3dstore
      - POSTGRES_USER=3dstore
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 2. Deploy with Docker

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_print_jobs_status ON print_jobs(status);
CREATE INDEX idx_products_category ON products(category_id);
```

### 2. Redis Configuration

```bash
# Optimize Redis
sudo nano /etc/redis/redis.conf
```

```
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Nginx Optimization

```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;

gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

client_max_body_size 100M;
```

## 🔧 Maintenance

### 1. Updates

```bash
# Update application
cd /opt/3dstore
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart 3dstore-backend

# Update frontend
cd ../frontend
npm install
ng build --prod
sudo cp -r dist/3dstore/* /var/www/html/
```

### 2. Monitoring Commands

```bash
# Check service status
sudo systemctl status 3dstore-backend

# Check disk usage
df -h

# Check memory usage
free -h

# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

## 📞 Support

For production deployment issues:
- Check system logs
- Verify service status
- Review configuration files
- Contact system administrator
