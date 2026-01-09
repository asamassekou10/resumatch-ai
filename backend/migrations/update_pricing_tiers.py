"""
Update pricing tiers to match market research and add missing tiers
This migration adds starter, basic, student, and elite tiers with revised pricing
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def update_pricing_tiers():
    """Update subscription tiers with revised pricing structure"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("UPDATING PRICING TIERS")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        conn = engine.connect()
        print("✅ Connected to database")
        print()

        # Clear existing tiers
        print("1. Clearing existing tiers...")
        conn.execute(text("DELETE FROM subscription_tier"))
        conn.commit()
        print("   ✅ Existing tiers cleared")
        print()

        # Insert new tier structure
        print("2. Inserting updated tiers...")
        conn.execute(text("""
            INSERT INTO subscription_tier
            (name, display_name, description, monthly_credits, price_cents, max_analyses_per_month, max_file_size_mb, max_concurrent_uploads, position, is_active, features)
            VALUES
                (
                    'free',
                    'Free',
                    'Try before you buy',
                    10,
                    0,
                    10,
                    5,
                    1,
                    1,
                    true,
                    '{"resume_analysis": true, "keyword_matching": true, "basic_feedback": true, "ai_optimization": false, "cover_letter": false, "priority_support": false, "launch_tier": true}'::jsonb
                ),
                (
                    'starter',
                    'Starter',
                    'Essential tools for job seekers',
                    15,
                    999,
                    15,
                    10,
                    2,
                    2,
                    false,
                    '{"resume_analysis": true, "keyword_matching": true, "basic_feedback": true, "ai_feedback": true, "ai_optimization": false, "cover_letter": false, "priority_support": false, "ats_scan": true, "available_after_launch": true}'::jsonb
                ),
                (
                    'pro',
                    'Pro',
                    'For active job seekers',
                    50,
                    2499,
                    50,
                    16,
                    5,
                    3,
                    true,
                    '{"resume_analysis": true, "keyword_matching": true, "basic_feedback": true, "ai_feedback": true, "ai_optimization": true, "cover_letter": true, "priority_support": true, "ats_scan": true, "unlimited_templates": true}'::jsonb
                ),
                (
                    'pro_founding',
                    'Pro - Founding Member',
                    'Limited time: Lock in $19.99 forever',
                    50,
                    1999,
                    50,
                    16,
                    5,
                    4,
                    true,
                    '{"resume_analysis": true, "keyword_matching": true, "basic_feedback": true, "ai_feedback": true, "ai_optimization": true, "cover_letter": true, "priority_support": true, "ats_scan": true, "unlimited_templates": true, "founding_member": true, "lifetime_lock": true, "badge": "Founding Member"}'::jsonb
                ),
                (
                    'pro_annual',
                    'Pro Annual',
                    'Pro plan billed annually (save 33%)',
                    50,
                    19900,
                    50,
                    16,
                    5,
                    5,
                    false,
                    '{"resume_analysis": true, "keyword_matching": true, "basic_feedback": true, "ai_feedback": true, "ai_optimization": true, "cover_letter": true, "priority_support": true, "ats_scan": true, "unlimited_templates": true, "billing_period": "annual", "available_after_launch": true}'::jsonb
                ),
                (
                    'elite',
                    'Elite',
                    'For recruiters and career coaches',
                    200,
                    4999,
                    200,
                    50,
                    10,
                    6,
                    true,
                    '{"resume_analysis": true, "keyword_matching": true, "basic_feedback": true, "ai_feedback": true, "ai_optimization": true, "cover_letter": true, "priority_support": true, "ats_scan": true, "unlimited_templates": true, "api_access": true, "bulk_upload": true, "white_label": true, "dedicated_support": true}'::jsonb
                )
        """))
        conn.commit()
        print("   ✅ New tiers inserted")
        print()

        # Verify
        print("3. Verification...")
        result = conn.execute(text("SELECT name, display_name, monthly_credits, price_cents FROM subscription_tier ORDER BY position"))
        tiers = result.fetchall()

        print("   Tiers in database:")
        for tier in tiers:
            price_dollars = tier[3] / 100 if tier[3] > 0 else 0
            print(f"   - {tier[1]}: {tier[2]} credits/month at ${price_dollars:.2f}")
        print()

        print("=" * 60)
        print("✅ PRICING TIERS UPDATED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Update Stripe Price IDs in environment variables")
        print("  2. Create corresponding products in Stripe Dashboard")
        print("  3. Update frontend pricing page to match new tiers")
        print()

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = update_pricing_tiers()
    sys.exit(0 if success else 1)
