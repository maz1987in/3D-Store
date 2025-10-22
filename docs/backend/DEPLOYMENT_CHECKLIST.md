# Deployment Checklist

This checklist ensures all security and configuration requirements are met before deploying to production.

## Pre-Deployment Security Review

### 1. Environment Variables Configuration

- [ ] All secrets configured via environment variables (never hardcoded)
- [ ] `SECRET_KEY` generated using: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] `SECURITY_PASSWORD_SALT` generated using: `python -c "import secrets; print(secrets.token_hex(16))"`
- [ ] Database password is strong (minimum 16 characters, mixed case, numbers, symbols)
- [ ] Redis password is strong
- [ ] `.env` file is NOT committed to git (verify with `git status`)
- [ ] `.env.example` exists and is up-to-date (without sensitive values)

### 2. CORS Configuration

- [ ] `CORS_ORIGINS` is set to specific domain(s), NOT `*`
- [ ] Example: `CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`
- [ ] Test CORS from actual frontend domain

### 3. Database Security

- [ ] Database user has minimum required permissions
- [ ] Database is NOT accessible from public internet
- [ ] Connection uses SSL/TLS if available
- [ ] Connection pool settings are appropriate for load:
  - [ ] `DB_POOL_SIZE` (production: 50-100)
  - [ ] `DB_MAX_OVERFLOW` (production: 50-100)
  - [ ] `DB_POOL_RECYCLE` (3600 recommended)

### 4. Permission Decorators

**CRITICAL**: Verify all permission decorators are enabled

- [ ] Search for `#@permissions.has_permission` in codebase
- [ ] Expected: 0 results (all should be uncommented)
- [ ] Command to check: `grep -r "#@permissions" backend/app/`

**Affected modules to verify**:
- [ ] `app/users/routes.py`
- [ ] `app/transaction/routes.py`
- [ ] `app/supplier/routes.py`
- [ ] `app/store/routes.py`
- [ ] `app/staff/routes.py`
- [ ] `app/setting/routes.py`
- [ ] `app/inventory/routes.py`
- [ ] `app/expense/routes.py`
- [ ] `app/dashboard/routes.py`
- [ ] `app/customers/routes.py`
- [ ] `app/company/routes.py`
- [ ] `app/cart/routes.py`
- [ ] `app/branch/routes.py`
- [ ] All other modules in `app/`

### 5. Rate Limiting

- [ ] Rate limiting is enabled: `RATELIMIT_ENABLED=True`
- [ ] Authentication endpoints have strict limits
- [ ] Redis is configured for rate limit storage (production)
- [ ] Test rate limiting works with: `curl` or similar tool

### 6. HTTPS/TLS Configuration

- [ ] HTTPS is enabled (required for production)
- [ ] Valid SSL certificate is installed
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header is enabled
- [ ] Certificate auto-renewal is configured (Let's Encrypt, etc.)

### 7. Security Headers

Verify these headers are set (check in browser dev tools):
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY`
- [ ] `X-XSS-Protection: 1; mode=block`
- [ ] `Strict-Transport-Security: max-age=31536000` (HTTPS only)

### 8. Session Security

- [ ] Session cookies are secure (HTTPS only)
- [ ] Session cookies are httpOnly
- [ ] Session cookies have sameSite=Lax or Strict
- [ ] Session timeout is appropriate

### 9. Error Handling & Logging

- [ ] Debug mode is disabled: `FLASK_DEBUG=False`
- [ ] Error pages don't expose sensitive information
- [ ] Logging is configured: `LOG_LEVEL=INFO` or `WARNING`
- [ ] Sensitive data is NOT logged (passwords, tokens, etc.)
- [ ] Log files are rotated and have size limits
- [ ] Sentry or error tracking is configured (recommended)

### 10. File Upload Security

- [ ] File upload validation is enabled
- [ ] File size limits are enforced: `MAX_CONTENT_LENGTH=16777216` (16MB)
- [ ] File types are restricted
- [ ] MIME type validation is enabled
- [ ] Uploaded files are scanned (if applicable)
- [ ] Files are stored outside webroot or in cloud storage

## Docker Deployment

### 11. Docker Compose Configuration

- [ ] Environment variables set before running:
  ```bash
  export MYSQL_ROOT_PASSWORD="your_secure_password"
  export REDIS_PASSWORD="your_secure_password"
  export SECRET_KEY="your_generated_secret"
  export SECURITY_PASSWORD_SALT="your_generated_salt"
  ```
- [ ] NO hardcoded passwords in `docker-compose.yml`
- [ ] Docker networks are properly configured
- [ ] Volumes are configured for data persistence
- [ ] Resource limits are set (CPU, memory)

### 12. Docker Image Security

- [ ] Using official base images
- [ ] Images are regularly updated
- [ ] Running as non-root user
- [ ] Minimal image size (remove unnecessary packages)
- [ ] No secrets in image layers

## Database Setup

### 13. Database Migrations

- [ ] All migrations have been tested in staging
- [ ] Database backup taken before migration
- [ ] Migrations run successfully: `alembic upgrade head`
- [ ] Performance indexes are applied: `python scripts/apply_indexes.py`
- [ ] No migration conflicts

### 14. Initial Data

- [ ] Admin user is created
- [ ] Initial roles and permissions are set up
- [ ] Default settings are configured
- [ ] Test data is NOT in production database

## Application Configuration

### 15. Cache Configuration

If using Redis cache:
- [ ] `CACHE_ENABLED=True`
- [ ] `CACHE_TYPE=RedisCache`
- [ ] Redis is secured with password
- [ ] Redis is NOT accessible from public internet
- [ ] Cache TTLs are appropriate

### 16. Scheduler Configuration

If using scheduler:
- [ ] `SCHEDULER_ENABLED=True`
- [ ] Scheduler mode is appropriate (`redis` for production)
- [ ] Timezone is correct: `SCHEDULER_TIMEZONE=Asia/Muscat`
- [ ] Scheduled jobs are tested

### 17. Email Configuration

If sending emails:
- [ ] `MAIL_ENABLED=True`
- [ ] SMTP credentials are correct
- [ ] Test email sending works
- [ ] Email templates are tested
- [ ] SPF/DKIM records are configured (to prevent spam)

### 18. Payment Gateway Configuration

If using payments:
- [ ] Production API keys are used (not sandbox/test keys)
- [ ] Webhook URLs are configured
- [ ] Webhook signature verification is enabled
- [ ] Test transactions work
- [ ] Refund process is tested

## Testing & Quality Assurance

### 19. Testing

- [ ] All tests pass: `python -m pytest`
- [ ] Test coverage is at least 80%: `pytest --cov=app --cov-report=term`
- [ ] Integration tests pass
- [ ] API tests pass
- [ ] Load testing completed (if high traffic expected)

### 20. Code Quality

- [ ] Linting passes: `flake8 app/`
- [ ] Type checking passes: `mypy app/` (if configured)
- [ ] No security vulnerabilities: `safety check`
- [ ] Dependencies are up-to-date

## Monitoring & Observability

### 21. Health Checks

- [ ] Health endpoint responds: `curl https://yourdomain.com/health`
- [ ] Database health check works
- [ ] Cache health check works (if applicable)
- [ ] All critical services are monitored

### 22. Logging & Monitoring

- [ ] Centralized logging is configured
- [ ] Log aggregation is set up (ELK, Datadog, etc.)
- [ ] Error tracking is configured (Sentry, Rollbar, etc.)
- [ ] Uptime monitoring is configured
- [ ] Performance monitoring is configured

### 23. Alerts

- [ ] Critical error alerts are configured
- [ ] High CPU/memory usage alerts
- [ ] Disk space alerts
- [ ] Database connection alerts
- [ ] Rate limit alerts
- [ ] Alert recipients are correct

## Backup & Recovery

### 24. Backup Strategy

- [ ] Database backups are automated
- [ ] Backup frequency is appropriate (daily minimum)
- [ ] Backups are tested (restore test)
- [ ] Backups are stored off-site
- [ ] Backup retention policy is defined
- [ ] File upload backups (if applicable)

### 25. Disaster Recovery

- [ ] Recovery procedure is documented
- [ ] RTO (Recovery Time Objective) is defined
- [ ] RPO (Recovery Point Objective) is defined
- [ ] DR plan has been tested
- [ ] Team knows the recovery process

## Documentation

### 26. Documentation Review

- [ ] API documentation is up-to-date
- [ ] README is current
- [ ] Security policy is documented (`SECURITY.md`)
- [ ] Environment variables are documented
- [ ] Deployment process is documented
- [ ] Troubleshooting guide exists

## Final Checks

### 27. Pre-Go-Live Checklist

- [ ] All above items checked ✓
- [ ] Staging environment matches production
- [ ] Full system test in staging
- [ ] Performance test passed
- [ ] Security audit completed
- [ ] Team is trained on new deployment
- [ ] Rollback plan is ready
- [ ] Communication plan for downtime (if any)

### 28. Post-Deployment

- [ ] Monitor application for first 24 hours
- [ ] Check error logs regularly
- [ ] Verify all features work
- [ ] Monitor performance metrics
- [ ] Check database performance
- [ ] Verify backup ran successfully
- [ ] User acceptance testing
- [ ] Document any issues found

## Security Incident Response

### 29. Incident Response Plan

- [ ] Security incident response team identified
- [ ] Incident response procedure documented
- [ ] Contact information for team members
- [ ] Process for security patching
- [ ] Process for notifying users of breaches

## Compliance & Legal

### 30. Compliance Checks

- [ ] GDPR compliance reviewed (if applicable)
- [ ] Data retention policy implemented
- [ ] Privacy policy is current
- [ ] Terms of service are current
- [ ] Cookie consent implemented (if needed)

---

## Quick Command Reference

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate SECURITY_PASSWORD_SALT
python -c "import secrets; print(secrets.token_hex(16))"

# Check for commented permission decorators
grep -r "#@permissions" backend/app/

# Run tests with coverage
python -m pytest --cov=app --cov-report=term

# Check for security vulnerabilities
pip install safety
safety check

# Run database migrations
alembic upgrade head

# Apply performance indexes
python scripts/apply_indexes.py

# Test health endpoint
curl https://yourdomain.com/health
```

---

## Emergency Contacts

- **DevOps Team**: [contact info]
- **Security Team**: [contact info]
- **Database Admin**: [contact info]
- **On-Call Engineer**: [contact info]

---

## Rollback Procedure

If issues are discovered after deployment:

1. **Immediate Actions**:
   - Put application in maintenance mode
   - Stop accepting new requests

2. **Database Rollback** (if migrations were run):
   ```bash
   alembic downgrade -1
   ```

3. **Application Rollback**:
   - Revert to previous Docker image tag
   - Or deploy previous code version

4. **Verification**:
   - Test critical functionality
   - Check error logs
   - Verify database integrity

5. **Communication**:
   - Notify stakeholders
   - Update status page
   - Document the issue

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Verified By**: _____________
**Sign-Off**: _____________


