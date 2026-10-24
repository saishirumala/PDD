# Supabase Backend Connection Setup Package

This folder contains all files required to connect your backend to Supabase automatically.

## Included Files

- `connect_supabase.py`: Automated CLI diagnostic and database table provisioning script.
- `supabase_service.py`: Service class for testing and managing Supabase REST API connection.
- `config.py`: Configuration settings loader for Supabase credentials.
- `database.py`: SQLAlchemy database connection manager supporting Supabase PostgreSQL.

## Quick Start

1. Copy these files to your backend directory or keep them in this folder.
2. Run the connection command:
   ```bash
   python connect_supabase.py
   ```
