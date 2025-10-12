#!/bin/bash
# Complete Backend Setup Script
# This creates all necessary files for the AI Resume Optimizer backend

echo "Creating AI Resume Optimizer Backend Files..."

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY app.py .
COPY ai_processor.py .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: resume_optimizer
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/resume_optimizer
      JWT_SECRET_KEY: your-secret-key-change-in-production
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./app.py:/app/app.py
      - ./ai_processor.py:/app/ai_processor.py

volumes:
  postgres_data:
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.0
flask-cors==4.0.0
flask-sqlalchemy==3.1.1
flask-bcrypt==1.0.1
flask-jwt-extended==4.5.3
PyPDF2==3.0.1
python-docx==1.1.0
scikit-learn==1.3.2
spacy==3.7.2
psycopg2-binary==2.9.9
gunicorn==21.2.0
numpy==1.26.2
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
venv/
.env
*.db
*.sqlite
.DS_Store
EOF

echo "✅ All backend configuration files created!"
echo ""
echo "Files created:"
echo "  - Dockerfile"
echo "  - docker-compose.yml"
echo "  - requirements.txt"
echo "  - .gitignore"
echo ""
echo "⚠️  You still need to create:"
echo "  - app.py (copy from 'Backend API - Flask Server' artifact)"
echo "  - ai_processor.py (copy from 'AI Processor' artifact)"
echo ""
echo "After creating those files, run:"
echo "  docker-compose up --build"
EOF

chmod +x setup_backend.sh

echo "Script created! Run it with: bash setup_backend.sh"