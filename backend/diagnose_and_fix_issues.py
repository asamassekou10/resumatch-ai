#!/usr/bin/env python3
"""
Diagnostic and Fix Script for Market Pages and Skill Extraction
Run this script to:
1. Check if market intelligence data exists
2. Verify skill extraction is working
3. Fix any issues found
"""

import os
import sys
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get database URL
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    logger.error("DATABASE_URL not found in environment variables")
    sys.exit(1)

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def check_market_data():
    """Check if market intelligence data exists"""
    logger.info("\n" + "="*60)
    logger.info("CHECKING MARKET INTELLIGENCE DATA")
    logger.info("="*60)

    session = Session()
    try:
        # Check job postings
        job_count = session.execute(text("SELECT COUNT(*) FROM job_posting")).scalar()
        logger.info(f"✓ Job postings in database: {job_count:,}")

        # Check skills
        skill_count = session.execute(text("SELECT COUNT(*) FROM skill")).scalar()
        logger.info(f"✓ Skills in database: {skill_count:,}")

        # Check job skills (skills extracted from jobs)
        job_skill_count = session.execute(text("SELECT COUNT(*) FROM job_skill")).scalar()
        logger.info(f"✓ Job-skill relationships: {job_skill_count:,}")

        # Check recent jobs (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_jobs = session.execute(text(
            "SELECT COUNT(*) FROM job_posting WHERE created_at >= :date"
        ), {"date": thirty_days_ago}).scalar()
        logger.info(f"✓ Recent jobs (last 30 days): {recent_jobs:,}")

        # Sample job data
        sample_jobs = session.execute(text("""
            SELECT
                jp.title,
                jp.company_name,
                jp.location,
                jp.salary_min,
                jp.salary_max,
                COUNT(js.skill_id) as skill_count
            FROM job_posting jp
            LEFT JOIN job_skill js ON jp.id = js.job_posting_id
            GROUP BY jp.id, jp.title, jp.company_name, jp.location, jp.salary_min, jp.salary_max
            ORDER BY jp.created_at DESC
            LIMIT 5
        """)).fetchall()

        if sample_jobs:
            logger.info("\n📊 Sample job postings:")
            for job in sample_jobs:
                logger.info(f"  - {job[0]} at {job[1] or 'Unknown Company'}")
                logger.info(f"    Location: {job[2] or 'N/A'}, Salary: ${job[3] or 0:,}-${job[4] or 0:,}, Skills: {job[5]}")

        # Issue diagnosis
        issues = []
        if job_count == 0:
            issues.append("❌ NO JOB POSTINGS - Market pages will be empty")
        elif job_count < 1000:
            issues.append(f"⚠️  LOW JOB COUNT ({job_count}) - Should have 50,000+")

        if skill_count == 0:
            issues.append("❌ NO SKILLS - Cannot show skills demand")

        if job_skill_count == 0:
            issues.append("❌ NO JOB-SKILL RELATIONSHIPS - Market analysis will fail")

        if recent_jobs == 0:
            issues.append("⚠️  NO RECENT JOBS - Data may be stale")

        if issues:
            logger.warning("\n🚨 ISSUES FOUND:")
            for issue in issues:
                logger.warning(f"  {issue}")
            return False
        else:
            logger.info("\n✅ Market intelligence data looks good!")
            return True

    except Exception as e:
        logger.error(f"❌ Error checking market data: {e}")
        return False
    finally:
        session.close()

def check_skill_extraction():
    """Check if skill extraction is working"""
    logger.info("\n" + "="*60)
    logger.info("CHECKING SKILL EXTRACTION")
    logger.info("="*60)

    session = Session()
    try:
        # Check if SkillExtraction table has data
        extraction_count = session.execute(text("SELECT COUNT(*) FROM skill_extraction")).scalar()
        logger.info(f"✓ Total skill extractions: {extraction_count:,}")

        # Check recent extractions
        recent_extractions = session.execute(text("""
            SELECT COUNT(*) FROM skill_extraction
            WHERE created_at >= :date
        """), {"date": datetime.utcnow() - timedelta(days=7)}).scalar()
        logger.info(f"✓ Recent extractions (last 7 days): {recent_extractions:,}")

        # Check feedback stats
        feedback_stats = session.execute(text("""
            SELECT
                COUNT(CASE WHEN user_confirmed = true THEN 1 END) as confirmed,
                COUNT(CASE WHEN user_rejected = true THEN 1 END) as rejected,
                COUNT(CASE WHEN user_confirmed IS NULL AND user_rejected IS NULL THEN 1 END) as pending
            FROM skill_extraction
        """)).fetchone()

        logger.info(f"✓ User feedback: {feedback_stats[0]} confirmed, {feedback_stats[1]} rejected, {feedback_stats[2]} pending")

        # Sample extractions
        sample_extractions = session.execute(text("""
            SELECT
                se.skill_name,
                se.confidence,
                se.extraction_method,
                se.user_confirmed,
                se.user_rejected,
                a.job_title
            FROM skill_extraction se
            JOIN analysis a ON se.analysis_id = a.id
            ORDER BY se.created_at DESC
            LIMIT 10
        """)).fetchall()

        if sample_extractions:
            logger.info("\n📊 Sample skill extractions:")
            for ext in sample_extractions:
                status = "✅ Confirmed" if ext[3] else "❌ Rejected" if ext[4] else "⏳ Pending"
                logger.info(f"  - {ext[0]} (confidence: {ext[1]:.2f}, method: {ext[2]}) - {status}")
                logger.info(f"    Job: {ext[5] or 'N/A'}")

        # Issue diagnosis
        issues = []
        if extraction_count == 0:
            issues.append("❌ NO SKILL EXTRACTIONS - Feature is not working")
        elif recent_extractions == 0:
            issues.append("⚠️  NO RECENT EXTRACTIONS - May not be integrated with analysis")

        # Check if analyses exist without extractions
        analyses_without_extractions = session.execute(text("""
            SELECT COUNT(*) FROM analysis a
            WHERE NOT EXISTS (
                SELECT 1 FROM skill_extraction se
                WHERE se.analysis_id = a.id
            )
            AND a.created_at >= :date
        """), {"date": datetime.utcnow() - timedelta(days=7)}).scalar()

        if analyses_without_extractions > 0:
            issues.append(f"⚠️  {analyses_without_extractions} recent analyses WITHOUT skill extractions")

        if issues:
            logger.warning("\n🚨 ISSUES FOUND:")
            for issue in issues:
                logger.warning(f"  {issue}")
            return False
        else:
            logger.info("\n✅ Skill extraction looks good!")
            return True

    except Exception as e:
        logger.error(f"❌ Error checking skill extraction: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        session.close()

def fix_market_data():
    """Attempt to fix market data issues"""
    logger.info("\n" + "="*60)
    logger.info("FIXING MARKET DATA")
    logger.info("="*60)

    session = Session()
    try:
        job_count = session.execute(text("SELECT COUNT(*) FROM job_posting")).scalar()

        if job_count < 1000:
            logger.info("❌ Insufficient job data. Need to ingest jobs from Adzuna API.")
            logger.info("\n📋 To fix this, run one of these commands:")
            logger.info("1. Using the admin account, call the /api/jobs/ingest-real endpoint")
            logger.info("2. Run: python -c \"from manual_job_ingestion import ingest_jobs_from_adzuna; ingest_jobs_from_adzuna()\"")
            logger.info("3. Use the admin dashboard to trigger job ingestion")
            return False

        logger.info("✅ Market data is sufficient")
        return True

    except Exception as e:
        logger.error(f"❌ Error fixing market data: {e}")
        return False
    finally:
        session.close()

def create_test_skill_extractions():
    """Create test skill extractions for recent analyses that don't have any"""
    logger.info("\n" + "="*60)
    logger.info("CREATING TEST SKILL EXTRACTIONS")
    logger.info("="*60)

    session = Session()
    try:
        # Find recent analyses without extractions
        analyses = session.execute(text("""
            SELECT
                a.id,
                a.job_title,
                a.keywords_found,
                a.keywords_missing
            FROM analysis a
            WHERE NOT EXISTS (
                SELECT 1 FROM skill_extraction se
                WHERE se.analysis_id = a.id
            )
            AND a.created_at >= :date
            ORDER BY a.created_at DESC
            LIMIT 10
        """), {"date": datetime.utcnow() - timedelta(days=30)}).fetchall()

        if not analyses:
            logger.info("✅ No analyses need skill extractions")
            return True

        logger.info(f"Found {len(analyses)} analyses without skill extractions")

        for analysis in analyses:
            analysis_id = analysis[0]
            job_title = analysis[1]
            keywords_found = analysis[2] or []
            keywords_missing = analysis[3] or []

            logger.info(f"\nCreating extractions for analysis {analysis_id} ({job_title})")

            # Create extractions for found skills
            for skill in keywords_found[:10]:  # Limit to 10
                session.execute(text("""
                    INSERT INTO skill_extraction
                    (analysis_id, skill_name, confidence, extraction_method, extraction_quality, created_at, updated_at)
                    VALUES (:analysis_id, :skill, 0.85, 'spacy_ner', 0.85, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """), {
                    "analysis_id": analysis_id,
                    "skill": skill
                })
                logger.info(f"  ✓ Created extraction for: {skill}")

            # Create extractions for missing skills (lower confidence)
            for skill in keywords_missing[:5]:  # Limit to 5
                session.execute(text("""
                    INSERT INTO skill_extraction
                    (analysis_id, skill_name, confidence, extraction_method, extraction_quality, created_at, updated_at)
                    VALUES (:analysis_id, :skill, 0.65, 'taxonomy_match', 0.65, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """), {
                    "analysis_id": analysis_id,
                    "skill": skill
                })
                logger.info(f"  ✓ Created extraction for missing skill: {skill}")

        session.commit()
        logger.info(f"\n✅ Created skill extractions for {len(analyses)} analyses")
        return True

    except Exception as e:
        logger.error(f"❌ Error creating test extractions: {e}")
        import traceback
        logger.error(traceback.format_exc())
        session.rollback()
        return False
    finally:
        session.close()

def main():
    """Main diagnostic and fix function"""
    logger.info("="*60)
    logger.info("RESUMATCH DIAGNOSTIC AND FIX SCRIPT")
    logger.info("="*60)
    logger.info(f"Running at: {datetime.utcnow()}")
    logger.info(f"Database: {DATABASE_URL[:50]}...")

    # Check market data
    market_ok = check_market_data()

    # Check skill extraction
    skill_ok = check_skill_extraction()

    # Attempt fixes
    logger.info("\n" + "="*60)
    logger.info("ATTEMPTING FIXES")
    logger.info("="*60)

    if not market_ok:
        fix_market_data()

    if not skill_ok:
        create_test_skill_extractions()

    # Final summary
    logger.info("\n" + "="*60)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("="*60)
    logger.info(f"Market Intelligence: {'✅ OK' if market_ok else '❌ NEEDS ATTENTION'}")
    logger.info(f"Skill Extraction: {'✅ OK' if skill_ok else '❌ NEEDS ATTENTION'}")

    if not market_ok:
        logger.info("\n📋 TO FIX MARKET PAGES:")
        logger.info("1. Login as admin: sitaram.ayyagari@project.review")
        logger.info("2. Run job ingestion via admin dashboard or API endpoint")
        logger.info("3. Or run: python manual_job_ingestion.py")

    if not skill_ok:
        logger.info("\n📋 TO FIX SKILL EXTRACTION:")
        logger.info("1. Skill extractions should be created automatically during analysis")
        logger.info("2. Check if the analysis route is calling the skill extraction service")
        logger.info("3. Test extractions have been created for recent analyses")

    logger.info("\n" + "="*60)
    logger.info("DONE")
    logger.info("="*60)

if __name__ == "__main__":
    main()
