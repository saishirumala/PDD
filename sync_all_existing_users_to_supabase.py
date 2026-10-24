#!/usr/bin/env python3
"""
Sync all existing users from NutriGuide backend database to Supabase Auth and REST API.
"""

import os
import sys
import time
import sqlite3
import httpx
from pathlib import Path

def sync_existing_users():
    print("=" * 65)
    print("      SYNCING ALL EXISTING DATABASE USERS TO SUPABASE      ")
    print("=" * 65)

    supabase_url = "https://nnwovklgbgmdoemymkyy.supabase.co"
    key = "sb_publishable_kJDTDsyMSbqvd1-uqAo8cQ_3n-qFzcs"

    # Locate local sqlite db file
    db_paths = [
        Path("backend/nutriguide.db"),
        Path("nutriguide.db")
    ]
    
    db_file = None
    for p in db_paths:
        if p.exists():
            db_file = p
            break

    if not db_file:
        print("[FAIL] Could not locate nutriguide.db file!")
        return

    print(f"[INFO] Connecting to local database: {db_file.resolve()}")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, calorie_goal, protein_goal, carbs_goal, fat_goal, fiber_goal FROM users")
    rows = cursor.fetchall()
    conn.close()

    print(f"[INFO] Found {len(rows)} users in local backend database.\n")

    auth_url = f"{supabase_url}/auth/v1/signup"
    headers = {
        "apikey": key,
        "Content-Type": "application/json"
    }

    synced_count = 0
    for row in rows:
        user_id, name, email, cal, prot, carbs, fat, fiber = row
        clean_email = email.strip()

        # Fix placeholder domains if needed for Supabase Auth validator
        if clean_email.endswith("@example.com"):
            clean_email = clean_email.replace("@example.com", "@nutriguide.ai")

        print(f"-> Syncing User #{user_id}: {name} ({clean_email})...")

        payload = {
            "email": clean_email,
            "password": "DefaultPassword123!",
            "data": {
                "name": name,
                "user_id": user_id,
                "calorie_goal": cal,
                "protein_goal": prot,
                "carbs_goal": carbs,
                "fat_goal": fat,
                "fiber_goal": fiber
            }
        }

        try:
            resp = httpx.post(auth_url, headers=headers, json=payload, timeout=10.0)
            if resp.status_code in (200, 201):
                print(f"   [OK] Successfully synced to Supabase Auth! (HTTP {resp.status_code})")
                synced_count += 1
            elif resp.status_code == 422 or "already registered" in resp.text.lower():
                print(f"   [INFO] User already exists in Supabase Auth.")
                synced_count += 1
            else:
                print(f"   [WARN] Sync response HTTP {resp.status_code}: {resp.text[:150]}")
        except Exception as exc:
            print(f"   [FAIL] Exception during sync: {exc}")

        time.sleep(1.0)

    print("\n" + "=" * 65)
    print(f"  SYNC COMPLETE: {synced_count}/{len(rows)} users processed into Supabase!")
    print("=" * 65)

if __name__ == "__main__":
    sync_existing_users()
