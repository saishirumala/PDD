export interface User {
  id: number;
  name: string;
  email: string;
  calorie_goal: number;
  protein_goal: number;
  carbs_goal: number;
  fat_goal: number;
  fiber_goal: number;
  created_at: string;
}

export interface Food {
  id: number;
  meal_id: number;
  name: string;
  estimated_quantity: string;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
}

export interface Nutrition {
  id: number;
  meal_id: number;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  fiber: number;
  sugar: number;
  sodium: number;
}

export interface Micronutrients {
  id: number;
  meal_id: number;
  iron: number;
  calcium: number;
  magnesium: number;
  potassium: number;
  vitamin_a: number;
  vitamin_c: number;
  vitamin_d: number;
  vitamin_b12: number;
}

export interface MealInsight {
  id: number;
  meal_id: number;
  health_score: number;
  summary: string;
  recommendations: string[];
}

export interface Meal {
  id: number;
  user_id: number;
  meal_name: string;
  description: string | null;
  image_url: string | null;
  analyzed_at: string;
  created_at: string;
  nutrition: Nutrition;
  micronutrients: Micronutrients;
  foods: Food[];
  insight: MealInsight;
}

export interface DailyNutritionSummary {
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  fiber: number;
  calorie_goal: number;
  protein_goal: number;
  carbs_goal: number;
  fat_goal: number;
  fiber_goal: number;
}

export interface DashboardTodayResponse {
  today: DailyNutritionSummary;
  meals_count: number;
  average_health_score: number;
  meals: Meal[];
}

export interface WeeklyChartItem {
  day: string;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  meals_count: number;
}

export interface DashboardSummaryResponse {
  weekly_chart: WeeklyChartItem[];
  total_meals: number;
  average_health_score: number;
}

export interface WaterLog {
  id: number;
  user_id: number;
  amount_ml: number;
  logged_at: string;
}

export interface WaterSummaryResponse {
  total_ml: number;
  goal_ml: number;
  logs: WaterLog[];
}
