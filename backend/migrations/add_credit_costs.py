"""
Add credit costs to RateLimitConfig for all operations and tiers
Defines how many credits each operation costs per tier
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def add_credit_costs():
    """Add credit cost configurations for all operations"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("ADDING CREDIT COST CONFIGURATIONS")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        conn = engine.connect()
        print("✅ Connected to database")
        print()

        # Clear existing rate limit configs
        print("1. Clearing existing rate limit configs...")
        conn.execute(text("DELETE FROM rate_limit_config"))
        conn.commit()
        print("   ✅ Existing configs cleared")
        print()

        # Insert credit cost configurations
        print("2. Inserting credit cost configurations...")
        conn.execute(text("""
            INSERT INTO rate_limit_config
            (operation, subscription_tier, requests_per_hour, requests_per_day, requests_per_month, cost_in_credits, description)
            VALUES
                -- Free tier (Launch: 10 credits)
                ('resume_analysis', 'free', 5, 10, 10, 1, 'Basic resume analysis for free users - launch tier'),
                ('feedback_generation', 'free', 0, 0, 0, 0, 'Not available in free tier'),
                ('optimization', 'free', 0, 0, 0, 0, 'Not available in free tier'),
                ('cover_letter', 'free', 0, 0, 0, 0, 'Not available in free tier'),

                -- Starter tier
                ('resume_analysis', 'starter', 10, 15, 15, 1, 'Basic resume analysis'),
                ('feedback_generation', 'starter', 5, 10, 15, 1, 'AI feedback generation'),
                ('optimization', 'starter', 0, 0, 0, 0, 'Not available in starter tier'),
                ('cover_letter', 'starter', 0, 0, 0, 0, 'Not available in starter tier'),

                -- Pro tier
                ('resume_analysis', 'pro', 20, 50, 50, 1, 'Resume analysis'),
                ('feedback_generation', 'pro', 20, 50, 50, 2, 'Detailed AI feedback'),
                ('optimization', 'pro', 15, 30, 50, 3, 'AI-powered optimization'),
                ('cover_letter', 'pro', 10, 20, 25, 2, 'Cover letter generation'),

                -- Pro Founding (same as pro)
                ('resume_analysis', 'pro_founding', 20, 50, 50, 1, 'Resume analysis - Founding Member'),
                ('feedback_generation', 'pro_founding', 20, 50, 50, 2, 'Detailed AI feedback - Founding Member'),
                ('optimization', 'pro_founding', 15, 30, 50, 3, 'AI-powered optimization - Founding Member'),
                ('cover_letter', 'pro_founding', 10, 20, 25, 2, 'Cover letter generation - Founding Member'),

                -- Pro Annual (same as pro)
                ('resume_analysis', 'pro_annual', 20, 50, 50, 1, 'Resume analysis'),
                ('feedback_generation', 'pro_annual', 20, 50, 50, 2, 'Detailed AI feedback'),
                ('optimization', 'pro_annual', 15, 30, 50, 3, 'AI-powered optimization'),
                ('cover_letter', 'pro_annual', 10, 20, 25, 2, 'Cover letter generation'),

                -- Elite tier
                ('resume_analysis', 'elite', 100, 200, 200, 1, 'Resume analysis'),
                ('feedback_generation', 'elite', 100, 200, 200, 2, 'Detailed AI feedback'),
                ('optimization', 'elite', 75, 150, 200, 3, 'AI-powered optimization'),
                ('cover_letter', 'elite', 50, 100, 100, 2, 'Cover letter generation'),
                ('bulk_upload', 'elite', 10, 20, 50, 5, 'Bulk resume upload'),

                -- Student tier
                ('resume_analysis', 'student', 15, 30, 30, 1, 'Resume analysis'),
                ('feedback_generation', 'student', 10, 25, 30, 1, 'AI feedback generation'),
                ('career_guidance', 'student', 5, 10, 15, 2, 'Career path guidance'),
                ('optimization', 'student', 0, 0, 0, 0, 'Not available in student tier'),
                ('cover_letter', 'student', 0, 0, 0, 0, 'Not available in student tier')
        """))
        conn.commit()
        print("   ✅ Credit costs configured")
        print()

        # Verify
        print("3. Verification...")
        result = conn.execute(text("""
            SELECT subscription_tier, operation, cost_in_credits, requests_per_month
            FROM rate_limit_config
            ORDER BY subscription_tier, operation
        """))
        configs = result.fetchall()

        current_tier = None
        for config in configs:
            if config[0] != current_tier:
                current_tier = config[0]
                print(f"\n   {current_tier.upper()}:")
            print(f"     - {config[1]}: {config[2]} credit(s) | {config[3]} per month")
        print()

        print("=" * 60)
        print("✅ CREDIT COSTS CONFIGURED SUCCESSFULLY!")
        print("=" * 60)
        print()

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = add_credit_costs()
    sys.exit(0 if success else 1)
