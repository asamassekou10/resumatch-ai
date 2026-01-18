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
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), nullable=True)
    # Subscription and credit fields
    subscription_tier = db.Column(db.String(50), default='free', nullable=False, index=True)
    subscription_status = db.Column(db.String(50), default='inactive', nullable=False, index=True)  # inactive, active, cancelled, expired, past_due
    credits = db.Column(db.Integer, default=0, nullable=False)
    stripe_customer_id = db.Column(db.String(255), nullable=True, unique=True)
    subscription_id = db.Column(db.String(255), nullable=True, unique=True)
    subscription_start_date = db.Column(db.DateTime, nullable=True, index=True)  # For billing anniversary
    last_credit_reset = db.Column(db.DateTime, nullable=True)  # Track last credit reset
    
    # Trial tracking fields
    trial_start_date = db.Column(db.DateTime, nullable=True, index=True)
    trial_end_date = db.Column(db.DateTime, nullable=True, index=True)
    is_trial_active = db.Column(db.Boolean, default=False, nullable=False)
    trial_credits_granted = db.Column(db.Integer, default=0, nullable=False)
    trial_expired_date = db.Column(db.DateTime, nullable=True)
    last_email_sent_date = db.Column(db.DateTime, nullable=True)
    email_sequence_step = db.Column(db.Integer, default=0, nullable=False)  # Track which email in sequence

    # Email automation preferences and tracking
    weekly_email_start_date = db.Column(db.DateTime, nullable=True, index=True)  # Fixed reference date for weekly emails
    email_preferences = db.Column(db.JSON, default={})  # {'marketing': True, 'weekly': True, 'trial_updates': True}
    last_email_opened_date = db.Column(db.DateTime, nullable=True)
    last_email_clicked_date = db.Column(db.DateTime, nullable=True)
    email_bounce_count = db.Column(db.Integer, default=0, nullable=False)
    email_variant = db.Column(db.String(50), nullable=True)  # For A/B testing
    timezone = db.Column(db.String(50), default='UTC')  # User timezone for scheduling

    # Market preferences for personalized insights
    preferred_industry = db.Column(db.String(100), nullable=True, index=True)  # 'Technology', 'Healthcare', 'Security', etc.
    preferred_job_titles = db.Column(db.JSON, default=[])  # List of target job titles
    preferred_location = db.Column(db.String(200), nullable=True)  # City/region preference
    experience_level = db.Column(db.String(50), nullable=True)  # 'Entry', 'Mid', 'Senior', 'Executive'
    preferences_completed = db.Column(db.Boolean, default=False)  # Has user completed preference setup?
    detected_industries = db.Column(db.JSON, default=[])  # Industries detected from their resumes

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, index=True)

    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    admin_logs = db.relationship('AdminLog', backref='admin_user', lazy=True)

    # Table-level composite indexes for common queries
    __table_args__ = (
        db.Index('idx_user_subscription', 'subscription_tier', 'subscription_status'),
        db.Index('idx_user_active_tier', 'is_active', 'subscription_tier'),
    )

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

    def get_active_pass(self):
        """Get the user's active weekly pass if one exists"""
        from models import Purchase
        active_pass = Purchase.query.filter(
            Purchase.user_id == self.id,
            Purchase.purchase_type == 'weekly_pass',
            Purchase.is_active == True,
            Purchase.payment_status == 'succeeded',
            Purchase.access_expires_at > datetime.utcnow()
        ).order_by(Purchase.access_expires_at.desc()).first()
        return active_pass

    def has_active_pass(self):
        """Check if user has an active weekly pass"""
        return self.get_active_pass() is not None

    def to_dict(self):
        # Check for active weekly pass
        active_pass = self.get_active_pass()
        pass_info = None
        if active_pass:
            time_remaining = active_pass.access_expires_at - datetime.utcnow()
            hours_remaining = int(time_remaining.total_seconds() / 3600)
            days_remaining = hours_remaining // 24
            pass_info = {
                'is_active': True,
                'expires_at': active_pass.access_expires_at.isoformat(),
                'hours_remaining': hours_remaining,
                'days_remaining': days_remaining,
                'purchase_id': active_pass.id
            }

        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'credits': self.credits,
            'roles': [r.name for r in self.roles],
            'preferred_industry': self.preferred_industry,
            'preferred_job_titles': self.preferred_job_titles or [],
            'preferred_location': self.preferred_location,
            'experience_level': self.experience_level,
            'preferences_completed': self.preferences_completed,
            'detected_industries': self.detected_industries or [],
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'weekly_pass': pass_info
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
    optimized_feedback = db.Column(db.Text)  # Detailed optimization feedback
    cover_letter = db.Column(db.Text)  # AI-generated cover letter

    # Template system fields
    structured_resume = db.Column(db.JSON, nullable=True)  # Parsed resume data for templates
    selected_resume_template = db.Column(db.String(50), default='modern')
    selected_cover_letter_template = db.Column(db.String(50), default='professional')

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for better query performance
    __table_args__ = (
        db.Index('idx_user_created', 'user_id', 'created_at'),
        db.Index('idx_analysis_match_score', 'match_score'),
        db.Index('idx_analysis_industry', 'detected_industry'),
        db.Index('idx_analysis_user_industry', 'user_id', 'detected_industry'),
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
            'optimized_feedback': self.optimized_feedback,
            'cover_letter': self.cover_letter,
            'resume_filename': self.resume_filename,
            'structured_resume': self.structured_resume,
            'selected_resume_template': self.selected_resume_template,
            'selected_cover_letter_template': self.selected_cover_letter_template,
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
    keyword = db.relationship('Keyword', backref='job_postings', lazy='select')  # Relationship to enable joinedload
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
        db.Index('idx_job_posting_keyword_location', 'location'),
        db.Index('idx_job_posting_keyword_industry', 'industry'),
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


class GuestSession(db.Model):
    """Guest session model for temporary guest users without login"""
    __tablename__ = 'guest_sessions'

    id = db.Column(db.String(255), primary_key=True)  # UUID as string
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    credits_used = db.Column(db.Integer, default=0, nullable=False)
    credits_remaining = db.Column(db.Integer, default=5, nullable=False)

    # Guest session metadata
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent = db.Column(db.Text, nullable=True)
    device_fingerprint = db.Column(db.String(255), nullable=True)

    # Session status
    status = db.Column(db.String(20), default='active', nullable=False)  # 'active', 'expired', 'converted'
    converted_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)

    # Relationships
    analyses = db.relationship('GuestAnalysis', backref='guest_session', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_session_token', 'session_token'),
        db.Index('idx_expires_at', 'expires_at'),
        db.Index('idx_ip_address', 'ip_address'),
        db.Index('idx_device_fingerprint', 'device_fingerprint'),
        db.Index('idx_guest_status', 'status'),
    )

    def __repr__(self):
        return f'<GuestSession {self.id} ({self.status})>'

    def is_expired(self):
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at

    def has_credits(self):
        """Check if guest has remaining credits"""
        return self.credits_remaining > 0

    def deduct_credits(self, amount=1):
        """Deduct credits from guest session"""
        self.credits_used += amount
        self.credits_remaining = max(0, self.credits_remaining - amount)

    def to_dict(self):
        return {
            'id': self.id,
            'session_token': self.session_token,
            'credits_remaining': self.credits_remaining,
            'credits_used': self.credits_used,
            'status': self.status,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class GuestAnalysis(db.Model):
    """Guest analysis results - temporary, auto-deleted after 24 hours"""
    __tablename__ = 'guest_analyses'

    id = db.Column(db.String(255), primary_key=True)  # UUID as string
    guest_session_id = db.Column(db.String(255), db.ForeignKey('guest_sessions.id'), nullable=False, index=True)

    # Job information
    job_title = db.Column(db.String(200), nullable=True)
    company_name = db.Column(db.String(200), nullable=True)
    resume_filename = db.Column(db.String(255), nullable=True)

    # Analysis content
    resume_text = db.Column(db.Text, nullable=False)
    job_description = db.Column(db.Text, nullable=False)

    # Analysis results (stored as JSON)
    match_score = db.Column(db.Float, nullable=False)
    keywords_found = db.Column(db.JSON, nullable=True)
    keywords_missing = db.Column(db.JSON, nullable=True)
    suggestions = db.Column(db.Text, nullable=True)
    ai_feedback = db.Column(db.Text, nullable=True)
    detected_industry = db.Column(db.String(100), nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)

    __table_args__ = (
        db.Index('idx_guest_analysis_session_id', 'guest_session_id'),
        db.Index('idx_guest_analysis_expires_at', 'expires_at'),
    )

    def __repr__(self):
        return f'<GuestAnalysis {self.id}>'

    def is_expired(self):
        """Check if analysis has expired"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self, include_content=True):
        data = {
            'id': self.id,
            'guest_session_id': self.guest_session_id,
            'job_title': self.job_title,
            'company_name': self.company_name,
            'match_score': self.match_score,
            'keywords_found': self.keywords_found,
            'keywords_missing': self.keywords_missing,
            'suggestions': self.suggestions,
            'ai_feedback': self.ai_feedback,
            'detected_industry': self.detected_industry,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat()
        }

        if include_content:
            data['resume_text'] = self.resume_text
            data['job_description'] = self.job_description

        return data


# ==================== JOB MATCHING MODELS ====================

class JobPosting(db.Model):
    """Job postings for AI-powered job matching"""
    __tablename__ = 'job_postings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False, index=True)
    location = db.Column(db.String(200))
    remote_type = db.Column(db.String(50))  # 'remote', 'hybrid', 'onsite'
    industry = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    requirements = db.Column(db.JSON)  # ["Python", "React", "5 years exp"]
    responsibilities = db.Column(db.JSON)  # ["Build APIs", "Lead team"]
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    salary_currency = db.Column(db.String(10), default='USD')
    employment_type = db.Column(db.String(50))  # 'full-time', 'part-time', 'contract'
    experience_level = db.Column(db.String(50))  # 'Entry', 'Mid', 'Senior', 'Lead'
    posted_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_date = db.Column(db.DateTime)
    source = db.Column(db.String(100))  # 'LinkedIn', 'Indeed', 'Manual', etc.
    external_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matches = db.relationship('JobMatch', backref='job_posting', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_job_industry_active', 'industry', 'is_active'),
        db.Index('idx_job_posted_active', 'posted_date', 'is_active'),
        db.Index('idx_job_location', 'location'),
    )

    def __repr__(self):
        return f'<JobPosting {self.title} at {self.company}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'remote_type': self.remote_type,
            'industry': self.industry,
            'description': self.description,
            'requirements': self.requirements or [],
            'responsibilities': self.responsibilities or [],
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'salary_range': f"${self.salary_min:,} - ${self.salary_max:,}" if self.salary_min and self.salary_max else None,
            'employment_type': self.employment_type,
            'experience_level': self.experience_level,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'source': self.source,
            'external_url': self.external_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class JobMatch(db.Model):
    """AI-generated job matches for users with match scores and explanations"""
    __tablename__ = 'job_matches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False, index=True)

    # AI-generated match data
    match_score = db.Column(db.Float, nullable=False)  # 0-100
    ai_explanation = db.Column(db.Text)  # Why this is a good match
    matching_skills = db.Column(db.JSON)  # ["Python", "React", "AWS"]
    missing_skills = db.Column(db.JSON)  # ["Docker", "Kubernetes"]
    skill_match_percentage = db.Column(db.Float)  # Percentage of required skills matched

    # User interaction
    is_saved = db.Column(db.Boolean, default=False, index=True)
    is_applied = db.Column(db.Boolean, default=False)
    is_dismissed = db.Column(db.Boolean, default=False)
    viewed_at = db.Column(db.DateTime)
    saved_at = db.Column(db.DateTime)
    applied_at = db.Column(db.DateTime)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='job_matches')

    __table_args__ = (
        db.Index('idx_match_user_score', 'user_id', 'match_score'),
        db.Index('idx_match_user_saved', 'user_id', 'is_saved'),
        db.Index('idx_job_match_score', 'match_score'),
        db.UniqueConstraint('user_id', 'job_posting_id', name='unique_user_job_match'),
    )

    def __repr__(self):
        return f'<JobMatch user={self.user_id} job={self.job_posting_id} score={self.match_score}>'

    def mark_saved(self):
        """Mark this job as saved by the user"""
        self.is_saved = True
        self.saved_at = datetime.utcnow()

    def mark_applied(self):
        """Mark this job as applied to by the user"""
        self.is_applied = True
        self.applied_at = datetime.utcnow()

    def mark_viewed(self):
        """Mark this job as viewed by the user"""
        if not self.viewed_at:
            self.viewed_at = datetime.utcnow()

    def to_dict(self, include_job_details=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'job_posting_id': self.job_posting_id,
            'match_score': round(self.match_score, 1),
            'ai_explanation': self.ai_explanation,
            'matching_skills': self.matching_skills or [],
            'missing_skills': self.missing_skills or [],
            'skill_match_percentage': round(self.skill_match_percentage, 1) if self.skill_match_percentage else None,
            'is_saved': self.is_saved,
            'is_applied': self.is_applied,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'created_at': self.created_at.isoformat()
        }

        # Include full job details if requested
        if include_job_details and self.job_posting:
            data['job'] = self.job_posting.to_dict()
            # Calculate days ago
            if self.job_posting.posted_date:
                days_ago = (datetime.utcnow() - self.job_posting.posted_date).days
                data['job']['posted_days_ago'] = days_ago

        return data


class InterviewPrep(db.Model):
    """AI-generated interview preparation content for specific companies/roles"""
    __tablename__ = 'interview_prep'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False, index=True)
    job_title = db.Column(db.String(200), nullable=True)
    industry = db.Column(db.String(100), index=True)

    # AI-generated content
    questions = db.Column(db.JSON)  # [{"question": "...", "type": "technical/behavioral", "answer_framework": "...", "tips": "..."}]
    company_culture = db.Column(db.Text)  # AI analysis of company culture
    interview_process = db.Column(db.JSON)  # {"rounds": 3, "stages": ["phone", "technical", "final"], "duration": "2-3 weeks"}
    interview_tips = db.Column(db.JSON)  # Company-specific tips ["Tip 1", "Tip 2"]
    common_topics = db.Column(db.JSON)  # Common interview topics for this company

    # User interaction
    is_saved = db.Column(db.Boolean, default=False, index=True)
    practiced_questions = db.Column(db.JSON, default=[])  # Question IDs user has practiced

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cached_until = db.Column(db.DateTime)  # Cache expiry (1 week)

    # Relationships
    user = db.relationship('User', backref='interview_preps')

    __table_args__ = (
        db.Index('idx_prep_user_company', 'user_id', 'company'),
        db.Index('idx_prep_company', 'company'),
    )

    def __repr__(self):
        return f'<InterviewPrep user={self.user_id} company={self.company}>'

    def mark_question_practiced(self, question_index):
        """Mark a question as practiced"""
        if self.practiced_questions is None:
            self.practiced_questions = []
        if question_index not in self.practiced_questions:
            self.practiced_questions.append(question_index)
            self.practiced_questions = list(self.practiced_questions)  # Trigger update

    def is_cached(self):
        """Check if prep data is still fresh"""
        if not self.cached_until:
            return False
        return datetime.utcnow() < self.cached_until

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company': self.company,
            'job_title': self.job_title,
            'industry': self.industry,
            'questions': self.questions or [],
            'company_culture': self.company_culture,
            'interview_process': self.interview_process or {},
            'interview_tips': self.interview_tips or [],
            'common_topics': self.common_topics or [],
            'is_saved': self.is_saved,
            'practiced_questions': self.practiced_questions or [],
            'total_questions': len(self.questions) if self.questions else 0,
            'practiced_count': len(self.practiced_questions) if self.practiced_questions else 0,
            'created_at': self.created_at.isoformat(),
            'is_fresh': self.is_cached()
        }


# ============== COMPANY INTELLIGENCE MODEL ==============

class CompanyIntel(db.Model):
    """
    Company Intelligence - AI-powered company research and insights
    Stores comprehensive company information for user research
    """
    __tablename__ = 'company_intel'

    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False, index=True)
    industry = db.Column(db.String(100), index=True)

    # Company overview
    overview = db.Column(db.Text)  # Company description and history
    founded_year = db.Column(db.Integer)
    headquarters = db.Column(db.String(200))
    company_size = db.Column(db.String(200))  # "1-10", "11-50", "51-200", etc. or AI-generated descriptions
    website = db.Column(db.String(500))

    # Business information (JSON)
    products_services = db.Column(db.JSON)  # [{name, description}, ...]
    target_markets = db.Column(db.JSON)  # [market1, market2, ...]
    competitors = db.Column(db.JSON)  # [{name, comparison}, ...]

    # Culture and values
    company_culture = db.Column(db.Text)  # AI-generated culture analysis
    core_values = db.Column(db.JSON)  # [value1, value2, ...]
    work_environment = db.Column(db.Text)  # Work environment description

    # News and updates (JSON)
    recent_news = db.Column(db.JSON)  # [{title, summary, date, source}, ...]
    major_developments = db.Column(db.JSON)  # [development1, development2, ...]

    # Leadership team (JSON)
    leadership = db.Column(db.JSON)  # [{name, title, bio}, ...]

    # Financial and growth (JSON)
    financial_health = db.Column(db.JSON)  # {revenue, funding, profitability, etc.}
    growth_metrics = db.Column(db.JSON)  # {employee_growth, revenue_growth, etc.}

    # Career insights
    interview_insights = db.Column(db.Text)  # Interview process overview
    employee_sentiment = db.Column(db.Text)  # AI analysis of employee reviews
    pros_cons = db.Column(db.JSON)  # {pros: [...], cons: [...]}

    # Technology stack (JSON)
    tech_stack = db.Column(db.JSON)  # {languages: [...], frameworks: [...], tools: [...]}

    # AI-generated insights
    ai_summary = db.Column(db.Text)  # Executive summary
    key_insights = db.Column(db.JSON)  # [insight1, insight2, ...]
    recommendations = db.Column(db.JSON)  # [recommendation1, recommendation2, ...]

    # User interaction
    is_saved = db.Column(db.Boolean, default=False, index=True)
    notes = db.Column(db.Text)  # User's personal notes

    # Timestamps and caching
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cached_until = db.Column(db.DateTime)  # 14-day cache for company intel

    # Relationships
    user = db.relationship('User', backref=db.backref('company_intels', lazy='dynamic'))

    def __repr__(self):
        return f'<CompanyIntel {self.company} for User {self.user_id}>'

    def is_cached(self):
        """Check if company intel is still cached (fresh)"""
        if not self.cached_until:
            return False
        return datetime.utcnow() < self.cached_until

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'company': self.company,
            'industry': self.industry,
            'overview': self.overview,
            'founded_year': self.founded_year,
            'headquarters': self.headquarters,
            'company_size': self.company_size,
            'website': self.website,
            'products_services': self.products_services,
            'target_markets': self.target_markets,
            'competitors': self.competitors,
            'company_culture': self.company_culture,
            'core_values': self.core_values,
            'work_environment': self.work_environment,
            'recent_news': self.recent_news,
            'major_developments': self.major_developments,
            'leadership': self.leadership,
            'financial_health': self.financial_health,
            'growth_metrics': self.growth_metrics,
            'interview_insights': self.interview_insights,
            'employee_sentiment': self.employee_sentiment,
            'pros_cons': self.pros_cons,
            'tech_stack': self.tech_stack,
            'ai_summary': self.ai_summary,
            'key_insights': self.key_insights,
            'recommendations': self.recommendations,
            'is_saved': self.is_saved,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cached_until': self.cached_until.isoformat() if self.cached_until else None,
            'is_fresh': self.is_cached()
        }


class CareerPath(db.Model):
    """
    Career Path - AI-generated career progression roadmaps
    Provides personalized career advancement strategies and roadmaps
    """
    __tablename__ = 'career_path'

    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Career positions
    current_role = db.Column(db.String(200), nullable=False, index=True)
    target_role = db.Column(db.String(200), nullable=False, index=True)
    industry = db.Column(db.String(100), index=True)
    years_of_experience = db.Column(db.Integer)

    # Path overview
    path_summary = db.Column(db.Text)
    estimated_duration = db.Column(db.String(100))  # "2-3 years", "6-12 months", etc.
    difficulty_level = db.Column(db.String(50))  # "Beginner-friendly", "Moderate", "Challenging"

    # Career steps (JSON array of step objects)
    # [{step_number, title, description, duration, skills_to_acquire, key_actions, certifications}]
    career_steps = db.Column(db.JSON)

    # Skills analysis
    current_skills = db.Column(db.JSON)  # Skills user currently has
    skills_gap = db.Column(db.JSON)  # Skills needed to acquire
    transferable_skills = db.Column(db.JSON)  # Skills that transfer well

    # Learning resources (JSON)
    # [{type, title, url, description, cost, priority}]
    learning_resources = db.Column(db.JSON)

    # Certifications recommended
    # [{name, provider, cost, duration, priority, relevance}]
    certifications = db.Column(db.JSON)

    # Salary progression
    # [{role, min_salary, max_salary, median_salary}]
    salary_expectations = db.Column(db.JSON)

    # Alternative paths
    # [{path_name, description, duration, steps_summary}]
    alternative_paths = db.Column(db.JSON)

    # Networking and mentorship
    networking_tips = db.Column(db.Text)
    mentor_guidance = db.Column(db.Text)
    industry_connections = db.Column(db.JSON)  # Where to connect

    # Success metrics
    # [{milestone, timeframe, success_criteria, importance}]
    key_milestones = db.Column(db.JSON)

    # Success stories (anonymized case studies)
    # [{profile, transition_time, key_factors, advice}]
    success_stories = db.Column(db.JSON)

    # AI insights
    ai_recommendations = db.Column(db.Text)

    # Risk and success factors
    # [{"factor": "...", "impact": "high/medium/low", "mitigation": "..."}]
    risk_factors = db.Column(db.JSON)
    success_factors = db.Column(db.JSON)

    # Market insights
    job_market_outlook = db.Column(db.Text)
    demand_trend = db.Column(db.String(50))  # "Growing", "Stable", "Declining"

    # User interaction
    is_saved = db.Column(db.Boolean, default=False, index=True)
    notes = db.Column(db.Text)  # Personal career planning notes

    # Progress tracking (user can mark steps complete)
    # {step_1: {completed: true, date: "...", notes: "..."}, ...}
    progress_tracking = db.Column(db.JSON, default=dict)

    # Timestamps and caching
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cached_until = db.Column(db.DateTime)  # 30-day cache for career paths

    def is_cached(self):
        """Check if career path is still cached (fresh)"""
        if not self.cached_until:
            return False
        return datetime.utcnow() < self.cached_until

    def get_completion_percentage(self):
        """Calculate what percentage of steps are completed"""
        if not self.progress_tracking or not self.career_steps:
            return 0

        completed_steps = sum(
            1 for step_key, progress in self.progress_tracking.items()
            if progress.get('completed', False)
        )
        total_steps = len(self.career_steps)

        return (completed_steps / total_steps * 100) if total_steps > 0 else 0

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'current_role': self.current_role,
            'target_role': self.target_role,
            'industry': self.industry,
            'years_of_experience': self.years_of_experience,

            'path_summary': self.path_summary,
            'estimated_duration': self.estimated_duration,
            'difficulty_level': self.difficulty_level,

            'career_steps': self.career_steps or [],

            'current_skills': self.current_skills or [],
            'skills_gap': self.skills_gap or [],
            'transferable_skills': self.transferable_skills or [],

            'learning_resources': self.learning_resources or [],
            'certifications': self.certifications or [],

            'salary_expectations': self.salary_expectations or [],
            'alternative_paths': self.alternative_paths or [],

            'networking_tips': self.networking_tips,
            'mentor_guidance': self.mentor_guidance,
            'industry_connections': self.industry_connections or [],

            'key_milestones': self.key_milestones or [],
            'success_stories': self.success_stories or [],

            'ai_recommendations': self.ai_recommendations,
            'risk_factors': self.risk_factors or [],
            'success_factors': self.success_factors or [],

            'job_market_outlook': self.job_market_outlook,
            'demand_trend': self.demand_trend,

            'is_saved': self.is_saved,
            'notes': self.notes,
            'progress_tracking': self.progress_tracking or {},
            'completion_percentage': self.get_completion_percentage(),

            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cached_until': self.cached_until.isoformat() if self.cached_until else None,
            'is_fresh': self.is_cached()
        }


class Purchase(db.Model):
    """Purchase model for tracking micro-transactions and one-time purchases"""
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Purchase details
    purchase_type = db.Column(db.String(50), nullable=False, index=True)  # 'single_rescan', 'weekly_pass', 'credits_pack'
    amount_usd = db.Column(db.Float, nullable=False)  # Amount paid in USD
    credits_granted = db.Column(db.Integer, default=0)  # Credits added to account

    # For time-limited purchases (weekly pass)
    access_expires_at = db.Column(db.DateTime, nullable=True, index=True)  # When the pass expires
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Is the purchase still active/valid

    # Payment details
    stripe_payment_intent_id = db.Column(db.String(255), unique=True, nullable=True)
    stripe_charge_id = db.Column(db.String(255), unique=True, nullable=True)
    payment_status = db.Column(db.String(50), default='pending', nullable=False)  # pending, succeeded, failed, refunded
    payment_method = db.Column(db.String(50), nullable=True)  # card, apple_pay, google_pay

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('purchases', lazy=True))

    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_user_purchase_type', 'user_id', 'purchase_type'),
        db.Index('idx_purchase_expires', 'user_id', 'access_expires_at'),
        db.Index('idx_payment_intent', 'stripe_payment_intent_id'),
    )

    def __repr__(self):
        return f'<Purchase {self.id} - {self.purchase_type} for User {self.user_id}>'

    def is_expired(self):
        """Check if time-limited purchase has expired"""
        if not self.access_expires_at:
            return False
        return datetime.utcnow() > self.access_expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'purchase_type': self.purchase_type,
            'amount_usd': self.amount_usd,
            'credits_granted': self.credits_granted,
            'access_expires_at': self.access_expires_at.isoformat() if self.access_expires_at else None,
            'is_active': self.is_active and not self.is_expired(),
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
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


class Feedback(db.Model):
    """Feedback model for user submissions"""
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    category = db.Column(db.String(50), nullable=False, default='general')  # general, bug, feature, support, praise
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optional - if logged in
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Feedback {self.id} - {self.category} - {self.rating}/5>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'rating': self.rating,
            'category': self.category,
            'message': self.message,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class JobApplication(db.Model):
    """Job Application Tracker model for tracking job applications"""
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Job Details
    company_name = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    job_url = db.Column(db.String(500))
    job_description = db.Column(db.Text)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    location = db.Column(db.String(200))
    work_type = db.Column(db.String(50))  # remote, hybrid, onsite

    # Application Status
    # Statuses: saved, applied, phone_screen, interview, offer, rejected, withdrawn, accepted
    status = db.Column(db.String(50), nullable=False, default='saved', index=True)

    # Important Dates
    date_saved = db.Column(db.DateTime, default=datetime.utcnow)
    date_applied = db.Column(db.DateTime)
    date_response = db.Column(db.DateTime)
    date_interview = db.Column(db.DateTime)
    follow_up_date = db.Column(db.DateTime)

    # Notes & Tracking
    notes = db.Column(db.Text)
    resume_version = db.Column(db.String(200))  # Which resume version was used
    cover_letter_used = db.Column(db.Boolean, default=False)
    referral_contact = db.Column(db.String(200))
    interview_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.String(500))

    # UI State
    is_starred = db.Column(db.Boolean, default=False, index=True)
    is_archived = db.Column(db.Boolean, default=False, index=True)

    # Linked Analysis (optional)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_job_app_user_status', 'user_id', 'status'),
        db.Index('idx_job_app_user_created', 'user_id', 'created_at'),
        db.Index('idx_job_app_user_starred', 'user_id', 'is_starred'),
        db.Index('idx_job_app_follow_up', 'user_id', 'follow_up_date'),
    )

    # Relationship
    user = db.relationship('User', backref=db.backref('job_applications', lazy='dynamic'))
    analysis = db.relationship('Analysis', backref=db.backref('job_application', uselist=False))

    def __repr__(self):
        return f'<JobApplication {self.id} - {self.company_name} - {self.job_title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'job_url': self.job_url,
            'job_description': self.job_description,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'location': self.location,
            'work_type': self.work_type,
            'status': self.status,
            'date_saved': self.date_saved.isoformat() if self.date_saved else None,
            'date_applied': self.date_applied.isoformat() if self.date_applied else None,
            'date_response': self.date_response.isoformat() if self.date_response else None,
            'date_interview': self.date_interview.isoformat() if self.date_interview else None,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'notes': self.notes,
            'resume_version': self.resume_version,
            'cover_letter_used': self.cover_letter_used,
            'referral_contact': self.referral_contact,
            'interview_notes': self.interview_notes,
            'rejection_reason': self.rejection_reason,
            'is_starred': self.is_starred,
            'is_archived': self.is_archived,
            'analysis_id': self.analysis_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Initialize schemas
user_schema = UserSchema()
analysis_schema = AnalysisSchema()
analysis_create_schema = AnalysisCreateSchema()
