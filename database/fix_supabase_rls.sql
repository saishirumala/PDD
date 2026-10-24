-- Fix Supabase Row-Level Security (RLS) Policy for 'users' Table
-- Run this script in your Supabase Dashboard -> SQL Editor to allow signups from web frontend

-- 1. Enable RLS on users table (if not already enabled)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- 2. Drop existing policy if present
DROP POLICY IF EXISTS "Allow public user registration" ON public.users;
DROP POLICY IF EXISTS "Allow public select users" ON public.users;

-- 3. Create INSERT policy allowing anonymous/publishable key signups
CREATE POLICY "Allow public user registration"
ON public.users
FOR INSERT
WITH CHECK (true);

-- 4. Create SELECT policy allowing reading user records
CREATE POLICY "Allow public select users"
ON public.users
FOR SELECT
USING (true);
