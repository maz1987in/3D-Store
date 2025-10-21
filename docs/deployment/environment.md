# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the 3D Store application.

## Overview

Environment variables are used to configure the application for different environments (development, staging, production) without changing the code.

### Configuration Files

- **Backend**: `.env` file in `/backend/` directory
- **Frontend**: `environment.ts` and `environment.prod.ts` in `/frontend/src/environments/`

---

## Backend Environment Variables

### Database Configuration

#### PostgreSQL/MySQL

```bash
# Database Type
DB_TYPE=postgresql  # Options: postgresql, mysql, sqlite

# Database Credentials
DB_USERNAME=your_database_username
DB_PASSWORD=your_database_password
DB_DATABASE_NAME=store3d
DB_HOST=localhost:5432

# Full Database URL (alternative to individual settings)
DATABASE_URL=postgresql://username:password@localhost:5432/store3d
```

#### SQLite (Development Only)

```bash
DB_TYPE=sqlite
DB_DATABASE_NAME=store3d.sqlite3
```

**Notes**:
- Use PostgreSQL or MySQL for production
- SQLite is suitable only for development/testing
- `DATABASE_URL` takes precedence over individual DB_ variables

---

### Application Configuration

```bash
# Flask Environment
FLASK_APP=run.py
FLASK_ENV=development  # Options: development, production
FLASK_DEBUG=True  # Set to False in production

# Application URL
APP_URL=http://localhost:5000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:4200

# API Version
API_VERSION=v1
```

---

### Security Configuration

```bash
# Secret Keys
SECRET_KEY=your_super_secret_key_change_this_in_production
SECURITY_PASSWORD_SALT=your_password_salt_change_this

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_change_this
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hours in seconds
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days in seconds

# Session Configuration
SESSION_TYPE=filesystem
SESSION_PERMANENT=False
SESSION_USE_SIGNER=True
```

**⚠️ Security Warning**:
- **Never** commit `.env` files to version control
- Use strong, random values for SECRET_KEY and JWT_SECRET_KEY
- Change default values in production
- Rotate keys periodically

**Generating Secure Keys**:
```python
import secrets
secret_key = secrets.token_hex(32)
print(secret_key)
```

---

### Cache Configuration

```bash
# Cache System
CACHE_ENABLED=True  # Set to False to disable caching
CACHE_TYPE=redis  # Options: redis, memcached, simple
CACHE_DEFAULT_TIMEOUT=300  # 5 minutes in seconds

# Redis Configuration
CACHE_REDIS_HOST=localhost
CACHE_REDIS_PORT=6379
CACHE_REDIS_DB=0
CACHE_REDIS_PASSWORD=your_redis_password
REDIS_URL=redis://localhost:6379/0  # Full Redis URL
CACHE_KEY_PREFIX=3dstore:
```

**Cache Types**:
- `redis` - Production (recommended)
- `memcached` - Alternative caching backend
- `simple` - In-memory cache (development only)

---

### File Storage Configuration

```bash
# Upload Directory
UPLOAD_FOLDER=/path/to/uploads
MAX_CONTENT_LENGTH=104857600  # 100MB in bytes

# File Storage Backend
STORAGE_BACKEND=local  # Options: local, s3, gcs

# AWS S3 Configuration (if using S3)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=3dstore-files
AWS_REGION=us-east-1
AWS_S3_CUSTOM_DOMAIN=cdn.3dstore.com  # Optional CDN

# Depot Configuration
DEPOT_BACKEND_STORAGE=local  # Options: local, s3, gcs
DEPOT_STORAGE_PATH=/path/to/depot/storage
```

**Storage Backends**:
- `local` - Local file system (development)
- `s3` - AWS S3 (production recommended)
- `gcs` - Google Cloud Storage

---

### Email Configuration

```bash
# Email Server
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# Email Credentials
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_specific_password
MAIL_DEFAULT_SENDER=3dstore@example.com

# Email Templates
MAIL_TEMPLATE_FOLDER=/path/to/email/templates
```

**Gmail Setup**:
1. Enable 2-factor authentication
2. Generate app-specific password
3. Use app password as MAIL_PASSWORD

---

### Logging Configuration

```bash
# Log Level
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log Format
LOG_FORMAT=json  # Options: json, text

# Log Outputs
LOG_CONSOLE_ENABLED=True
LOG_FILE_ENABLED=True
LOG_FILE_PATH=/path/to/logs/app.log

# Log Rotation
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=10
```

---

### Task Scheduler Configuration

```bash
# Scheduler
SCHEDULER_API_ENABLED=True
SCHEDULER_TIMEZONE=UTC

# Job Store
SCHEDULER_JOBSTORES=redis
SCHEDULER_REDIS_URL=redis://localhost:6379/1
```

---

### Rate Limiting Configuration

```bash
# Rate Limiting
RATELIMIT_ENABLED=True
RATELIMIT_STORAGE_URL=redis://localhost:6379/2

# Default Limits
RATELIMIT_DEFAULT=100/hour
RATELIMIT_LOGIN=5/minute
RATELIMIT_UPLOAD=10/hour
```

---

### Payment Gateway Configuration

#### Thawani Pay

```bash
# Thawani Configuration
THAWANI_API_KEY=your_thawani_api_key
THAWANI_SECRET_KEY=your_thawani_secret_key
THAWANI_PUBLISHABLE_KEY=your_thawani_publishable_key
THAWANI_MODE=test  # Options: test, live
THAWANI_API_URL=https://uatcheckout.thawani.om  # Test URL
```

#### OMPay

```bash
# OMPay Configuration
OMPAY_MERCHANT_ID=your_merchant_id
OMPAY_API_KEY=your_ompay_api_key
OMPAY_SECRET_KEY=your_ompay_secret_key
OMPAY_MODE=test  # Options: test, live
OMPAY_API_URL=https://test.ompay.om  # Test URL
```

---

### OAuth Configuration

#### Google OAuth

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/3dstore/api/v1/auth/google/callback
```

#### Apple OAuth

```bash
# Apple OAuth
APPLE_CLIENT_ID=your_apple_client_id
APPLE_TEAM_ID=your_apple_team_id
APPLE_KEY_ID=your_apple_key_id
APPLE_PRIVATE_KEY_PATH=/path/to/apple/private/key.pem
APPLE_REDIRECT_URI=http://localhost:5000/3dstore/api/v1/auth/apple/callback
```

#### Twitter OAuth

```bash
# Twitter OAuth
TWITTER_CONSUMER_KEY=your_twitter_consumer_key
TWITTER_CONSUMER_SECRET=your_twitter_consumer_secret
TWITTER_REDIRECT_URI=http://localhost:5000/3dstore/api/v1/auth/twitter/callback
```

---

### Monitoring and Analytics

```bash
# Sentry (Error Tracking)
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Google Analytics
GA_TRACKING_ID=UA-XXXXXXXXX-X

# Metrics
METRICS_ENABLED=True
PROMETHEUS_PORT=9090
```

---

### CORS Configuration

```bash
# CORS Settings
CORS_ENABLED=True
CORS_ORIGINS=http://localhost:4200,https://3dstore.com
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization,x-access-tokens
CORS_EXPOSE_HEADERS=Content-Range,X-Content-Range
CORS_SUPPORTS_CREDENTIALS=True
CORS_MAX_AGE=3600
```

---

### Timezone and Localization

```bash
# Timezone
TZ=UTC
TIMEZONE=UTC

# Default Language
DEFAULT_LANGUAGE=ENGLISH  # Options: ENGLISH, ARABIC
SUPPORTED_LANGUAGES=ENGLISH,ARABIC
```

---

## Frontend Environment Variables

### Development Environment

**File**: `frontend/src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  
  // API Configuration
  apiUrl: 'http://localhost:5000/3dstore/api/v1',
  wsUrl: 'ws://localhost:5000/ws',
  uploadUrl: 'http://localhost:5000/3dstore/api/v1/upload',
  
  // File Upload
  maxFileSize: 104857600, // 100MB
  supportedFormats: ['.stl', '.obj', '.3mf'],
  
  // Storage Keys
  tokenKey: 'auth_token',
  refreshTokenKey: 'refresh_token',
  userKey: 'current_user',
  
  // Feature Flags
  enableGoogleAuth: true,
  enableAppleAuth: false,
  enableTwitterAuth: false,
  enablePWA: false,
  enableOfflineMode: false,
  
  // Analytics
  googleAnalyticsId: '',
  enableAnalytics: false,
  
  // Monitoring
  sentryDsn: '',
  enableSentry: false,
  
  // Cache
  cacheTimeout: 300000, // 5 minutes
  enableCache: true,
  
  // UI Configuration
  defaultLanguage: 'en',
  supportedLanguages: ['en', 'ar'],
  itemsPerPage: 20,
  
  // Payment Gateways
  thawaniPublicKey: '',
  ompayPublicKey: ''
};
```

### Production Environment

**File**: `frontend/src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  
  // API Configuration
  apiUrl: 'https://api.3dstore.com/3dstore/api/v1',
  wsUrl: 'wss://api.3dstore.com/ws',
  uploadUrl: 'https://api.3dstore.com/3dstore/api/v1/upload',
  
  // File Upload
  maxFileSize: 104857600,
  supportedFormats: ['.stl', '.obj', '.3mf'],
  
  // Storage Keys
  tokenKey: 'auth_token',
  refreshTokenKey: 'refresh_token',
  userKey: 'current_user',
  
  // Feature Flags
  enableGoogleAuth: true,
  enableAppleAuth: true,
  enableTwitterAuth: true,
  enablePWA: true,
  enableOfflineMode: true,
  
  // Analytics
  googleAnalyticsId: 'UA-XXXXXXXXX-X',
  enableAnalytics: true,
  
  // Monitoring
  sentryDsn: 'https://xxxxx@sentry.io/xxxxx',
  enableSentry: true,
  
  // Cache
  cacheTimeout: 600000, // 10 minutes
  enableCache: true,
  
  // UI Configuration
  defaultLanguage: 'en',
  supportedLanguages: ['en', 'ar'],
  itemsPerPage: 20,
  
  // Payment Gateways
  thawaniPublicKey: 'your_thawani_public_key',
  ompayPublicKey: 'your_ompay_public_key'
};
```

---

## Environment-Specific Configuration

### Development

```bash
# Backend (.env)
FLASK_ENV=development
FLASK_DEBUG=True
DB_TYPE=sqlite
CACHE_TYPE=simple
LOG_LEVEL=DEBUG
```

### Staging

```bash
# Backend (.env.staging)
FLASK_ENV=staging
FLASK_DEBUG=False
DB_TYPE=postgresql
CACHE_TYPE=redis
LOG_LEVEL=INFO
SENTRY_ENVIRONMENT=staging
```

### Production

```bash
# Backend (.env.production)
FLASK_ENV=production
FLASK_DEBUG=False
DB_TYPE=postgresql
CACHE_TYPE=redis
LOG_LEVEL=WARNING
SENTRY_ENVIRONMENT=production
STORAGE_BACKEND=s3
```

---

## Docker Environment Variables

### Docker Compose

**File**: `docker-compose.yml`

```yaml
services:
  backend:
    environment:
      - FLASK_ENV=${FLASK_ENV:-production}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    env_file:
      - .env
  
  frontend:
    environment:
      - NODE_ENV=production
      - API_URL=${API_URL}
```

### Docker .env file

```bash
# Docker Environment
COMPOSE_PROJECT_NAME=3dstore

# Service Ports
BACKEND_PORT=5000
FRONTEND_PORT=4200
POSTGRES_PORT=5432
REDIS_PORT=6379

# Database
POSTGRES_USER=3dstore
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=store3d

# Redis
REDIS_PASSWORD=your_redis_password
```

---

## Environment Variable Best Practices

### 1. Security

- ✅ **Never commit `.env` files** to version control
- ✅ **Use `.env.example`** as template
- ✅ **Rotate secrets** regularly
- ✅ **Use strong random values** for keys
- ✅ **Encrypt sensitive values** in production
- ❌ **Don't hardcode** secrets in code
- ❌ **Don't expose** secrets in logs

### 2. Organization

- Group related variables together
- Use consistent naming conventions
- Comment complex configurations
- Document all variables
- Use defaults when appropriate

### 3. Validation

```python
# Backend validation
import os

def validate_env():
    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'DATABASE_URL'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")

# Call on startup
validate_env()
```

### 4. Documentation

- Document all variables in this file
- Include examples in `.env.example`
- Explain purpose and valid values
- Note production vs development differences

---

## Environment File Template

### `.env.example` (Backend)

```bash
# ========================================
# 3D Store Backend Environment Variables
# ========================================

# Database Configuration
DB_TYPE=postgresql
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DATABASE_NAME=store3d
DB_HOST=localhost:5432

# Application
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=change_this_to_a_random_secret_key
JWT_SECRET_KEY=change_this_to_a_random_jwt_key

# Cache
CACHE_ENABLED=True
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0

# File Storage
UPLOAD_FOLDER=./uploads
STORAGE_BACKEND=local

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Payment Gateways
THAWANI_API_KEY=your_thawani_key
OMPAY_API_KEY=your_ompay_key

# OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret

# Monitoring
SENTRY_DSN=your_sentry_dsn
```

---

## Loading Environment Variables

### Backend (Python)

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# With defaults
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'False') == 'True'
```

### Frontend (Angular)

```typescript
// Access environment variables
import { environment } from '../environments/environment';

const apiUrl = environment.apiUrl;
const maxFileSize = environment.maxFileSize;
```

---

## Troubleshooting

### Common Issues

**Issue**: Environment variables not loading

**Solution**:
```bash
# Check if .env file exists
ls -la .env

# Verify file permissions
chmod 600 .env

# Check variable names (no spaces)
# Correct: SECRET_KEY=value
# Wrong: SECRET_KEY = value
```

**Issue**: Docker not using environment variables

**Solution**:
```yaml
# docker-compose.yml
services:
  backend:
    env_file:
      - .env  # Add this line
```

---

## Additional Resources

- [12-Factor App Methodology](https://12factor.net/config)
- [Python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Environment Variables Best Practices](https://www.doppler.com/blog/environment-variables-best-practices)

---

**Last Updated**: January 2025  
**Version**: 1.0.0

