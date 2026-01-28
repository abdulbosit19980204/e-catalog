import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    core_tables = [t for t in tables if t.startswith('core_')]
    print(f"CORE TABLES FOUND: {core_tables}")
    
    for ct in ['core_systemsettings', 'core_aitokenusage', 'core_aimodel']:
        status = "EXISTS" if ct in tables else "MISSING"
        print(f" - {ct}: {status}")
    
    if 'core_aimodel' not in tables:
        print("\nAttempting to MANUALLY create core_aimodel table...")
        try:
            cursor.execute("""
                CREATE TABLE "core_aimodel" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "is_active" bool NOT NULL,
                    "is_deleted" bool NOT NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "name" varchar(100) NOT NULL,
                    "model_id" varchar(255) NOT NULL UNIQUE,
                    "provider" varchar(50) NOT NULL,
                    "is_default" bool NOT NULL,
                    "meta_data" json NOT NULL
                );
            """)
            conn.commit()
            print("SUCCESS: core_aimodel table created manually.")
            
            # Seed initial data
            from datetime import datetime
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"""
                INSERT INTO "core_aimodel" (is_active, is_deleted, created_at, updated_at, name, model_id, provider, is_default, meta_data)
                VALUES (1, 0, '{now}', '{now}', 'Gemini 2.5 Flash', 'models/gemini-2.5-flash', 'google', 1, '{{}}');
            """)
            cursor.execute(f"""
                INSERT INTO "core_aimodel" (is_active, is_deleted, created_at, updated_at, name, model_id, provider, is_default, meta_data)
                VALUES (1, 0, '{now}', '{now}', 'Gemini 1.5 Pro', 'models/gemini-1.5-pro', 'google', 0, '{{}}');
            """)
            conn.commit()
            print("SUCCESS: Initial models seeded.")
            
            # Record migration as applied
            cursor.execute(f"""
                INSERT INTO "django_migrations" (app, name, applied)
                VALUES ('core', '0004_aimodel_alter_systemsettings_field_type', '{now}');
            """)
            conn.commit()
            print("SUCCESS: Migration 0004 recorded as applied.")
            
        except Exception as e:
            print(f"FAILED to create table manually: {e}")
    else:
        print("\nSUCCESS: core_aimodel table exists.")
    
    conn.close()
