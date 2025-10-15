from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Analysis(db.Model):
    """Analysis model for storing resume analysis results"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Job information
    job_title = db.Column(db.String(200))
    company_name = db.Column(db.String(200))
    
    # Analysis results
    match_score = db.Column(db.Float, nullable=False)
    keywords_found = db.Column(db.JSON)
    keywords_missing = db.Column(db.JSON)
    suggestions = db.Column(db.Text)
    
    # Content
    resume_text = db.Column(db.Text)
    job_description = db.Column(db.Text)
    
    # AI enhancements
    ai_feedback = db.Column(db.Text)
    optimized_resume = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for better query performance
    __table_args__ = (
        db.Index('idx_user_created', 'user_id', 'created_at'),
        db.Index('idx_match_score', 'match_score'),
    )
    
    def __repr__(self):
        return f'<Analysis {self.id} for User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_title': self.job_title,
            'company_name': self.company_name,
            'match_score': self.match_score,
            'keywords_found': self.keywords_found,
            'keywords_missing': self.keywords_missing,
            'suggestions': self.suggestions,
            'ai_feedback': self.ai_feedback,
            'optimized_resume': self.optimized_resume,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UserSchema(SQLAlchemyAutoSchema):
    """Marshmallow schema for User serialization"""
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6, max=128))
    
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash', 'analyses')

class AnalysisSchema(SQLAlchemyAutoSchema):
    """Marshmallow schema for Analysis serialization"""
    job_title = fields.Str(validate=validate.Length(max=200))
    company_name = fields.Str(validate=validate.Length(max=200))
    match_score = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    suggestions = fields.Str(validate=validate.Length(max=2000))
    
    class Meta:
        model = Analysis
        load_instance = True
        exclude = ('user_id', 'resume_text', 'job_description')

class AnalysisCreateSchema(Schema):
    """Schema for creating new analyses"""
    job_title = fields.Str(validate=validate.Length(max=200))
    company_name = fields.Str(validate=validate.Length(max=200))
    job_description = fields.Str(required=True, validate=validate.Length(min=50, max=10000))

# Initialize schemas
user_schema = UserSchema()
analysis_schema = AnalysisSchema()
analysis_create_schema = AnalysisCreateSchema()
