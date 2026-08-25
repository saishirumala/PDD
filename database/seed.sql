-- Seed script for NutriGuide
-- Adds a test user 'Jane Doe' with email 'jane@example.com' (password is hashed for 'Password123')

INSERT INTO users (name, email, password_hash, calorie_goal, protein_goal, carbs_goal, fat_goal, fiber_goal)
VALUES (
    'Jane Doe', 
    'jane@example.com', 
    '$2b$12$6K.Wskk9g88qR19hBv.jDuC.KxS9yVvD1ZkK6x6F5G5y5y5y5y5y5', -- mock bcrypt hash
    2000, 
    130.0, 
    240.0, 
    60.0, 
    25.0
) ON CONFLICT (email) DO NOTHING;
