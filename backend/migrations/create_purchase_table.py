"""
Create Purchase table for micro-transactions
"""

from datetime import datetime
from models import db

def upgrade():
    """Create purchases table"""
    db.engine.execute("""
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

        CREATE INDEX IF NOT EXISTS idx_user_purchase_type ON purchases(user_id, purchase_type);
        CREATE INDEX IF NOT EXISTS idx_purchase_expires ON purchases(user_id, access_expires_at);
        CREATE INDEX IF NOT EXISTS idx_payment_intent ON purchases(stripe_payment_intent_id);
        CREATE INDEX IF NOT EXISTS idx_purchase_user_id ON purchases(user_id);
        CREATE INDEX IF NOT EXISTS idx_purchase_created ON purchases(created_at);
        CREATE INDEX IF NOT EXISTS idx_purchase_type ON purchases(purchase_type);
    """)

    print("✅ Created purchases table with indexes")

def downgrade():
    """Drop purchases table"""
    db.engine.execute("DROP TABLE IF EXISTS purchases CASCADE;")
    print("❌ Dropped purchases table")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        upgrade()
