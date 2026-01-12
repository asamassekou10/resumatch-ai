"""
Create purchases table - run this in production
Usage: python create_purchases_table.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def create_purchases_table():
    """Create purchases table with all indexes"""
    with app.app_context():
        try:
            # Create purchases table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

                    purchase_type VARCHAR(50) NOT NULL,
                    amount_usd FLOAT NOT NULL,
                    credits_granted INTEGER DEFAULT 0,

                    access_expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,

                    stripe_payment_intent_id VARCHAR(255) UNIQUE,
                    stripe_charge_id VARCHAR(255) UNIQUE,
                    payment_status VARCHAR(50) DEFAULT 'pending' NOT NULL,
                    payment_method VARCHAR(50),

                    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
                );
            """))

            # Create indexes
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_purchase_type ON purchases(user_id, purchase_type);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_expires ON purchases(user_id, access_expires_at);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_payment_intent ON purchases(stripe_payment_intent_id);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_user_id ON purchases(user_id);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_created ON purchases(created_at);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_type ON purchases(purchase_type);"))

            db.session.commit()

            print("✅ Successfully created purchases table with indexes")
            print("✅ Table: purchases")
            print("✅ Indexes: 6 created")

            # Verify table exists
            result = db.session.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'purchases'
            """))

            if result.fetchone():
                print("✅ Verified: purchases table exists")
            else:
                print("❌ Warning: Could not verify table creation")

        except Exception as e:
            print(f"❌ Error creating purchases table: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_purchases_table()
