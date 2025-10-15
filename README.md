# AI Resume Optimizer & Career Dashboard

A full-stack web application that helps job seekers optimize their resumes for specific job opportunities using AI-powered analysis.

## 🚀 Features

- **Resume Analysis**: Upload your resume and get a match score against job descriptions
- **Keyword Extraction**: Identify which keywords are present and missing from your resume
- **Career Dashboard**: Track your application history and progress over time
- **Skill Gap Analysis**: Visualize the most commonly requested skills you're missing
- **Google OAuth Authentication**: Sign in with Google for quick and secure access
- **Email Delivery**: Automatically receive analysis results, AI feedback, and generated content via email
- **AI-Powered Enhancement**: Get personalized feedback, optimized resume versions, and tailored cover letters
- **Secure Authentication**: User accounts with JWT-based authentication and password hashing
- **Resume Version Management**: Store and compare multiple resume versions

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or use Docker)
- Docker & Docker Compose (recommended for easy setup)

## 🛠️ Installation

### Option 1: Docker Setup (Recommended)

1. **Clone and setup project structure**:
```bash
mkdir ai-resume-optimizer
cd ai-resume-optimizer

# Create backend directory
mkdir backend
cd backend
```

2. **Create the following files in the `backend` directory**:
   - `app.py` - Flask backend API
   - `ai_processor.py` - AI processing engine
   - `requirements.txt` - Python dependencies
   - `Dockerfile` - Docker configuration
   - `docker-compose.yml` - Docker services

3. **Start the application**:
```bash
docker-compose up --build
```

The backend will be running at `http://localhost:5000`

### Option 2: Manual Setup

#### Backend Setup

1. **Install Python dependencies**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. **Setup PostgreSQL database**:
```bash
createdb resume_optimizer
```

3. **Set environment variables**:
```bash
export DATABASE_URL="postgresql://localhost/resume_optimizer"
export JWT_SECRET_KEY="your-secret-key-here"
```

4. **Run the backend**:
```bash
python app.py
```

#### Frontend Setup

1. **Create React app**:
```bash
cd ..
npx create-react-app frontend
cd frontend
```

2. **Install dependencies**:
```bash
npm install recharts
```

3. **Replace `src/App.jsx` with the provided React component**

4. **Update API URL** in `App.jsx` if needed:
```javascript
const API_URL = 'http://localhost:5000/api';
```

5. **Run the frontend**:
```bash
npm start
```

The frontend will open at `http://localhost:3000`

## 📁 Project Structure

```
ai-resume-optimizer/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── ai_processor.py        # AI analysis engine
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Docker configuration
│   └── docker-compose.yml    # Docker services
└── frontend/
    ├── src/
    │   └── App.jsx           # React application
    ├── package.json
    └── public/
```

## 🔧 Configuration

### Environment Setup

**⚠️ IMPORTANT**: See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed configuration instructions including Google OAuth and email setup.

### Backend Configuration

Edit these environment variables in `docker-compose.yml` or create a `.env` file:

**Required for Basic Setup:**
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens (change in production!)
- `SECRET_KEY`: Secret key for Flask sessions

**Required for Google OAuth:**
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

**Required for Email Delivery:**
- `SENDGRID_API_KEY`: SendGrid API key for email sending
- `FROM_EMAIL`: Email address for sending notifications

**Required for AI Features:**
- `GEMINI_API_KEY`: Google Gemini API key for AI-powered features

### Frontend Configuration

Update the API URL in `App.jsx`:
```javascript
const API_URL = 'http://localhost:5000/api';  // Change for production
```

## 🎯 Usage

1. **Register/Login**: Create an account or login
2. **Upload Resume**: Click "New Analysis" and upload your resume (PDF, DOCX, or TXT)
3. **Paste Job Description**: Copy the job description from the posting
4. **Get Results**: View your match score, found keywords, and missing keywords
5. **Track Progress**: View your analysis history and skill development trends on the dashboard

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/google` - Initiate Google OAuth login
- `GET /api/auth/callback` - Handle Google OAuth callback
- `POST /api/auth/logout` - Logout user

### Analysis
- `POST /api/analyze` - Analyze resume (requires auth)
- `GET /api/analyses` - Get all user's analyses (requires auth)
- `GET /api/analyses/<id>` - Get specific analysis (requires auth)
- `POST /api/analyses/<id>/resend-email` - Resend analysis results via email

### AI Features
- `POST /api/analyze/feedback/<id>` - Generate personalized AI feedback
- `POST /api/analyze/optimize/<id>` - Generate optimized resume version
- `POST /api/analyze/cover-letter/<id>` - Generate tailored cover letter
- `POST /api/analyze/skill-suggestions/<id>` - Get skill development suggestions

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics (requires auth)

## 🔐 Security Features

- Password hashing with bcrypt
- JWT-based authentication
- Google OAuth 2.0 integration
- CORS protection
- SQL injection prevention via SQLAlchemy ORM
- Input validation
- Environment variable security
- Rate limiting

## 🧪 Testing

Test the backend API:
```bash
# Health check
curl http://localhost:5000/api/health

# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## 🚀 Deployment

### Deploy to Heroku

1. **Install Heroku CLI** and login:
```bash
heroku login
```

2. **Create Heroku app**:
```bash
heroku create your-app-name
```

3. **Add PostgreSQL addon**:
```bash
heroku addons:create heroku-postgresql:mini
```

4. **Set environment variables**:
```bash
heroku config:set JWT_SECRET_KEY="your-production-secret-key"
```

5. **Deploy**:
```bash
git push heroku main
```

### Deploy to AWS/DigitalOcean

Use the provided `Dockerfile` and `docker-compose.yml` for containerized deployment on any cloud platform.

## 🎨 Customization

### Adding More NLP Features

Edit `ai_processor.py` to add:
- Custom skill extraction patterns
- Industry-specific keyword lists
- Advanced NER models
- Sentiment analysis

### Improving the UI

The React frontend uses Tailwind CSS. Customize colors and styling in `App.jsx`.

### Database Schema Extensions

Add new fields to models in `app.py`:
```python
class Analysis(db.Model):
    # Add custom fields
    industry = db.Column(db.String(100))
    experience_level = db.Column(db.String(50))
```

## 📈 Development Roadmap

### Phase 1 (Weeks 1-4) ✅
- [x] Backend API with authentication
- [x] Database schema
- [x] Basic frontend structure

### Phase 2 (Weeks 5-8) - Current
- [ ] Enhanced keyword extraction with KeyBERT
- [ ] Better NER with custom training
- [ ] PDF parsing improvements
- [ ] Resume version management

### Phase 3 (Weeks 9-12) ✅
- [x] Advanced dashboard visualizations
- [x] Email notifications with SendGrid
- [x] Google OAuth authentication
- [x] AI-powered resume optimization
- [x] Cover letter generation

### Phase 4 (Weeks 13-14)
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Cloud deployment
- [ ] Documentation

### Phase 5 (Week 15)
- [ ] Final presentation
- [ ] User testing
- [ ] Bug fixes

## 🐛 Troubleshooting

### Common Issues

**1. PDF parsing fails**
- Ensure PyPDF2 is installed correctly
- Try converting PDF to text format first
- Check if PDF has selectable text (not scanned image)

**2. spaCy model not found**
```bash
python -m spacy download en_core_web_sm
```

**3. Database connection errors**
- Check PostgreSQL is running
- Verify DATABASE_URL is correct
- Ensure database exists: `createdb resume_optimizer`

**4. CORS errors in frontend**
- Verify backend is running on port 5000
- Check CORS configuration in `app.py`
- Update API_URL in React app

**5. Docker build fails**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## 🔍 Performance Metrics

According to project proposal success metrics:

**Technical Metrics:**
- ✅ API response time: < 10 seconds for analysis
- ✅ Keyword accuracy: ~80% on test sets
- ✅ All features operational
- ✅ Containerized deployment ready

**User-Centric Metrics:**
- ✅ Clear, actionable suggestions
- ✅ Easy-to-understand visualizations
- ✅ No guidance needed for basic use

## 📚 Dependencies

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database
- **JWT**: Authentication
- **spaCy**: NLP and NER
- **scikit-learn**: ML algorithms (TF-IDF, cosine similarity)
- **PyPDF2**: PDF parsing
- **python-docx**: DOCX parsing

### Frontend
- **React**: UI framework
- **Recharts**: Data visualization
- **Tailwind CSS**: Styling

## 🤝 Contributing

This is an academic project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚠️ Ethical Considerations

Per the project proposal:

**Privacy & Security:**
- All user data is encrypted and secure
- No data sharing with third parties
- HTTPS required in production

**Algorithmic Bias:**
- Tool is transparent about keyword matching
- Encourages honest skill representation
- Does not judge candidate quality

**User Wellbeing:**
- Encouraging language in UI
- Score framed as "similarity," not "qualification"
- Emphasizes continuous improvement

## 📝 License

This project is for educational purposes as part of ITAI 2277 coursework.

## 👤 Author

Alhassane Samassekou  
Project Reference: RT-14165  
Course: ITAI 2277 – Artificial Intelligence

## 🙏 Acknowledgments

- spaCy for NLP capabilities
- scikit-learn for ML algorithms
- Flask and React communities

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the API documentation
3. Check Docker logs: `docker-compose logs backend`

## 🎓 Academic Context

This project fulfills the requirements for Phase 01 of the AI course project, demonstrating:
- Full-stack development skills
- AI/ML integration
- Database design
- User authentication
- Data visualization
- Ethical AI considerations

---

**Note**: Remember to change the `JWT_SECRET_KEY` before deploying to production!