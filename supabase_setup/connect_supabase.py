#!/usr/bin/env python3
"""
NutriGuide Supabase Automated Connection & Diagnostic Script
Run: python connect_supabase.py
"""

import sys
import os
from pathlib import Path

# Setup paths
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from dotenv import load_dotenv

env_path = current_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from sqlalchemy import text
from config import settings
from database import engine, Base
from supabase_service import supabase_service
import models  # Ensure models are imported

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_banner():
    print("=" * 65)
    print("      NUTRIGUIDE SUPABASE AUTOMATIC CONNECTION DIAGNOSTIC      ")
    print("=" * 65)

def check_env():
    print("\n[1/4] Checking Environment Configuration...")
    print(f"  * SUPABASE_URL            : {settings.SUPABASE_URL or 'NOT SET'}")
    print(f"  * SUPABASE_PUBLISHABLE_KEY: {'[PRESENT]' if settings.SUPABASE_PUBLISHABLE_KEY else 'NOT SET'}")
    print(f"  * SUPABASE_SECRET_KEY     : {'[PRESENT]' if settings.SUPABASE_SECRET_KEY else 'NOT SET'}")
    print(f"  * Effective DB URL        : {settings.effective_db_url}")

def check_supabase_api():
    print("\n[2/4] Testing Supabase REST API Connection...")
    success, msg, details = supabase_service.test_connection()
    if success:
        print(f"  [OK] {msg}")
        for k, v in details.items():
            print(f"       - {k}: {v}")
    else:
        print(f"  [WARN] {msg}")
    return success

def check_and_provision_db():
    print("\n[3/4] Testing Database Connection & Provisioning Tables...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print("  [OK] Database connection successful! (SELECT 1 returned 1)")

        print("  * Provisioning / verifying database tables...")
        Base.metadata.create_all(bind=engine)
        print("  [OK] All database tables provisioned successfully!")
        return True
    except Exception as e:
        print(f"  [FAIL] Database connection/provisioning error: {e}")
        print("\n  [TIP] If using PostgreSQL on Supabase, set SUPABASE_DB_URL in .env:")
        print("        SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.nnwovklgbgmdoemymkyy.supabase.co:5432/postgres")
        return False

def print_summary(api_ok, db_ok):
    print("\n[4/4] Connection Summary:")
    print("=" * 65)
    print(f"  * Supabase API Status : {'[OK] CONNECTED' if api_ok else '[FAIL] DISCONNECTED'}")
    print(f"  * Database Status     : {'[OK] CONNECTED & READY' if db_ok else '[WARN] DB ISSUE DETECTED'}")
    print("=" * 65)

def main():
    print_banner()
    check_env()
    api_ok = check_supabase_api()
    db_ok = check_and_provision_db()
    print_summary(api_ok, db_ok)
    
    if api_ok or db_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
