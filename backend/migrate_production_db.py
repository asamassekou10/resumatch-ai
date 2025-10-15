from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        print("Starting database migration...")
        
        # Add missing columns
        commands = [
            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS name VARCHAR(100);',
            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS google_id VARCHAR(100) UNIQUE;',
            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);',
            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) DEFAULT \'email\';',
            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;',
            'ALTER TABLE "user" ALTER COLUMN password_hash DROP NOT NULL;'
        ]
        
        for command in commands:
            try:
                db.session.execute(text(command))
                print(f"✅ Executed: {command[:50]}...")
            except Exception as e:
                print(f"⚠️ Warning: {str(e)}")
        
        db.session.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.session.rollback()