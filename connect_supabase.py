#!/usr/bin/env python3
"""
Root wrapper for NutriGuide Supabase Automatic Connection Script
Run from project root: python connect_supabase.py
"""
import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import and execute main from backend/connect_supabase.py
from connect_supabase import main

if __name__ == "__main__":
    main()
