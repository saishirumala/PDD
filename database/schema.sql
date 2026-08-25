-- NutriGuide Database Schema

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    calorie_goal INTEGER DEFAULT 2000,
    protein_goal REAL DEFAULT 150.0,
    carbs_goal REAL DEFAULT 225.0,
    fat_goal REAL DEFAULT 65.0,
    fiber_goal REAL DEFAULT 30.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    meal_name VARCHAR(200) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nutrition (
    id SERIAL PRIMARY KEY,
    meal_id INTEGER NOT NULL UNIQUE REFERENCES meals(id) ON DELETE CASCADE,
    calories INTEGER NOT NULL,
    protein REAL NOT NULL,
    carbohydrates REAL NOT NULL,
    fat REAL NOT NULL,
    fiber REAL NOT NULL,
    sugar REAL NOT NULL,
    sodium REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS micronutrients (
    id SERIAL PRIMARY KEY,
    meal_id INTEGER NOT NULL UNIQUE REFERENCES meals(id) ON DELETE CASCADE,
    iron REAL DEFAULT 0.0,
    calcium REAL DEFAULT 0.0,
    magnesium REAL DEFAULT 0.0,
    potassium REAL DEFAULT 0.0,
    vitamin_a REAL DEFAULT 0.0,
    vitamin_c REAL DEFAULT 0.0,
    vitamin_d REAL DEFAULT 0.0,
    vitamin_b12 REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS foods (
    id SERIAL PRIMARY KEY,
    meal_id INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    estimated_quantity VARCHAR(100) NOT NULL,
    calories INTEGER NOT NULL,
    protein REAL NOT NULL,
    carbohydrates REAL NOT NULL,
    fat REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS meal_insights (
    id SERIAL PRIMARY KEY,
    meal_id INTEGER NOT NULL UNIQUE REFERENCES meals(id) ON DELETE CASCADE,
    health_score INTEGER NOT NULL,
    summary TEXT NOT NULL,
    recommendations JSON NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS water_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount_ml INTEGER NOT NULL,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_meals_user_id ON meals(user_id);
CREATE INDEX IF NOT EXISTS idx_foods_meal_id ON foods(meal_id);
CREATE INDEX IF NOT EXISTS idx_water_logs_user_id ON water_logs(user_id);
