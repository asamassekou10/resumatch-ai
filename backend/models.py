from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class Role(db.Model):
    """Role model for RBAC"""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    permissions = db.relationship('Permission', secondary='role_permissions', backref='roles')
    users = db.relationship('User', secondary='user_roles', backref='roles')

    def __repr__(self):
        return f'<Role {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': [p.name for p in self.permissions],
            'created_at': self.created_at.isoformat()
        }

class Permission(db.Model):
    """Permission model for RBAC"""
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Permission {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

# Association table for user roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

# Association table for role permissions
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    name = db.Column(db.String(100), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    auth_provider = db.Column(db.String(20), default='email')  # 'email' or 'google'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), nullable=True)
    # Subscription and credit fields
    subscription_tier = db.Column(db.String(50), default='free', nullable=False)
    credits = db.Column(db.Integer, default=0, nullable=False)
    stripe_customer_id = db.Column(db.String(255), nullable=True, unique=True)
    subscription_id = db.Column(db.String(255), nullable=True, unique=True)

    # Market preferences for personalized insights
    preferred_industry = db.Column(db.String(100), nullable=True)  # 'Technology', 'Healthcare', 'Security', etc.
    preferred_job_titles = db.Column(db.JSON, default=[])  # List of target job titles
    preferred_location = db.Column(db.String(200), nullable=True)  # City/region preference
    experience_level = db.Column(db.String(50), nullable=True)  # 'Entry', 'Mid', 'Senior', 'Executive'
    preferences_completed = db.Column(db.Boolean, default=False)  # Has user completed preference setup?
    detected_industries = db.Column(db.JSON, default=[])  # Industries detected from their resumes

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    admin_logs = db.relationship('AdminLog', backref='admin_user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def has_admin_access(self):
        """Check if user has admin access (bypasses payment)"""
        return self.is_admin

    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name):
        """Check if user has a specific permission through any of their roles"""
        return any(permission.name == permission_name for role in self.roles for permission in role.permissions)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'subscription_tier': self.subscription_tier,
            'credits': self.credits,
            'roles': [r.name for r in self.roles],
            'preferred_industry': self.preferred_industry,
            'preferred_job_titles': self.preferred_job_titles or [],
            'preferred_location': self.preferred_location,
            'experience_level': self.experience_level,
            'preferences_completed': self.preferences_completed,
            'detected_industries': self.detected_industries or [],
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
    resume_filename = db.Column(db.String(255))  # Original filename of uploaded resume
    detected_industry = db.Column(db.String(100), nullable=True)  # Industry detected from resume

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
            'resume_filename': self.resume_filename,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AdminLog(db.Model):
    """AdminLog model for audit trail of admin actions"""
    __tablename__ = 'admin_logs'

    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    changes = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        db.Index('idx_admin_created', 'admin_user_id', 'created_at'),
    )

    def __repr__(self):
        return f'<AdminLog {self.action} on {self.resource_type}:{self.resource_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'admin_user_id': self.admin_user_id,
            'admin_email': self.admin_user.email if self.admin_user else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'changes': self.changes,
            'created_at': self.created_at.isoformat()
        }

class SystemConfiguration(db.Model):
    """System-wide configuration settings - allows runtime configuration without code changes"""
    __tablename__ = 'system_configuration'

    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.JSON, nullable=False)
    data_type = db.Column(db.String(50), nullable=False)  # 'int', 'float', 'string', 'json', 'bool'
    description = db.Column(db.Text)
    category = db.Column(db.String(50), index=True)  # 'file', 'validation', 'scoring', 'rate_limit', 'credit', 'ai'
    is_editable = db.Column(db.Boolean, default=True)  # Some configs should be read-only
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = (
        db.Index('idx_config_category', 'category'),
    )

    def __repr__(self):
        return f'<SystemConfiguration {self.config_key}={self.config_value}>'

    def to_dict(self):
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'data_type': self.data_type,
            'description': self.description,
            'category': self.category,
            'is_editable': self.is_editable,
            'updated_at': self.updated_at.isoformat()
        }

class SubscriptionTier(db.Model):
    """Define subscription tiers with their features and limits"""
    __tablename__ = 'subscription_tiers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 'free', 'pro', 'enterprise'
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    monthly_credits = db.Column(db.Integer, default=0)
    price_cents = db.Column(db.Integer, default=0)  # in cents, e.g., 1999 = $19.99
    stripe_price_id = db.Column(db.String(100))  # Stripe price identifier
    max_file_size_mb = db.Column(db.Integer, default=5)
    max_analyses_per_month = db.Column(db.Integer, default=5)
    max_concurrent_uploads = db.Column(db.Integer, default=1)
    features = db.Column(db.JSON, default={})  # e.g., {'ai_feedback': True, 'optimization': False}
    rate_limits = db.Column(db.JSON, default={})  # Custom rate limits per tier
    is_active = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0)  # Display order
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SubscriptionTier {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'monthly_credits': self.monthly_credits,
            'price_cents': self.price_cents,
            'max_file_size_mb': self.max_file_size_mb,
            'max_analyses_per_month': self.max_analyses_per_month,
            'features': self.features,
            'rate_limits': self.rate_limits,
            'is_active': self.is_active
        }

class RateLimitConfig(db.Model):
    """Configure rate limits for different operations and user tiers"""
    __tablename__ = 'rate_limit_config'

    id = db.Column(db.Integer, primary_key=True)
    operation = db.Column(db.String(100), nullable=False)  # 'resume_analysis', 'feedback', 'optimization'
    subscription_tier = db.Column(db.String(50), nullable=False)  # 'free', 'pro', 'enterprise', 'default'
    requests_per_hour = db.Column(db.Integer, nullable=False)
    requests_per_day = db.Column(db.Integer, nullable=False)
    requests_per_month = db.Column(db.Integer)
    cost_in_credits = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('operation', 'subscription_tier', name='unique_op_tier'),
        db.Index('idx_operation', 'operation'),
        db.Index('idx_tier', 'subscription_tier'),
    )

    def __repr__(self):
        return f'<RateLimitConfig {self.operation} - {self.subscription_tier}>'

    def to_dict(self):
        return {
            'id': self.id,
            'operation': self.operation,
            'subscription_tier': self.subscription_tier,
            'requests_per_hour': self.requests_per_hour,
            'requests_per_day': self.requests_per_day,
            'requests_per_month': self.requests_per_month,
            'cost_in_credits': self.cost_in_credits,
            'description': self.description
        }

class ScoringThreshold(db.Model):
    """Configure intelligent scoring thresholds and feedback ranges"""
    __tablename__ = 'scoring_thresholds'

    id = db.Column(db.Integer, primary_key=True)
    threshold_name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    min_score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)  # Dynamic feedback message
    color_code = db.Column(db.String(7))  # Hex color for UI display
    icon = db.Column(db.String(50))  # Icon identifier for UI
    recommendation_weight = db.Column(db.Float, default=1.0)  # How heavily to weight this category
    skill_extraction_keywords = db.Column(db.JSON, default=[])  # Keywords to extract for this range
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ScoringThreshold {self.threshold_name}: {self.min_score}-{self.max_score}%>'

    def to_dict(self):
        return {
            'id': self.id,
            'threshold_name': self.threshold_name,
            'min_score': self.min_score,
            'max_score': self.max_score,
            'feedback_text': self.feedback_text,
            'color_code': self.color_code,
            'icon': self.icon,
            'recommendation_weight': self.recommendation_weight
        }

class ValidationRule(db.Model):
    """Centralized validation rules - password, email, file, text"""
    __tablename__ = 'validation_rules'

    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    rule_category = db.Column(db.String(50), nullable=False)  # 'password', 'email', 'file', 'text'
    rule_type = db.Column(db.String(50), nullable=False)  # 'min_length', 'max_length', 'pattern', 'file_size'
    rule_value = db.Column(db.JSON, nullable=False)  # Value or pattern
    error_message = db.Column(db.Text)
    priority = db.Column(db.Integer, default=0)  # Order of validation
    is_active = db.Column(db.Boolean, default=True)
    applies_to_tier = db.Column(db.String(50))  # Null = all tiers
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_category_type', 'rule_category', 'rule_type'),
    )

    def __repr__(self):
        return f'<ValidationRule {self.rule_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'rule_category': self.rule_category,
            'rule_type': self.rule_type,
            'rule_value': self.rule_value,
            'error_message': self.error_message,
            'is_active': self.is_active,
            'applies_to_tier': self.applies_to_tier
        }

class Keyword(db.Model):
    """Enterprise-grade intelligent keyword/skill management with hierarchical taxonomy"""
    __tablename__ = 'keywords'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True, nullable=False, index=True)
    keyword_type = db.Column(db.String(50), nullable=False)  # 'skill', 'technology', 'framework', 'tool', 'concept', 'language'
    category = db.Column(db.String(100), nullable=False, index=True)  # 'backend', 'frontend', 'database', 'devops', 'ml', 'data', etc.
    priority = db.Column(db.String(20), default='medium', nullable=False)  # 'critical', 'important', 'medium', 'optional'
    industry_relevance = db.Column(db.JSON, default={})  # {'tech': 0.95, 'finance': 0.3, 'healthcare': 0.7}
    synonyms = db.Column(db.JSON, default=[])  # ["python3", "python 3", "py", "python3.9"]
    related_keywords = db.Column(db.JSON, default=[])  # ["numpy", "pandas", "django"] - related skills
    confidence_score = db.Column(db.Float, default=1.0)  # 0-1: confidence in keyword validity
    is_deprecated = db.Column(db.Boolean, default=False)  # Old technology that's being phased out
    replacement_keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'))  # If deprecated, what to use instead
    year_popularity = db.Column(db.JSON, default={})  # {'2021': 95, '2022': 88, '2023': 75}
    average_salary_premium = db.Column(db.Float)  # Additional salary % for this skill
    difficulty_level = db.Column(db.String(20), default='intermediate')  # 'beginner', 'intermediate', 'advanced', 'expert'

    # NEW: Hierarchical taxonomy support
    parent_keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=True)  # For hierarchy
    hierarchy_level = db.Column(db.Integer, default=2)  # 0=root industry, 1=category, 2=skill
    parent_keyword = db.relationship('Keyword', remote_side=[id], foreign_keys=[parent_keyword_id], backref='child_keywords')

    # NEW: ML/NER extraction tracking
    extraction_patterns = db.Column(db.JSON, default=[])  # Regex patterns for NER: ["python\d?", "py\d?"]
    extraction_count = db.Column(db.Integer, default=0)  # How often auto-extracted from resumes
    user_confirmed_count = db.Column(db.Integer, default=0)  # User confirmations (accuracy metric)
    user_rejected_count = db.Column(db.Integer, default=0)  # User rejections
    extraction_accuracy = db.Column(db.Float, default=1.0)  # confirmed / (confirmed + rejected)

    # NEW: Skill relationship tracking
    co_occurrence_patterns = db.Column(db.JSON, default={})  # {"python": 0.95, "django": 0.92}
    skill_co_occurrence_count = db.Column(db.Integer, default=0)  # Times appearing with other skills

    # NEW: Market intelligence
    job_postings_containing = db.Column(db.Integer, default=0)  # Count from job postings
    market_demand_score = db.Column(db.Float, default=0.5)  # 0-1: current market demand
    salary_trend = db.Column(db.JSON, default={})  # {'2020': 95000, '2021': 105000, '2023': 120000}
    trend_direction = db.Column(db.String(20), default='stable')  # 'increasing', 'decreasing', 'stable'

    # NEW: Metadata and tracking
    source = db.Column(db.String(50), default='manual')  # 'manual', 'auto_extracted', 'user_added', 'job_posting'
    last_verified_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = (
        db.Index('idx_keyword_category', 'category'),
        db.Index('idx_keyword_type', 'keyword_type'),
        db.Index('idx_keyword_priority', 'priority'),
        db.Index('idx_keyword_parent', 'parent_keyword_id'),
        db.Index('idx_keyword_hierarchy', 'hierarchy_level'),
        db.Index('idx_keyword_source', 'source'),
    )

    def __repr__(self):
        return f'<Keyword {self.keyword} ({self.category})>'

    def to_dict(self):
        return {
            'id': self.id,
            'keyword': self.keyword,
            'keyword_type': self.keyword_type,
            'category': self.category,
            'priority': self.priority,
            'industry_relevance': self.industry_relevance,
            'synonyms': self.synonyms,
            'related_keywords': self.related_keywords,
            'confidence_score': self.confidence_score,
            'is_deprecated': self.is_deprecated,
            'difficulty_level': self.difficulty_level,
            'average_salary_premium': self.average_salary_premium,
            'year_popularity': self.year_popularity
        }

class KeywordSimilarity(db.Model):
    """Pre-computed semantic similarity between keywords"""
    __tablename__ = 'keyword_similarity'

    id = db.Column(db.Integer, primary_key=True)
    keyword_1_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    keyword_2_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)  # 0-1: cosine similarity
    match_type = db.Column(db.String(50), nullable=False)  # 'synonym', 'related', 'version_variant', 'acronym_expansion'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('keyword_1_id', 'keyword_2_id', name='unique_keyword_pair'),
        db.Index('idx_keyword1', 'keyword_1_id'),
        db.Index('idx_keyword2', 'keyword_2_id'),
    )

    def __repr__(self):
        return f'<KeywordSimilarity {self.keyword_1_id} <-> {self.keyword_2_id}: {self.similarity_score}>'

class KeywordDatabase(db.Model):
    """Curated industry-standard keyword database mappings"""
    __tablename__ = 'keyword_database'

    id = db.Column(db.Integer, primary_key=True)
    data_source = db.Column(db.String(100), nullable=False)  # 'job_market', 'user_input', 'ai_generated', 'manual_curation'
    role_level = db.Column(db.String(50), nullable=False)  # 'entry', 'mid', 'senior', 'lead', 'architect'
    job_role = db.Column(db.String(100), nullable=False, index=True)  # 'Data Scientist', 'Full Stack Engineer', 'DevOps Engineer'
    keywords = db.Column(db.JSON, nullable=False)  # {category: [keywords]}
    description = db.Column(db.Text)
    confidence = db.Column(db.Float, default=0.8)  # Confidence in these keywords for this role
    industry_tag = db.Column(db.String(100))  # 'tech', 'finance', 'healthcare', 'ecommerce'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_job_role', 'job_role'),
        db.Index('idx_role_level', 'role_level'),
    )

    def __repr__(self):
        return f'<KeywordDatabase {self.job_role} - {self.role_level}>'

    def to_dict(self):
        return {
            'id': self.id,
            'job_role': self.job_role,
            'role_level': self.role_level,
            'keywords': self.keywords,
            'confidence': self.confidence,
            'industry_tag': self.industry_tag
        }

class KeywordMatchingRule(db.Model):
    """Fuzzy matching and keyword normalization rules"""
    __tablename__ = 'keyword_matching_rule'

    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(200), nullable=False, unique=True)  # Regex or substring pattern
    normalized_keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    match_type = db.Column(db.String(50), nullable=False)  # 'regex', 'substring', 'fuzzy', 'version_variant'
    confidence = db.Column(db.Float, default=0.9)  # 0-1: confidence in this matching rule
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index('idx_pattern', 'pattern'),
        db.Index('idx_normalized_keyword', 'normalized_keyword_id'),
    )

    def __repr__(self):
        return f'<KeywordMatchingRule {self.pattern} -> {self.normalized_keyword_id}>'

class UserSkillHistory(db.Model):
    """Track user's past keyword interactions for ML training"""
    __tablename__ = 'user_skill_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'))
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    user_confirmed = db.Column(db.Boolean)  # User confirmed this keyword applies to them
    user_rejected = db.Column(db.Boolean)  # User disagreed with this keyword match
    match_quality = db.Column(db.Float)  # 0-1: how well did this match
    context = db.Column(db.String(500))  # Where this keyword appeared in resume
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index('idx_user_skills', 'user_id'),
        db.Index('idx_keyword_history', 'keyword_id'),
    )

    def __repr__(self):
        return f'<UserSkillHistory user={self.user_id}, keyword={self.keyword_id}>'


# ==================== NEW: ML AND MARKET INTELLIGENCE MODELS ====================

class SkillExtraction(db.Model):
    """Track auto-extracted skills from resumes for quality improvement"""
    __tablename__ = 'skill_extraction'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=True)
    extracted_text = db.Column(db.String(200), nullable=False)  # What was extracted from resume
    matched_keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=True)
    confidence = db.Column(db.Float, nullable=False)  # NER confidence score (0-1)

    # User feedback
    user_confirmed = db.Column(db.Boolean, nullable=True)  # Did user agree with this extraction?
    user_rejected = db.Column(db.Boolean, nullable=True)  # Did user disagree?
    extraction_quality = db.Column(db.Float)  # Final quality score after user feedback

    # Metadata
    extraction_method = db.Column(db.String(50))  # 'regex', 'ner', 'fuzzy', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index('idx_extraction_keyword', 'matched_keyword_id'),
        db.Index('idx_extraction_analysis', 'analysis_id'),
        db.Index('idx_extraction_confirmed', 'user_confirmed'),
    )

    def __repr__(self):
        return f'<SkillExtraction {self.extracted_text} -> {self.matched_keyword_id}>'


class SkillRelationship(db.Model):
    """Track skill co-occurrence patterns in resumes for relationship discovery"""
    __tablename__ = 'skill_relationship'

    id = db.Column(db.Integer, primary_key=True)
    skill_1_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    skill_2_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)

    # Relationship metrics
    co_occurrence_count = db.Column(db.Integer, default=1)  # How many resumes have both?
    relationship_strength = db.Column(db.Float)  # 0-1: how strongly correlated
    relationship_type = db.Column(db.String(50))  # 'prerequisite', 'complementary', 'alternative'

    # Metadata
    first_seen_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('skill_1_id', 'skill_2_id', name='unique_skill_pair'),
        db.Index('idx_skill1', 'skill_1_id'),
        db.Index('idx_skill2', 'skill_2_id'),
        db.Index('idx_relationship_strength', 'relationship_strength'),
    )

    def __repr__(self):
        return f'<SkillRelationship {self.skill_1_id} <-> {self.skill_2_id}>'


class JobPostingKeyword(db.Model):
    """Track skills extracted from job postings for market intelligence"""
    __tablename__ = 'job_posting_keyword'

    id = db.Column(db.Integer, primary_key=True)
    job_posting_url = db.Column(db.String(500), nullable=True)  # External job posting URL (not unique - multiple skills per posting)
    job_title = db.Column(db.String(200), nullable=True)  # Job title from posting
    company_name = db.Column(db.String(200), nullable=True)

    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    frequency = db.Column(db.Integer, default=1)  # How many times mentioned in job description

    # Salary and market data
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    salary_currency = db.Column(db.String(10), default='USD')

    # Location and industry
    location = db.Column(db.String(200), nullable=True)
    industry = db.Column(db.String(100), nullable=True)

    # Metadata
    source = db.Column(db.String(50))  # 'indeed', 'linkedin', 'glassdoor', etc.
    extracted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index('idx_job_keyword', 'keyword_id'),
        db.Index('idx_job_location', 'location'),
        db.Index('idx_job_industry', 'industry'),
        db.Index('idx_job_extracted_at', 'extracted_at'),
    )

    def __repr__(self):
        return f'<JobPostingKeyword {self.job_title} - {self.keyword_id}>'


class SkillTaxonomy(db.Model):
    """Hierarchical skill taxonomy for organizational structure"""
    __tablename__ = 'skill_taxonomy'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 'Information Technology', 'Sales', etc.
    level = db.Column(db.Integer, nullable=False)  # 0=root, 1=category, 2=subcategory
    parent_id = db.Column(db.Integer, db.ForeignKey('skill_taxonomy.id'), nullable=True)

    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # For UI display

    # Metadata
    keywords_count = db.Column(db.Integer, default=0)  # How many keywords in this category?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_taxonomy_level', 'level'),
        db.Index('idx_taxonomy_parent', 'parent_id'),
    )

    def __repr__(self):
        return f'<SkillTaxonomy {self.name} (level {self.level})>'


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
