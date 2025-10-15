# AI Resume Analyzer - Setup Guide

This guide will help you set up the AI Resume Analyzer with Google OAuth authentication and email delivery features.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Cloud Console account (for OAuth)
- SendGrid account (for email delivery)
- Gemini API key (for AI features)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd AI-RESUME-ANALYZER
```

### 2. Environment Configuration

Copy the environment template and configure your variables:

```bash
cp backend/env_template.txt .env
```

Edit `.env` with your actual values:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_optimizer

# JWT Configuration (CHANGE THESE IN PRODUCTION!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
SECRET_KEY=your-secret-key-for-sessions

# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/callback

# Email Configuration (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key

# Rate Limiting
RATELIMIT_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

## 🔧 Detailed Setup Instructions

### Google OAuth Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Google+ API

2. **Create OAuth 2.0 Credentials**
   - Go to "Credentials" in the API & Services section
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:5000/api/auth/callback` (development)
     - `https://yourdomain.com/api/auth/callback` (production)

3. **Configure Environment Variables**
   ```env
   GOOGLE_CLIENT_ID=your-client-id-from-console
   GOOGLE_CLIENT_SECRET=your-client-secret-from-console
   ```

### SendGrid Email Setup

1. **Create SendGrid Account**
   - Sign up at [SendGrid](https://sendgrid.com/)
   - Verify your account and sender identity

2. **Generate API Key**
   - Go to Settings → API Keys
   - Create a new API key with "Full Access" permissions
   - Copy the API key

3. **Configure Environment Variables**
   ```env
   SENDGRID_API_KEY=your-sendgrid-api-key
   FROM_EMAIL=noreply@yourdomain.com
   ```

### Gemini AI Setup

1. **Get Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key

2. **Configure Environment Variable**
   ```env
   GEMINI_API_KEY=your-gemini-api-key
   ```

## 🐳 Docker Setup

### Development Environment

```bash
# Start the development environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Environment

1. **Update docker-compose.yml** with production values:
   ```yaml
   environment:
     DATABASE_URL: ${DATABASE_URL}
     JWT_SECRET_KEY: ${JWT_SECRET_KEY}
     SECRET_KEY: ${SECRET_KEY}
     GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
     GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET}
     SENDGRID_API_KEY: ${SENDGRID_API_KEY}
     FROM_EMAIL: ${FROM_EMAIL}
     GEMINI_API_KEY: ${GEMINI_API_KEY}
   ```

2. **Set production environment variables** on your hosting platform

## 🧪 Testing the Setup

### 1. Test Google OAuth

1. Start the application: `docker-compose up -d`
2. Open `http://localhost:3000`
3. Click "Sign Up" or "Sign In"
4. Click "Continue with Google"
5. Complete Google authentication
6. Verify you're redirected back to the dashboard

### 2. Test Email Delivery

1. Sign in to your account
2. Upload a resume and analyze it
3. Check your email for the analysis results
4. Try generating AI feedback, optimized resume, or cover letter
5. Verify emails are received for each feature

### 3. Test Manual Email Resend

1. Go to any analysis result page
2. Click "Resend Email" button
3. Verify the email is received

## 🔒 Security Considerations

### Environment Variables

- **Never commit `.env` files** to version control
- Use strong, unique secrets for JWT_SECRET_KEY and SECRET_KEY
- Rotate API keys regularly
- Use different keys for development and production

### Production Deployment

1. **Use HTTPS** for all OAuth redirects
2. **Set secure JWT secrets** (at least 32 characters)
3. **Configure CORS** properly for your domain
4. **Use environment-specific database URLs**
5. **Enable rate limiting** in production

### Database Security

- Use strong database passwords
- Enable SSL connections in production
- Regular database backups
- Monitor for suspicious activity

## 🐛 Troubleshooting

### Common Issues

#### Google OAuth Not Working

**Error**: "redirect_uri_mismatch"
- **Solution**: Ensure the redirect URI in Google Console matches exactly: `http://localhost:5000/api/auth/callback`

**Error**: "invalid_client"
- **Solution**: Check that GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct

#### Email Not Sending

**Error**: "SendGrid API key invalid"
- **Solution**: Verify SENDGRID_API_KEY is correct and has proper permissions

**Error**: "Email not received"
- **Solution**: Check spam folder, verify FROM_EMAIL is authenticated in SendGrid

#### Database Connection Issues

**Error**: "Database connection failed"
- **Solution**: Ensure PostgreSQL container is running and DATABASE_URL is correct

### Debug Mode

Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
FLASK_ENV=development
```

View logs:
```bash
docker-compose logs -f backend
```

## 📱 Frontend Configuration

The frontend automatically detects the backend URL. For production:

1. Update `API_URL` in `frontend/src/App.jsx`
2. Set `FRONTEND_URL` environment variable in backend
3. Update CORS origins in `backend/app.py`

## 🔄 Database Migrations

When updating the User model:

```bash
# Access the backend container
docker-compose exec backend bash

# Run migrations (if using Flask-Migrate)
flask db upgrade

# Or recreate tables (development only)
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## 📊 Monitoring and Logs

### Application Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs postgres
```

### Email Delivery Monitoring

- Check SendGrid dashboard for delivery statistics
- Monitor bounce rates and spam reports
- Set up webhook endpoints for delivery events

## 🚀 Deployment Checklist

- [ ] All environment variables configured
- [ ] Google OAuth credentials set up
- [ ] SendGrid API key configured
- [ ] Gemini API key set up
- [ ] Database URL configured for production
- [ ] HTTPS enabled for OAuth redirects
- [ ] CORS origins updated for production domain
- [ ] JWT secrets are strong and unique
- [ ] Rate limiting enabled
- [ ] Error monitoring set up
- [ ] Email delivery tested
- [ ] Google OAuth flow tested

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f backend`
2. Verify all environment variables are set
3. Test each service individually (OAuth, Email, AI)
4. Check the troubleshooting section above

For additional help, refer to the main README.md file.
