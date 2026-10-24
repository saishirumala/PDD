-- Supabase Migration SQL: Populate All 7 Existing Users into public.users Table

-- 1. Ensure RLS Policy allows inserting and reading
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public user registration" ON public.users;
DROP POLICY IF EXISTS "Allow public select users" ON public.users;

CREATE POLICY "Allow public user registration" ON public.users FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select users" ON public.users FOR SELECT USING (true);

-- 2. Insert all 7 existing users into public.users table
INSERT INTO public.users (name, email, password_hash, calorie_goal, protein_goal, carbs_goal, fat_goal, fiber_goal)
VALUES 
    ('sai', 'saishirumala05@gmail.com', '$2b$12$demo_hash_placeholder_1', 2000, 150.0, 225.0, 65.0, 30.0),
    ('sai', 'shirumala.sai2004@gmail.com', '$2b$12$demo_hash_placeholder_2', 2000, 150.0, 225.0, 65.0, 30.0),
    ('madhava', 'sivasainathreddys5114.sse@saveetha.com', '$2b$12$demo_hash_placeholder_3', 2000, 150.0, 225.0, 65.0, 30.0),
    ('Test User', 'testnewuser99@example.com', '$2b$12$demo_hash_placeholder_4', 2000, 150.0, 225.0, 65.0, 30.0),
    ('rishith', 'reddysab2005@gmail.com', '$2b$12$demo_hash_placeholder_5', 2000, 150.0, 225.0, 65.0, 30.0),
    ('New Test User', 'newuser123@example.com', '$2b$12$demo_hash_placeholder_6', 2000, 150.0, 225.0, 65.0, 30.0),
    ('Automatic User', 'autouser_test@gmail.com', '$2b$12$demo_hash_placeholder_7', 2000, 150.0, 225.0, 65.0, 30.0)
ON CONFLICT (email) DO NOTHING;
