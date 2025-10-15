# ResumeAnalyzer AI v2.0 - Production-Ready Resume Analysis Platform

A comprehensive, production-ready AI-powered resume analysis platform built with Flask and React. This version includes enterprise-grade features, security, testing, and deployment capabilities.

## 🚀 Features

### Backend (Flask/Python)
- **Secure Authentication**: JWT-based auth with bcrypt password hashing
- **AI-Powered Analysis**: Advanced NLP with spaCy and scikit-learn
- **Gemini AI Integration**: Personalized feedback and resume optimization
- **Database Management**: SQLAlchemy with Alembic migrations
- **Comprehensive Testing**: 80%+ code coverage with pytest
- **Production Security**: CORS, rate limiting, input validation
- **Structured Logging**: JSON logging with request tracking
- **API Documentation**: OpenAPI/Swagger integration ready

### Frontend (React)
- **Modern UI/UX**: Beautiful, responsive design with Tailwind CSS
- **State Management**: Context API with custom hooks
- **Form Validation**: Comprehensive client-side validation
- **Error Handling**: Global error boundary and user-friendly messages
- **File Upload**: Drag-and-drop with validation
- **Real-time Feedback**: Loading states and progress indicators
- **Security**: Input sanitization and XSS protection

## 🏗️ Architecture

```
├── backend/
│   ├── app_v2.py              # Main Flask application
│   ├── config.py              # Environment-specific configurations
│   ├── models.py              # SQLAlchemy models with Marshmallow schemas
│   ├── errors.py              # Global error handling and logging
│   ├── validators.py          # Input validation utilities
│   ├── ai_processor_v2.py     # Enhanced AI processing with caching
│   ├── gemini_service_v2.py   # Gemini AI service with retry logic
│   ├── routes/                # API route blueprints
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── analysis.py       # Resume analysis endpoints
│   │   ├── dashboard.py      # Dashboard and insights
│   │   └── health.py         # Health check endpoints
│   ├── tests/                 # Comprehensive test suite
│   ├── migrations/            # Alembic database migrations
│   └── requirements.txt       # Production dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── contexts/          # React contexts (Auth, etc.)
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API service layer
│   │   ├── utils/             # Utility functions
│   │   └── config/            # Application configuration
│   └── package.json           # Updated with testing and linting
└── .github/workflows/         # CI/CD pipeline
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis (optional, for caching)

### Backend Setup

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database:**
```bash
# Set up PostgreSQL database
createdb resume_optimizer

# Run migrations
alembic upgrade head
```

6. **Run tests:**
```bash
pytest --cov=. --cov-report=html
```

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
cp env.example .env.local
# Edit .env.local with your API URL
```

4. **Run development server:**
```bash
npm start
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/resume_optimizer
DEV_DATABASE_URL=postgresql://user:password@localhost:5432/resume_optimizer_dev
TEST_DATABASE_URL=sqlite:///:memory:

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# AI Services
GEMINI_API_KEY=your-gemini-api-key

# Environment
FLASK_ENV=development
LOG_LEVEL=INFO

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379/0
```

#### Frontend (.env.local)
```bash
REACT_APP_API_URL=http://localhost:5000/api/v1
REACT_APP_ENV=development
REACT_APP_ENABLE_DEBUG=false
```

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_auth.py -v
pytest tests/test_analysis.py -v

# Run with coverage threshold
pytest --cov=. --cov-fail-under=80
```

### Frontend Testing
```bash
cd frontend

# Run tests with coverage
npm run test:coverage

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format
```

## 🚀 Deployment

### Docker Deployment

1. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

2. **Production deployment:**
```bash
# Set production environment variables
export FLASK_ENV=production
export DATABASE_URL=your-production-db-url

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app_v2:app
```

### Manual Deployment

1. **Backend deployment:**
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
alembic upgrade head
gunicorn --bind 0.0.0.0:5000 app_v2:app
```

2. **Frontend deployment:**
```bash
cd frontend
npm install
npm run build
# Serve build/ directory with your web server
```

## 📊 Monitoring & Logging

### Structured Logging
- JSON-formatted logs with request IDs
- Error tracking and performance monitoring
- Configurable log levels per environment

### Health Checks
- `/api/v1/health` - Basic health check
- `/api/v1/health/detailed` - Detailed system status

### Metrics
- Request/response times
- Error rates
- Database connection status
- AI service availability

## 🔒 Security Features

### Backend Security
- JWT token expiration and validation
- CORS configuration with domain whitelist
- Input validation and sanitization
- Rate limiting per endpoint
- File upload security (MIME type validation)
- SQL injection protection
- XSS prevention

### Frontend Security
- Input sanitization
- XSS protection
- Secure token storage
- HTTPS enforcement in production

## 🧩 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/change-password` - Change password

### Analysis Endpoints
- `POST /api/v1/analysis/analyze` - Analyze resume
- `GET /api/v1/analysis/analyses` - Get user analyses
- `GET /api/v1/analysis/analyses/{id}` - Get specific analysis
- `POST /api/v1/analysis/analyses/{id}/feedback` - Generate AI feedback
- `POST /api/v1/analysis/analyses/{id}/optimize` - Optimize resume
- `POST /api/v1/analysis/analyses/{id}/cover-letter` - Generate cover letter
- `DELETE /api/v1/analysis/analyses/{id}` - Delete analysis

### Dashboard Endpoints
- `GET /api/v1/dashboard/stats` - Get dashboard statistics
- `GET /api/v1/dashboard/insights` - Get personalized insights

## 🔄 CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow:

1. **Backend Tests**: Python tests with coverage
2. **Frontend Tests**: React tests and linting
3. **Security Scanning**: Bandit and Safety checks
4. **Integration Tests**: End-to-end testing
5. **Deployment**: Automated staging and production deployment

## 📈 Performance Optimizations

### Backend
- AI processing result caching
- Database query optimization
- Connection pooling
- Async file processing

### Frontend
- Code splitting and lazy loading
- Image optimization
- Bundle size optimization
- Caching strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test files for usage examples

## 🔄 Migration from v1.0

If migrating from v1.0:

1. **Backup your database**
2. **Update environment variables**
3. **Run database migrations**: `alembic upgrade head`
4. **Update frontend API calls** to use new endpoints
5. **Test thoroughly** before deploying to production

## 🎯 Roadmap

- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Enterprise SSO integration
- [ ] Advanced AI models integration

---

**Built with ❤️ by the ResumeAnalyzer AI Team**
