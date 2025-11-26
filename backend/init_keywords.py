"""
Initialize keyword database with common technologies and skills

This script populates the keywords table with industry-standard skills and technologies.
Run with: docker-compose exec backend python init_keywords.py
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_keywords():
    """Initialize core keywords database"""
    # Import inside function to ensure Flask app is initialized
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/resume_optimizer')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)

    # Import models after db is configured
    from datetime import datetime

    # Define Keyword model inline to avoid import issues
    class Keyword(db.Model):
        __tablename__ = 'keywords'
        id = db.Column(db.Integer, primary_key=True)
        keyword = db.Column(db.String(100), unique=True, nullable=False, index=True)
        keyword_type = db.Column(db.String(50), nullable=False)
        category = db.Column(db.String(100), nullable=False, index=True)
        priority = db.Column(db.String(20), default='medium', nullable=False)
        industry_relevance = db.Column(db.JSON, default={})
        synonyms = db.Column(db.JSON, default=[])
        related_keywords = db.Column(db.JSON, default=[])
        confidence_score = db.Column(db.Float, default=1.0)
        is_deprecated = db.Column(db.Boolean, default=False)
        replacement_keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'))
        year_popularity = db.Column(db.JSON, default={})
        average_salary_premium = db.Column(db.Float)
        difficulty_level = db.Column(db.String(20), default='intermediate')
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        updated_by_id = db.Column(db.Integer)

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        logger.info("Database tables created/verified")

        # Clear existing keywords (optional - comment out if you want to preserve)
        # Keyword.query.delete()
        # db.session.commit()

        keywords_data = [
            # ==================== PROGRAMMING LANGUAGES ====================
            {
                'keyword': 'python',
                'keyword_type': 'language',
                'category': 'backend',
                'priority': 'critical',
                'synonyms': ['python3', 'python 3', 'py', 'python3.9', 'python3.10', 'python3.11'],
                'related_keywords': ['django', 'flask', 'fastapi', 'numpy', 'pandas', 'scikit-learn'],
                'industry_relevance': {'tech': 0.95, 'finance': 0.9, 'healthcare': 0.85, 'ecommerce': 0.8},
                'difficulty_level': 'beginner',
                'average_salary_premium': 15.0,
                'year_popularity': {'2020': 95, '2021': 92, '2022': 89, '2023': 85}
            },
            {
                'keyword': 'javascript',
                'keyword_type': 'language',
                'category': 'frontend',
                'priority': 'critical',
                'synonyms': ['js', 'javascript es6', 'es6', 'ecmascript'],
                'related_keywords': ['react', 'vue', 'angular', 'node.js', 'typescript'],
                'industry_relevance': {'tech': 0.98, 'ecommerce': 0.95, 'finance': 0.85},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 12.0,
                'year_popularity': {'2020': 98, '2021': 97, '2022': 96, '2023': 95}
            },
            {
                'keyword': 'typescript',
                'keyword_type': 'language',
                'category': 'frontend',
                'priority': 'important',
                'synonyms': ['ts', 'typescript 4', 'typescript 5'],
                'related_keywords': ['javascript', 'react', 'angular', 'node.js'],
                'industry_relevance': {'tech': 0.9, 'finance': 0.85},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 8.0,
                'year_popularity': {'2020': 70, '2021': 80, '2022': 87, '2023': 92}
            },
            {
                'keyword': 'java',
                'keyword_type': 'language',
                'category': 'backend',
                'priority': 'critical',
                'synonyms': ['java 8', 'java 11', 'java 17', 'jvm'],
                'related_keywords': ['spring', 'spring boot', 'maven', 'gradle', 'junit'],
                'industry_relevance': {'tech': 0.92, 'finance': 0.95, 'enterprise': 0.98},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 10.0,
                'year_popularity': {'2020': 90, '2021': 88, '2022': 85, '2023': 82}
            },
            {
                'keyword': 'go',
                'keyword_type': 'language',
                'category': 'backend',
                'priority': 'important',
                'synonyms': ['golang', 'go programming'],
                'related_keywords': ['docker', 'kubernetes', 'microservices'],
                'industry_relevance': {'tech': 0.85, 'devops': 0.9},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 12.0,
                'year_popularity': {'2020': 75, '2021': 80, '2022': 85, '2023': 88}
            },
            {
                'keyword': 'rust',
                'keyword_type': 'language',
                'category': 'backend',
                'priority': 'medium',
                'synonyms': ['rust programming'],
                'related_keywords': ['systems programming', 'memory safety'],
                'industry_relevance': {'tech': 0.75, 'systems': 0.9},
                'difficulty_level': 'advanced',
                'average_salary_premium': 18.0,
                'year_popularity': {'2020': 55, '2021': 65, '2022': 75, '2023': 82}
            },
            {
                'keyword': 'sql',
                'keyword_type': 'skill',
                'category': 'database',
                'priority': 'critical',
                'synonyms': ['sql querying', 'sql database'],
                'related_keywords': ['postgresql', 'mysql', 'oracle', 'database design'],
                'industry_relevance': {'tech': 0.95, 'data': 0.98, 'finance': 0.98},
                'difficulty_level': 'beginner',
                'average_salary_premium': 5.0,
                'year_popularity': {'2020': 98, '2021': 97, '2022': 96, '2023': 95}
            },

            # ==================== FRONTEND FRAMEWORKS ====================
            {
                'keyword': 'react',
                'keyword_type': 'framework',
                'category': 'frontend',
                'priority': 'critical',
                'synonyms': ['react.js', 'reactjs', 'react 16', 'react 17', 'react 18'],
                'related_keywords': ['javascript', 'jsx', 'redux', 'hooks', 'webpack'],
                'industry_relevance': {'tech': 0.96, 'ecommerce': 0.95, 'startup': 0.94},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 10.0,
                'year_popularity': {'2020': 95, '2021': 94, '2022': 92, '2023': 90}
            },
            {
                'keyword': 'vue',
                'keyword_type': 'framework',
                'category': 'frontend',
                'priority': 'important',
                'synonyms': ['vue.js', 'vuejs', 'vue 2', 'vue 3'],
                'related_keywords': ['javascript', 'vuex', 'composition api'],
                'industry_relevance': {'tech': 0.75, 'startup': 0.8},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 8.0,
                'year_popularity': {'2020': 72, '2021': 73, '2022': 72, '2023': 70}
            },
            {
                'keyword': 'angular',
                'keyword_type': 'framework',
                'category': 'frontend',
                'priority': 'important',
                'synonyms': ['angularjs', 'angular 12', 'angular 13', 'angular 14', 'angular 15'],
                'related_keywords': ['typescript', 'rxjs', 'dependency injection'],
                'industry_relevance': {'tech': 0.78, 'enterprise': 0.88, 'finance': 0.85},
                'difficulty_level': 'advanced',
                'average_salary_premium': 9.0,
                'year_popularity': {'2020': 80, '2021': 78, '2022': 75, '2023': 72}
            },

            # ==================== BACKEND FRAMEWORKS ====================
            {
                'keyword': 'django',
                'keyword_type': 'framework',
                'category': 'backend',
                'priority': 'important',
                'synonyms': ['django rest framework', 'drf', 'django orm'],
                'related_keywords': ['python', 'postgresql', 'celery', 'redis'],
                'industry_relevance': {'tech': 0.88, 'startup': 0.9, 'ecommerce': 0.85},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 8.0,
                'year_popularity': {'2020': 88, '2021': 86, '2022': 83, '2023': 80}
            },
            {
                'keyword': 'flask',
                'keyword_type': 'framework',
                'category': 'backend',
                'priority': 'important',
                'synonyms': ['flask web'],
                'related_keywords': ['python', 'werkzeug', 'jinja2', 'sqlalchemy'],
                'industry_relevance': {'tech': 0.82, 'startup': 0.88},
                'difficulty_level': 'beginner',
                'average_salary_premium': 7.0,
                'year_popularity': {'2020': 85, '2021': 83, '2022': 80, '2023': 77}
            },
            {
                'keyword': 'fastapi',
                'keyword_type': 'framework',
                'category': 'backend',
                'priority': 'medium',
                'synonyms': ['fast api'],
                'related_keywords': ['python', 'async', 'pydantic', 'uvicorn'],
                'industry_relevance': {'tech': 0.85, 'startup': 0.88},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 10.0,
                'year_popularity': {'2020': 60, '2021': 72, '2022': 82, '2023': 88}
            },
            {
                'keyword': 'spring boot',
                'keyword_type': 'framework',
                'category': 'backend',
                'priority': 'critical',
                'synonyms': ['spring', 'spring framework', 'springboot'],
                'related_keywords': ['java', 'maven', 'gradle', 'microservices'],
                'industry_relevance': {'tech': 0.90, 'enterprise': 0.95, 'finance': 0.92},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 9.0,
                'year_popularity': {'2020': 92, '2021': 90, '2022': 88, '2023': 86}
            },
            {
                'keyword': 'node.js',
                'keyword_type': 'framework',
                'category': 'backend',
                'priority': 'critical',
                'synonyms': ['nodejs', 'node'],
                'related_keywords': ['javascript', 'express', 'npm', 'async'],
                'industry_relevance': {'tech': 0.92, 'startup': 0.95, 'ecommerce': 0.90},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 8.0,
                'year_popularity': {'2020': 90, '2021': 89, '2022': 87, '2023': 85}
            },

            # ==================== DATABASES ====================
            {
                'keyword': 'postgresql',
                'keyword_type': 'technology',
                'category': 'database',
                'priority': 'critical',
                'synonyms': ['postgres', 'postgresql 12', 'postgresql 13', 'postgresql 14', 'postgresql 15'],
                'related_keywords': ['sql', 'database design', 'plpgsql'],
                'industry_relevance': {'tech': 0.95, 'startup': 0.94, 'data': 0.92},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 6.0,
                'year_popularity': {'2020': 88, '2021': 89, '2022': 90, '2023': 91}
            },
            {
                'keyword': 'mongodb',
                'keyword_type': 'technology',
                'category': 'database',
                'priority': 'important',
                'synonyms': ['mongo', 'mongodb 4', 'mongodb 5', 'mongodb 6'],
                'related_keywords': ['nosql', 'bson', 'mongoose', 'aggregation'],
                'industry_relevance': {'tech': 0.85, 'startup': 0.90, 'ecommerce': 0.88},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 5.0,
                'year_popularity': {'2020': 82, '2021': 82, '2022': 80, '2023': 78}
            },
            {
                'keyword': 'redis',
                'keyword_type': 'technology',
                'category': 'database',
                'priority': 'important',
                'synonyms': ['redis cache', 'redis in-memory'],
                'related_keywords': ['caching', 'data structures', 'pubsub'],
                'industry_relevance': {'tech': 0.88, 'ecommerce': 0.90, 'finance': 0.85},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 7.0,
                'year_popularity': {'2020': 85, '2021': 86, '2022': 87, '2023': 88}
            },

            # ==================== DEVOPS & CLOUD ====================
            {
                'keyword': 'docker',
                'keyword_type': 'technology',
                'category': 'devops',
                'priority': 'critical',
                'synonyms': ['docker containers', 'containerization'],
                'related_keywords': ['kubernetes', 'docker-compose', 'registry'],
                'industry_relevance': {'tech': 0.95, 'enterprise': 0.92, 'startup': 0.88},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 10.0,
                'year_popularity': {'2020': 88, '2021': 90, '2022': 92, '2023': 94}
            },
            {
                'keyword': 'kubernetes',
                'keyword_type': 'technology',
                'category': 'devops',
                'priority': 'critical',
                'synonyms': ['k8s', 'k3s', 'kubernetes orchestration'],
                'related_keywords': ['docker', 'helm', 'microservices', 'pods'],
                'industry_relevance': {'tech': 0.90, 'enterprise': 0.95, 'startup': 0.80},
                'difficulty_level': 'advanced',
                'average_salary_premium': 15.0,
                'year_popularity': {'2020': 82, '2021': 87, '2022': 91, '2023': 94}
            },
            {
                'keyword': 'aws',
                'keyword_type': 'technology',
                'category': 'devops',
                'priority': 'critical',
                'synonyms': ['amazon web services', 'aws ec2', 'aws lambda', 'aws rds', 's3'],
                'related_keywords': ['cloud computing', 'devops', 'infrastructure'],
                'industry_relevance': {'tech': 0.95, 'enterprise': 0.93, 'startup': 0.92},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 12.0,
                'year_popularity': {'2020': 92, '2021': 93, '2022': 94, '2023': 95}
            },
            {
                'keyword': 'gcp',
                'keyword_type': 'technology',
                'category': 'devops',
                'priority': 'important',
                'synonyms': ['google cloud', 'google cloud platform', 'gce', 'bigquery'],
                'related_keywords': ['cloud computing', 'devops', 'data analytics'],
                'industry_relevance': {'tech': 0.85, 'data': 0.92},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 11.0,
                'year_popularity': {'2020': 78, '2021': 80, '2022': 82, '2023': 84}
            },
            {
                'keyword': 'azure',
                'keyword_type': 'technology',
                'category': 'devops',
                'priority': 'important',
                'synonyms': ['microsoft azure', 'azure cloud', 'azure devops'],
                'related_keywords': ['cloud computing', 'devops', 'enterprise'],
                'industry_relevance': {'tech': 0.82, 'enterprise': 0.95, 'finance': 0.88},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 10.0,
                'year_popularity': {'2020': 80, '2021': 82, '2022': 84, '2023': 86}
            },

            # ==================== DATA SCIENCE & ML ====================
            {
                'keyword': 'machine learning',
                'keyword_type': 'skill',
                'category': 'ml',
                'priority': 'critical',
                'synonyms': ['ml', 'machine learning algorithms', 'supervised learning', 'unsupervised learning'],
                'related_keywords': ['tensorflow', 'scikit-learn', 'neural networks', 'data science'],
                'industry_relevance': {'tech': 0.90, 'finance': 0.92, 'healthcare': 0.95},
                'difficulty_level': 'advanced',
                'average_salary_premium': 20.0,
                'year_popularity': {'2020': 88, '2021': 90, '2022': 92, '2023': 94}
            },
            {
                'keyword': 'tensorflow',
                'keyword_type': 'framework',
                'category': 'ml',
                'priority': 'important',
                'synonyms': ['tensorflow 2', 'tf', 'tensorflow.js'],
                'related_keywords': ['keras', 'neural networks', 'deep learning'],
                'industry_relevance': {'tech': 0.88, 'data': 0.95},
                'difficulty_level': 'advanced',
                'average_salary_premium': 16.0,
                'year_popularity': {'2020': 85, '2021': 87, '2022': 88, '2023': 89}
            },
            {
                'keyword': 'pytorch',
                'keyword_type': 'framework',
                'category': 'ml',
                'priority': 'important',
                'synonyms': ['torch', 'pytorch deep learning'],
                'related_keywords': ['neural networks', 'deep learning', 'cuda'],
                'industry_relevance': {'tech': 0.85, 'data': 0.92},
                'difficulty_level': 'advanced',
                'average_salary_premium': 15.0,
                'year_popularity': {'2020': 80, '2021': 85, '2022': 88, '2023': 91}
            },
            {
                'keyword': 'numpy',
                'keyword_type': 'framework',
                'category': 'data',
                'priority': 'important',
                'synonyms': ['numerical python'],
                'related_keywords': ['python', 'pandas', 'scipy', 'data analysis'],
                'industry_relevance': {'tech': 0.90, 'data': 0.98},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 4.0,
                'year_popularity': {'2020': 92, '2021': 93, '2022': 93, '2023': 92}
            },
            {
                'keyword': 'pandas',
                'keyword_type': 'framework',
                'category': 'data',
                'priority': 'important',
                'synonyms': ['python data analysis'],
                'related_keywords': ['python', 'numpy', 'data analysis', 'dataframes'],
                'industry_relevance': {'tech': 0.90, 'data': 0.98},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 4.0,
                'year_popularity': {'2020': 91, '2021': 92, '2022': 92, '2023': 91}
            },

            # ==================== OTHER IMPORTANT SKILLS ====================
            {
                'keyword': 'git',
                'keyword_type': 'tool',
                'category': 'devops',
                'priority': 'critical',
                'synonyms': ['github', 'gitlab', 'bitbucket', 'version control'],
                'related_keywords': ['version control', 'ci/cd', 'collaboration'],
                'industry_relevance': {'tech': 0.98, 'all': 0.95},
                'difficulty_level': 'beginner',
                'average_salary_premium': 0.0,
                'year_popularity': {'2020': 98, '2021': 98, '2022': 98, '2023': 98}
            },
            {
                'keyword': 'rest api',
                'keyword_type': 'skill',
                'category': 'backend',
                'priority': 'critical',
                'synonyms': ['restful api', 'rest', 'http api', 'rest web services'],
                'related_keywords': ['api design', 'http', 'json', 'openapi'],
                'industry_relevance': {'tech': 0.96, 'ecommerce': 0.95},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 5.0,
                'year_popularity': {'2020': 96, '2021': 96, '2022': 95, '2023': 94}
            },
            {
                'keyword': 'microservices',
                'keyword_type': 'skill',
                'category': 'backend',
                'priority': 'important',
                'synonyms': ['microservice architecture', 'micro services'],
                'related_keywords': ['docker', 'kubernetes', 'service mesh'],
                'industry_relevance': {'tech': 0.88, 'enterprise': 0.92},
                'difficulty_level': 'advanced',
                'average_salary_premium': 12.0,
                'year_popularity': {'2020': 82, '2021': 85, '2022': 88, '2023': 90}
            },
            {
                'keyword': 'ci/cd',
                'keyword_type': 'skill',
                'category': 'devops',
                'priority': 'important',
                'synonyms': ['continuous integration', 'continuous deployment', 'jenkins', 'gitlab ci', 'github actions'],
                'related_keywords': ['docker', 'kubernetes', 'automation'],
                'industry_relevance': {'tech': 0.90, 'enterprise': 0.88},
                'difficulty_level': 'intermediate',
                'average_salary_premium': 8.0,
                'year_popularity': {'2020': 85, '2021': 87, '2022': 89, '2023': 91}
            },
            {
                'keyword': 'agile',
                'keyword_type': 'skill',
                'category': 'management',
                'priority': 'important',
                'synonyms': ['scrum', 'kanban', 'agile methodology', 'sprint'],
                'related_keywords': ['project management', 'teamwork'],
                'industry_relevance': {'tech': 0.88, 'all': 0.82},
                'difficulty_level': 'beginner',
                'average_salary_premium': 0.0,
                'year_popularity': {'2020': 85, '2021': 86, '2022': 87, '2023': 88}
            },
        ]

        added_count = 0
        skipped_count = 0

        for kw_data in keywords_data:
            # Check if keyword already exists
            existing = Keyword.query.filter_by(keyword=kw_data['keyword'].lower()).first()
            if existing:
                logger.info(f"Skipping {kw_data['keyword']} - already exists")
                skipped_count += 1
                continue

            keyword = Keyword(**kw_data)
            db.session.add(keyword)
            added_count += 1

        db.session.commit()
        logger.info(f"✅ Initialized keywords: Added {added_count}, Skipped {skipped_count}")

        # Log summary
        total = Keyword.query.count()
        categories = db.session.query(Keyword.category, db.func.count(Keyword.id)).group_by(Keyword.category).all()
        logger.info(f"Total keywords: {total}")
        for category, count in categories:
            logger.info(f"  - {category}: {count}")


if __name__ == '__main__':
    init_keywords()
