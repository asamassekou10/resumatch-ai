# 🌐 Production Deployment Guide

This guide covers deploying your AI Resume Optimizer to production environments.

## 🎯 Deployment Options

1. **Heroku** - Easiest, free tier available
2. **AWS** - Most flexible, scalable
3. **DigitalOcean** - Simple, affordable
4. **Render** - Modern, easy to use
5. **Railway** - Simple deployment

## 🚀 Option 1: Deploy to Heroku

### Prerequisites
- Heroku account (free at [heroku.com](https://heroku.com))
- Heroku CLI installed

### Step-by-Step Deployment

#### 1. Prepare Your Code

Create `Procfile` in backend directory:
```
web: gunicorn app:app
```

Create `runtime.txt`:
```
python-3.11.5
```

Update `requirements.txt` to include:
```
gunicorn==21.2.0
```

#### 2. Initialize Git Repository

```bash
cd backend
git init
git add .
git commit -m "Initial commit"
```

#### 3. Create Heroku App

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-resume-optimizer-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set JWT_SECRET_KEY=$(openssl rand -hex 32)
heroku config:set FLASK_ENV=production
```

#### 4. Deploy

```bash
git push heroku main
```

#### 5. Download spaCy Model

```bash
heroku run python -m spacy download en_core_web_sm
```

#### 6. Verify Deployment

```bash
heroku open
# Or visit: your-resume-optimizer-api.herokuapp.com/api/health
```

### Deploy Frontend to Netlify

1. **Build frontend:**
```bash
cd frontend
npm run build
```

2. **Update API_URL** in production build:

Create `.env.production`:
```
REACT_APP_API_URL=https://your-resume-optimizer-api.herokuapp.com/api
```

Update `App.jsx`:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
```

3. **Deploy to Netlify:**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=build
```

## 🔧 Option 2: Deploy to AWS

### Architecture
- **EC2**: Application server
- **RDS**: PostgreSQL database
- **S3**: Static frontend hosting
- **CloudFront**: CDN for frontend

### Backend Deployment (EC2)

#### 1. Launch EC2 Instance

```bash
# Amazon Linux 2 or Ubuntu 22.04
# Instance type: t2.micro (free tier)
# Security group: Allow ports 22, 80, 443, 5000
```

#### 2. Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y  # Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Docker
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

#### 3. Clone and Deploy

```bash
git clone your-repo-url
cd ai-resume-optimizer/backend
docker-compose up -d --build
```

#### 4. Setup RDS PostgreSQL

1. Create RDS PostgreSQL instance
2. Note connection string
3. Update `docker-compose.yml`:
```yaml
environment:
  DATABASE_URL: postgresql://user:pass@rds-endpoint:5432/dbname
```

#### 5. Configure Domain and SSL

```bash
# Install Nginx
sudo yum install nginx -y

# Configure reverse proxy
sudo nano /etc/nginx/conf.d/app.conf
```

Add:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Get SSL certificate
sudo yum install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Frontend Deployment (S3 + CloudFront)

#### 1. Build Frontend

```bash
cd frontend
npm run build
```

#### 2. Create S3 Bucket

```bash
aws s3 mb s3://your-resume-optimizer
aws s3 sync build/ s3://your-resume-optimizer
```

#### 3. Configure S3 for Static Website

Enable static website hosting in S3 console.

#### 4. Create CloudFront Distribution

- Origin: S3 bucket
- Default root object: index.html
- SSL certificate: Request via ACM

## 🐳 Option 3: Deploy to DigitalOcean

### Using Docker Droplet

#### 1. Create Droplet

- Choose "Docker" from Marketplace
- Size: $6/month Basic droplet
- Add SSH key

#### 2. Connect and Deploy

```bash
ssh root@your-droplet-ip

# Clone repository
git clone your-repo-url
cd ai-resume-optimizer/backend

# Create production docker-compose
cp docker-compose.yml docker-compose.prod.yml
```

Edit `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: resume_optimizer
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  backend:
    build: .
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/resume_optimizer
      JWT_SECRET_KEY: ${JWT_SECRET}
    ports:
      - "80:5000"
    depends_on:
      - postgres
    restart: always

volumes:
  postgres_data:
```

#### 3. Set Environment Variables

```bash
# Create .env file
nano .env
```

Add:
```
DB_USER=your_user
DB_PASSWORD=strong_password_here
JWT_SECRET=your_secret_key_here
```

#### 4. Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

#### 5. Setup Domain

Point your domain A record to droplet IP.

### Deploy Frontend to DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build:
   - Build command: `npm run build`
   - Output directory: `build`
3. Add environment variable:
   - `REACT_APP_API_URL=https://api.yourdomain.com`
4. Deploy

## 🎨 Option 4: Deploy to Render

### Backend Deployment

1. **Sign up** at [render.com](https://render.com)

2. **Create PostgreSQL database:**
   - New → PostgreSQL
   - Name: resume-optimizer-db
   - Copy connection string

3. **Create Web Service:**
   - New → Web Service
   - Connect repository
   - Build command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - Start command: `gunicorn app:app`

4. **Add Environment Variables:**
   - `DATABASE_URL`: (from PostgreSQL)
   - `JWT_SECRET_KEY`: (generate with `openssl rand -hex 32`)

5. **Deploy** - Automatic from Git pushes

### Frontend Deployment

1. **Create Static Site:**
   - New → Static Site
   - Connect frontend repository
   - Build command: `npm run build`
   - Publish directory: `build`

2. **Add Environment Variable:**
   - `REACT_APP_API_URL`: Your backend URL

## 🔒 Security Best Practices

### 1. Environment Variables

Never commit secrets to Git:

```bash
# Use environment variables
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL="postgresql://..."
```

### 2. HTTPS/SSL

Always use HTTPS in production:

```python
# In app.py for Heroku
from flask_talisman import Talisman

if os.getenv('FLASK_ENV') == 'production':
    Talisman(app, content_security_policy=None)
```

### 3. CORS Configuration

```python
# Update CORS for production
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 4. Rate Limiting

Add to `requirements.txt`:
```
Flask-Limiter==3.5.0
```

In `app.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per hour")
@jwt_required()
def analyze_resume():
    # ...
```

### 5. Input Validation

```python
from werkzeug.utils import secure_filename

# Validate file uploads
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/analyze', methods=['POST'])
@jwt_required()
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'Resume file required'}), 400
    
    file = request.files['resume']
    
    # Validate file
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    if len(file.read()) > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large'}), 400
    
    file.seek(0)  # Reset file pointer after reading
    # Continue with processing...
```

### 6. Database Security

```python
# Use connection pooling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

# Enable SSL for database in production
if os.getenv('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_ENGINE_OPTIONS']['connect_args'] = {
        'sslmode': 'require'
    }
```

## 📊 Monitoring and Logging

### Setup Application Monitoring

#### 1. Add Logging

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'app.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')
```

#### 2. Track Errors

```python
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f'Unhandled Exception: {str(e)}')
    return jsonify({'error': 'An unexpected error occurred'}), 500
```

#### 3. Use Monitoring Services

**Sentry for Error Tracking:**

```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )
```

**New Relic for Performance Monitoring:**

```bash
pip install newrelic
newrelic-admin generate-config LICENSE_KEY newrelic.ini
```

Run with:
```bash
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn app:app
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          python -m spacy download en_core_web_sm
      
      - name: Run tests
        run: |
          cd backend
          python -m pytest tests/

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.14
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "your-resume-optimizer-api"
          heroku_email: "your@email.com"
          appdir: "backend"

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Frontend
        run: |
          cd frontend
          npm install
          npm run build
        env:
          REACT_APP_API_URL: ${{secrets.API_URL}}
      
      - name: Deploy to Netlify
        uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=frontend/build
        env:
          NETLIFY_SITE_ID: ${{secrets.NETLIFY_SITE_ID}}
          NETLIFY_AUTH_TOKEN: ${{secrets.NETLIFY_AUTH_TOKEN}}
```

## 📈 Performance Optimization

### 1. Database Optimization

Add indexes:

```python
class Analysis(db.Model):
    # ... existing fields ...
    
    # Add indexes for common queries
    __table_args__ = (
        db.Index('idx_user_created', 'user_id', 'created_at'),
        db.Index('idx_match_score', 'match_score'),
    )
```

### 2. Caching

Add Redis caching:

```bash
pip install redis flask-caching
```

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
})

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_dashboard_stats():
    # ... existing code ...
```

### 3. Load Balancing

Nginx configuration for multiple backend instances:

```nginx
upstream backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. CDN for Frontend

Use CloudFlare or AWS CloudFront:
- Enable caching for static assets
- Enable compression (Gzip/Brotli)
- Minify JavaScript and CSS

## 🔍 Health Checks

Add comprehensive health check:

```python
@app.route('/api/health', methods=['GET'])
def health_check():
    health = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }
    
    # Check database
    try:
        db.session.execute('SELECT 1')
        health['database'] = 'connected'
    except Exception as e:
        health['database'] = 'disconnected'
        health['status'] = 'unhealthy'
        health['error'] = str(e)
    
    # Check spaCy model
    try:
        if nlp:
            health['nlp_model'] = 'loaded'
        else:
            health['nlp_model'] = 'not_loaded'
    except:
        health['nlp_model'] = 'error'
    
    status_code = 200 if health['status'] == 'healthy' else 503
    return jsonify(health), status_code
```

## 📝 Environment Configuration

### Production Environment Variables Checklist

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET_KEY=your-super-secret-key-here

# Optional but recommended
FLASK_ENV=production
REDIS_URL=redis://host:6379/0
SENTRY_DSN=https://...@sentry.io/...
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (if implementing notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your-app-password

# Analytics (optional)
GOOGLE_ANALYTICS_ID=UA-XXXXX-Y
```

## 🚨 Disaster Recovery

### 1. Database Backups

**Heroku:**
```bash
# Automatic backups (paid plans)
heroku pg:backups:schedule --at '02:00 America/Los_Angeles'

# Manual backup
heroku pg:backups:capture

# Download backup
heroku pg:backups:download
```

**AWS RDS:**
- Enable automated backups (retention: 7-35 days)
- Take manual snapshots before major changes

**DigitalOcean:**
```bash
# Automated backups via cron
0 2 * * * docker exec postgres pg_dump -U user dbname > /backups/$(date +\%Y\%m\%d).sql
```

### 2. Application Backup

```bash
# Backup application code
git push --all backup-repo

# Backup environment variables
heroku config -s > .env.backup

# Backup uploaded files (if storing locally)
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### 3. Rollback Plan

**Heroku:**
```bash
# Rollback to previous release
heroku releases
heroku rollback v123
```

**Docker:**
```bash
# Keep previous image
docker tag backend:latest backend:previous
docker-compose up -d --no-deps backend

# Rollback
docker tag backend:previous backend:latest
docker-compose restart backend
```

## 📊 Post-Deployment Checklist

- [ ] SSL certificate is active and valid
- [ ] All environment variables are set
- [ ] Database migrations completed
- [ ] Health check endpoint returns 200
- [ ] Can register new user
- [ ] Can login with test account
- [ ] Can analyze resume successfully
- [ ] Dashboard displays correctly
- [ ] Email notifications work (if implemented)
- [ ] Error tracking is configured
- [ ] Monitoring is active
- [ ] Backups are scheduled
- [ ] Domain DNS is configured correctly
- [ ] CORS is configured for production domain
- [ ] Rate limiting is active
- [ ] Logs are being collected
- [ ] Performance metrics are tracked

## 🎯 Cost Estimates

### Heroku (Recommended for Students)
- **Hobby tier:** $7/month (backend) + $5/month (database)
- **Frontend (Netlify):** Free
- **Total:** ~$12/month

### AWS
- **EC2 t2.micro:** Free tier (12 months)
- **RDS t2.micro:** Free tier (12 months)
- **S3 + CloudFront:** ~$1-5/month
- **Total:** $0-5/month (first year)

### DigitalOcean
- **Basic Droplet:** $6/month
- **Managed Database:** $15/month
- **App Platform (frontend):** Free
- **Total:** ~$21/month

### Render
- **Free tier:** $0/month (with limitations)
- **Starter tier:** $7/month (backend) + $7/month (database)
- **Total:** $0-14/month

## 📱 Mobile Considerations

If adding mobile app later:

1. **Expose API** properly with versioning:
```python
@app.route('/api/v1/analyze', methods=['POST'])
```

2. **Add API documentation** (Swagger/OpenAPI)

3. **Implement refresh tokens** for better security

4. **Add push notifications** capability

## 🎓 Academic Submission

For your project submission:

1. **Live Demo URL:** https://your-app.com
2. **API Documentation:** https://your-app.com/api/docs
3. **Source Code:** GitHub repository link
4. **Demo Video:** Screen recording showing features
5. **Test Credentials:**
   - Email: demo@example.com
   - Password: (provide in submission)

## 📚 Additional Resources

- [Heroku Dev Center](https://devcenter.heroku.com/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [React Deployment](https://create-react-app.dev/docs/deployment/)

## 🎉 You're Production Ready!

Follow this guide to deploy your AI Resume Optimizer to production. Remember:

- Start with Heroku for simplicity
- Add monitoring from day one
- Implement backups immediately
- Test thoroughly before going live
- Monitor performance and errors
- Scale as needed

Good luck with your deployment! 🚀