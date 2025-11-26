"""
Initialize hierarchical skill taxonomy with 500+ skills across all industries

This script populates the database with a comprehensive skill taxonomy organized by:
- Level 0: Root industries (IT, Business, Creative, Healthcare, Education, Soft Skills)
- Level 1: Categories (Backend, Frontend, Sales, Design, etc.)
- Level 2: Subcategories (Python Frameworks, Design Tools, etc.)
- Level 3: Actual skills (Python, Django, Flask, Figma, etc.)

Run with: docker-compose exec backend python init_hierarchical_taxonomy.py
"""

import logging
import os
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_hierarchical_taxonomy():
    """Initialize hierarchical skill taxonomy database"""
    # Import Flask and create a fresh app context (like init_keywords.py does)
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/resume_optimizer')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)

    from hierarchical_taxonomy import SKILL_TAXONOMY

    # Import required for models BEFORE app context
    from datetime import datetime
    from sqlalchemy import Column, String, Integer, JSON, Float, Boolean, DateTime, ForeignKey

    # Define Keyword model inline to use this db instance
    class Keyword(db.Model):
        __tablename__ = 'keywords'
        id = Column(Integer, primary_key=True)
        keyword = Column(String(100), unique=True, nullable=False, index=True)
        keyword_type = Column(String(50), nullable=False)
        category = Column(String(100), nullable=False, index=True)
        priority = Column(String(20), default='medium', nullable=False)
        difficulty_level = Column(String(20), default='intermediate')
        average_salary_premium = Column(Float)
        parent_keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=True)
        hierarchy_level = Column(Integer, default=2)
        extraction_patterns = Column(JSON, default=[])
        extraction_count = Column(Integer, default=0)
        user_confirmed_count = Column(Integer, default=0)
        user_rejected_count = Column(Integer, default=0)
        extraction_accuracy = Column(Float, default=1.0)
        co_occurrence_patterns = Column(JSON, default={})
        skill_co_occurrence_count = Column(Integer, default=0)
        job_postings_containing = Column(Integer, default=0)
        market_demand_score = Column(Float, default=0.5)
        salary_trend = Column(JSON, default={})
        trend_direction = Column(String(20), default='stable')
        source = Column(String(50), default='manual')
        last_verified_at = Column(DateTime)
        industry_relevance = Column(JSON, default={})
        synonyms = Column(JSON, default=[])
        related_keywords = Column(JSON, default=[])
        confidence_score = Column(Float, default=1.0)
        is_deprecated = Column(Boolean, default=False)
        year_popularity = Column(JSON, default={})
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define SkillTaxonomy model inline to use this db instance
    class SkillTaxonomy(db.Model):
        __tablename__ = 'skill_taxonomy'
        id = Column(Integer, primary_key=True)
        name = Column(String(200), nullable=False, unique=True)
        level = Column(Integer, nullable=False)  # 0=industry, 1=category, 2=subcategory
        parent_id = Column(Integer, ForeignKey('skill_taxonomy.id'), nullable=True)
        description = Column(String(500))
        keywords_count = Column(Integer, default=0)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    with app.app_context():
        # Drop and recreate keywords and skill_taxonomy tables to apply new schema
        try:
            db.session.execute('DROP TABLE IF EXISTS keywords CASCADE')
            db.session.execute('DROP TABLE IF EXISTS skill_taxonomy CASCADE')
            db.session.commit()
            logger.info("Old tables dropped")
        except Exception as e:
            logger.warning(f"Could not drop old tables: {e}")
            db.session.rollback()

        # Create tables with new schema (models are now registered with db)
        db.create_all()
        logger.info("Database tables created/verified with new schema")

        added_skills_count = 0
        skipped_count = 0
        taxonomy_entries = 0

        # Dictionary to store keyword IDs for parent references
        keyword_cache = {}

        logger.info("\n" + "="*70)
        logger.info("INITIALIZING HIERARCHICAL SKILL TAXONOMY")
        logger.info("="*70)

        # Process each root industry (Level 0)
        for industry_name, industry_data in SKILL_TAXONOMY.items():
            logger.info(f"\n📁 Processing Industry: {industry_name}")

            # Create or get Level 0 SkillTaxonomy entry for this industry
            industry_taxonomy = SkillTaxonomy.query.filter_by(
                name=industry_name,
                level=0
            ).first()

            if not industry_taxonomy:
                industry_taxonomy = SkillTaxonomy(
                    name=industry_name,
                    level=0,
                    description=industry_data.get('description', ''),
                    keywords_count=0
                )
                db.session.add(industry_taxonomy)
                db.session.flush()
                taxonomy_entries += 1
                logger.info(f"  ✓ Created taxonomy entry for {industry_name}")
            else:
                logger.info(f"  ℹ Taxonomy entry exists for {industry_name}")

            # Process categories (Level 1)
            for category_name, category_data in industry_data.get('categories', {}).items():
                logger.info(f"  📂 Category: {category_name}")

                # Create Level 1 taxonomy entry
                category_taxonomy = SkillTaxonomy.query.filter_by(
                    name=category_name,
                    level=1,
                    parent_id=industry_taxonomy.id
                ).first()

                if not category_taxonomy:
                    category_taxonomy = SkillTaxonomy(
                        name=category_name,
                        level=1,
                        parent_id=industry_taxonomy.id,
                        description=category_data.get('description', ''),
                        keywords_count=0
                    )
                    db.session.add(category_taxonomy)
                    db.session.flush()
                    taxonomy_entries += 1
                    logger.info(f"    ✓ Created taxonomy entry for {category_name}")

                # Process subcategories and skills (Level 2 & 3)
                for subcategory_name, subcategory_data in category_data.get('subcategories', {}).items():
                    # Create Level 2 taxonomy entry
                    subcategory_taxonomy = SkillTaxonomy.query.filter_by(
                        name=subcategory_name,
                        level=2,
                        parent_id=category_taxonomy.id
                    ).first()

                    if not subcategory_taxonomy:
                        subcategory_taxonomy = SkillTaxonomy(
                            name=subcategory_name,
                            level=2,
                            parent_id=category_taxonomy.id,
                            description=subcategory_data.get('description', ''),
                            keywords_count=0
                        )
                        db.session.add(subcategory_taxonomy)
                        db.session.flush()
                        taxonomy_entries += 1

                    # Process actual skills
                    for skill_data in subcategory_data.get('skills', []):
                        skill_name = skill_data.get('name', '').lower().strip()

                        if not skill_name:
                            continue

                        # Check if skill already exists
                        existing_skill = Keyword.query.filter_by(keyword=skill_name).first()

                        if existing_skill:
                            logger.debug(f"    ⊘ Skipping {skill_name} - already exists")
                            skipped_count += 1
                            continue

                        # Create keyword entry with hierarchy
                        keyword = Keyword(
                            keyword=skill_name,
                            keyword_type='skill',
                            category=category_name.lower(),
                            priority=skill_data.get('priority', 'medium'),
                            difficulty_level=skill_data.get('difficulty', 'intermediate'),
                            average_salary_premium=skill_data.get('salary_premium', 0),
                            # Hierarchy support
                            parent_keyword_id=None,  # Will be set for skill variants
                            hierarchy_level=3,  # Level 3 = actual skills
                            # Source tracking
                            source='hierarchical_taxonomy',
                            last_verified_at=datetime.utcnow(),
                            # Initialize ML tracking fields
                            extraction_patterns=[],
                            extraction_count=0,
                            user_confirmed_count=0,
                            user_rejected_count=0,
                            extraction_accuracy=1.0,
                            # Relationship tracking
                            co_occurrence_patterns={},
                            skill_co_occurrence_count=0,
                            # Market intelligence
                            job_postings_containing=0,
                            market_demand_score=0.5,
                            salary_trend={},
                            trend_direction='stable',
                            # Default values
                            industry_relevance={industry_name.lower(): 0.9},
                            synonyms=[],
                            related_keywords=[],
                            confidence_score=1.0,
                            is_deprecated=False,
                            year_popularity={}
                        )

                        db.session.add(keyword)
                        db.session.flush()
                        keyword_cache[skill_name] = keyword.id
                        added_skills_count += 1

                        # Update taxonomy keywords count
                        subcategory_taxonomy.keywords_count = (subcategory_taxonomy.keywords_count or 0) + 1

                        if added_skills_count % 50 == 0:
                            logger.info(f"    → Added {added_skills_count} skills so far...")

                    # Log summary for subcategory
                    if subcategory_data.get('skills'):
                        logger.info(f"      ✓ {subcategory_name}: {len(subcategory_data['skills'])} skills processed")

        # Commit all changes
        db.session.commit()

        # Log final summary
        logger.info("\n" + "="*70)
        logger.info("INITIALIZATION COMPLETE")
        logger.info("="*70)
        logger.info(f"\n✅ Summary:")
        logger.info(f"   • Skills Added: {added_skills_count}")
        logger.info(f"   • Skills Skipped (duplicates): {skipped_count}")
        logger.info(f"   • Taxonomy Entries Created: {taxonomy_entries}")

        # Get statistics
        total_skills = Keyword.query.filter_by(source='hierarchical_taxonomy').count()
        logger.info(f"\n📊 Database Statistics:")
        logger.info(f"   • Total hierarchical skills: {total_skills}")

        # Skills by category
        categories = db.session.query(
            Keyword.category,
            db.func.count(Keyword.id)
        ).filter_by(source='hierarchical_taxonomy').group_by(Keyword.category).all()

        logger.info(f"\n📂 Skills by Category:")
        for category, count in sorted(categories, key=lambda x: x[1], reverse=True):
            logger.info(f"   • {category}: {count} skills")

        # Skills by priority
        priorities = db.session.query(
            Keyword.priority,
            db.func.count(Keyword.id)
        ).filter_by(source='hierarchical_taxonomy').group_by(Keyword.priority).all()

        logger.info(f"\n⭐ Skills by Priority:")
        for priority, count in sorted(priorities):
            logger.info(f"   • {priority}: {count} skills")

        # Taxonomy structure
        taxonomy_levels = db.session.query(
            SkillTaxonomy.level,
            db.func.count(SkillTaxonomy.id)
        ).group_by(SkillTaxonomy.level).all()

        logger.info(f"\n🏗️  Taxonomy Structure:")
        for level, count in sorted(taxonomy_levels):
            level_names = {0: "Industries", 1: "Categories", 2: "Subcategories"}
            logger.info(f"   • Level {level} ({level_names.get(level, 'Unknown')}): {count} entries")

        logger.info("\n" + "="*70)
        logger.info("✅ HIERARCHICAL TAXONOMY INITIALIZATION SUCCESSFUL!")
        logger.info("="*70 + "\n")

        return {
            'skills_added': added_skills_count,
            'skills_skipped': skipped_count,
            'taxonomy_entries': taxonomy_entries,
            'total_skills': total_skills
        }


if __name__ == '__main__':
    try:
        results = init_hierarchical_taxonomy()
        logger.info(f"Results: {results}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
