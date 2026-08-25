from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    calorie_goal = Column(Integer, default=2000)
    protein_goal = Column(Float, default=150.0) # grams
    carbs_goal = Column(Float, default=225.0)   # grams
    fat_goal = Column(Float, default=65.0)     # grams
    fiber_goal = Column(Float, default=30.0)   # grams
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    water_logs = relationship("WaterLog", back_populates="user", cascade="all, delete-orphan")


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meal_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="meals")
    nutrition = relationship("Nutrition", back_populates="meal", uselist=False, cascade="all, delete-orphan")
    micronutrients = relationship("Micronutrient", back_populates="meal", uselist=False, cascade="all, delete-orphan")
    foods = relationship("Food", back_populates="meal", cascade="all, delete-orphan")
    insight = relationship("MealInsight", back_populates="meal", uselist=False, cascade="all, delete-orphan")


class Nutrition(Base):
    __tablename__ = "nutrition"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), unique=True, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    fiber = Column(Float, nullable=False)
    sugar = Column(Float, nullable=False)
    sodium = Column(Float, nullable=False)

    meal = relationship("Meal", back_populates="nutrition")


class Micronutrient(Base):
    __tablename__ = "micronutrients"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), unique=True, nullable=False)
    iron = Column(Float, default=0.0)
    calcium = Column(Float, default=0.0)
    magnesium = Column(Float, default=0.0)
    potassium = Column(Float, default=0.0)
    vitamin_a = Column(Float, default=0.0)
    vitamin_c = Column(Float, default=0.0)
    vitamin_d = Column(Float, default=0.0)
    vitamin_b12 = Column(Float, default=0.0)

    meal = relationship("Meal", back_populates="micronutrients")


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    estimated_quantity = Column(String(100), nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)

    meal = relationship("Meal", back_populates="foods")


class MealInsight(Base):
    __tablename__ = "meal_insights"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), unique=True, nullable=False)
    health_score = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    recommendations = Column(JSON, nullable=False) # Store lists of recommendations
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meal = relationship("Meal", back_populates="insight")


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount_ml = Column(Integer, nullable=False)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="water_logs")
