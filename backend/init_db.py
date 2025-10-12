@"
from app import app, db

with app.app_context():
    db.create_all()
    print('✅ Database tables created successfully!')
"@ | Out-File -FilePath init_db.py -Encoding utf8