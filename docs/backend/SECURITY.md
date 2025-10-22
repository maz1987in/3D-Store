# Security Policy

## Security Best Practices

### Environment Configuration

**CRITICAL**: Never commit sensitive data to version control.

1. **Always use environment variables for secrets**:
   - `SECRET_KEY`
   - `SECURITY_PASSWORD_SALT`
   - Database passwords
   - API keys
   - Redis passwords

2. **Copy `.env.example` to `.env` and configure with real values**:
   ```bash
   cp .env.example .env
   # Edit .env with your secure values
   ```

3. **Generate strong secrets**:
   ```python
   # Generate SECRET_KEY
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Generate SECURITY_PASSWORD_SALT
   python -c "import secrets; print(secrets.token_hex(16))"
   ```

### Docker Security

When using Docker Compose, set environment variables before running:

```bash
# Set required secrets
export MYSQL_ROOT_PASSWORD="your_secure_mysql_password"
export REDIS_PASSWORD="your_secure_redis_password"
export SECRET_KEY="your_generated_secret_key"
export SECURITY_PASSWORD_SALT="your_generated_salt"

# Run docker-compose
docker-compose up -d
```

**Never** use default passwords like `password` or `changeme` in production.

### Authentication & Authorization

1. **All protected endpoints MUST use permission decorators**:
   ```python
   @route('/endpoint', methods=['GET'])
   @permissions.has_permission(['resource.action'])
   def protected_endpoint():
       pass
   ```

2. **JWT tokens must use explicit algorithms**:
   ```python
   # Correct
   jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
   
   # Incorrect (security risk)
   jwt.decode(token, SECRET_KEY, "HS256")
   ```

3. **Rate limiting on authentication endpoints**:
   - Login: 5 attempts per minute, 20 per hour
   - Signup: 3 attempts per minute, 10 per hour
   - Password reset: 3 attempts per 15 minutes

### CORS Configuration

**Production**: Restrict CORS to specific domains:
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Development**: Use specific localhost URLs:
```bash
CORS_ORIGINS=http://localhost:4200
```

**Never** use `CORS_ORIGINS=*` in production.

### Password Policy

Passwords must meet the following requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (@#$%^&+=)

### Database Security

1. **Connection pooling** - Use appropriate pool sizes:
   - Development: `DB_POOL_SIZE=10`
   - Production: `DB_POOL_SIZE=50` (adjust based on load)

2. **Connection recycling** - Prevent stale connections:
   ```bash
   DB_POOL_RECYCLE=3600  # 1 hour
   ```

3. **Use parameterized queries** - Never concatenate SQL strings:
   ```python
   # Correct (using SQLAlchemy ORM)
   User.query.filter(User.username == username).first()
   
   # Incorrect (SQL injection risk)
   session.execute(f"SELECT * FROM users WHERE username = '{username}'")
   ```

### Input Validation

1. **All user input must be validated** using Marshmallow schemas:
   ```python
   from marshmallow import Schema, fields, validate
   
   class UserInputSchema(Schema):
       email = fields.Email(required=True)
       username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
   ```

2. **Sanitize output** to prevent XSS attacks (handled by Flask's default escaping)

### File Upload Security

1. **Validate file types**:
   - Check file extensions
   - Verify MIME types
   - Use `python-magic` for content verification

2. **Limit file sizes**:
   ```bash
   MAX_CONTENT_LENGTH=16777216  # 16MB
   ```

3. **Store uploads outside webroot** or use cloud storage

### Logging & Monitoring

1. **Never log sensitive data**:
   - Passwords
   - Tokens
   - API keys
   - Credit card numbers
   - Personal identification numbers

2. **Log security events**:
   - Failed login attempts
   - Permission denials
   - Suspicious patterns
   - Rate limit violations

3. **Enable Sentry for error tracking** (optional):
   ```bash
   SENTRY=True
   SENTRY_DSN=your_sentry_dsn
   ```

### HTTPS/TLS

**Production requirements**:
- Always use HTTPS
- Enable HSTS headers
- Use strong TLS versions (1.2+)
- Configure secure session cookies

### Security Headers

The application automatically adds security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000` (in production)

### Dependency Management

1. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

2. **Scan for vulnerabilities**:
   ```bash
   pip install safety
   safety check
   ```

3. **Use dependency pinning** in `requirements.txt`

### Security Checklist for Deployment

- [ ] All secrets configured via environment variables
- [ ] No hardcoded credentials in code
- [ ] `.env` file not committed to git
- [ ] Strong passwords generated for all services
- [ ] CORS restricted to specific domains
- [ ] HTTPS enabled with valid certificate
- [ ] Database credentials secured
- [ ] Redis password set
- [ ] Permission decorators enabled on all protected routes
- [ ] Rate limiting configured
- [ ] File upload validation enabled
- [ ] Security headers configured
- [ ] Error tracking configured (Sentry)
- [ ] Logging configured (no sensitive data)
- [ ] Backup strategy in place
- [ ] Monitoring alerts configured

## Reporting a Vulnerability

If you discover a security vulnerability, please email security@yourdomain.com with:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if available)

**Do not** create public GitHub issues for security vulnerabilities.

We will respond within 48 hours and provide updates on the fix timeline.

## Security Updates

This project follows semantic versioning. Security updates are released as:
- **Patch versions** (x.x.X) for minor security fixes
- **Minor versions** (x.X.x) for moderate security improvements
- **Major versions** (X.x.x) may include breaking changes for critical security fixes

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Considerations](https://flask.palletsprojects.com/en/2.0.x/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)

