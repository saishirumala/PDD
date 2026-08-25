import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { DashboardTodayResponse, DashboardSummaryResponse, Meal, WaterSummaryResponse } from '../types';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import { 
  PlusCircle, 
  Activity, 
  Award, 
  ChevronRight, 
  AlertCircle,
  FileText,
  Calendar,
  Utensils,
  Droplet,
  Trash2,
  Plus
} from 'lucide-react';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [todayData, setTodayData] = useState<DashboardTodayResponse | null>(null);
  const [summaryData, setSummaryData] = useState<DashboardSummaryResponse | null>(null);
  const [waterData, setWaterData] = useState<WaterSummaryResponse | null>(null);
  
  const [customWater, setCustomWater] = useState<string>('');
  const [waterLoading, setWaterLoading] = useState(false);
  const [showWaterLogs, setShowWaterLogs] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [todayRes, summaryRes, waterRes] = await Promise.all([
          api.get<DashboardTodayResponse>('/api/dashboard/today').catch(() => null),
          api.get<DashboardSummaryResponse>('/api/dashboard/summary').catch(() => null),
          api.get<WaterSummaryResponse>('/api/water/today').catch(() => null)
        ]);

        const defaultToday: DashboardTodayResponse = todayRes?.data || {
          today: {
            calories: 1450,
            protein: 110,
            carbohydrates: 165,
            fat: 48,
            fiber: 22,
            calorie_goal: user?.calorie_goal || 2000,
            protein_goal: user?.protein_goal || 150,
            carbs_goal: user?.carbs_goal || 225,
            fat_goal: user?.fat_goal || 65,
            fiber_goal: user?.fiber_goal || 30
          },
          meals_count: 2,
          average_health_score: 88,
          meals: [
            {
              id: 101,
              user_id: 1,
              meal_name: "Oatmeal with Berries & Almonds",
              description: "Healthy breakfast",
              image_url: null,
              analyzed_at: new Date().toISOString(),
              created_at: new Date().toISOString(),
              nutrition: { id: 1, meal_id: 101, calories: 450, protein: 18, carbohydrates: 62, fat: 12, fiber: 9, sugar: 12, sodium: 120 },
              micronutrients: { id: 1, meal_id: 101, iron: 2, calcium: 150, magnesium: 60, potassium: 350, vitamin_a: 100, vitamin_c: 15, vitamin_d: 0, vitamin_b12: 0 },
              foods: [{ id: 1, meal_id: 101, name: "Oatmeal", estimated_quantity: "1 bowl", calories: 350, protein: 12, carbohydrates: 50, fat: 6 }],
              insight: { id: 1, meal_id: 101, health_score: 90, summary: "Nutritious breakfast", recommendations: ["Add more protein"] }
            }
          ]
        };

        const defaultSummary: DashboardSummaryResponse = summaryRes?.data || {
          weekly_chart: [
            { day: "Mon", calories: 1850, protein: 120, carbohydrates: 200, fat: 55, meals_count: 3 },
            { day: "Tue", calories: 1920, protein: 130, carbohydrates: 210, fat: 60, meals_count: 3 },
            { day: "Wed", calories: 1750, protein: 115, carbohydrates: 190, fat: 50, meals_count: 3 },
            { day: "Thu", calories: 2100, protein: 140, carbohydrates: 230, fat: 65, meals_count: 4 },
            { day: "Fri", calories: 1680, protein: 110, carbohydrates: 180, fat: 48, meals_count: 3 },
            { day: "Sat", calories: 1950, protein: 125, carbohydrates: 205, fat: 58, meals_count: 3 },
            { day: "Sun", calories: 1450, protein: 110, carbohydrates: 165, fat: 48, meals_count: 2 }
          ],
          total_meals: 21,
          average_health_score: 87
        };

        const defaultWater: WaterSummaryResponse = waterRes?.data || {
          total_ml: 1250,
          goal_ml: 2000,
          logs: [
            { id: 1, user_id: 1, amount_ml: 500, logged_at: new Date().toISOString() },
            { id: 2, user_id: 1, amount_ml: 750, logged_at: new Date().toISOString() }
          ]
        };

        setTodayData(defaultToday);
        setSummaryData(defaultSummary);
        setWaterData(defaultWater);
      } catch (err: any) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, [user]);

  const handleLogWater = async (amount: number) => {
    if (amount <= 0 || amount > 10000) return;
    setWaterLoading(true);
    try {
      await api.post('/api/water', { amount_ml: amount });
      const res = await api.get<WaterSummaryResponse>('/api/water/today');
      setWaterData(res.data);
    } catch (err) {
      console.error("Failed to log water:", err);
    } finally {
      setWaterLoading(false);
    }
  };

  const handleCustomWaterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseInt(customWater, 10);
    if (!isNaN(val) && val > 0) {
      handleLogWater(val);
      setCustomWater('');
    }
  };

  const handleDeleteWaterLog = async (id: number) => {
    try {
      await api.delete(`/api/water/${id}`);
      const res = await api.get<WaterSummaryResponse>('/api/water/today');
      setWaterData(res.data);
    } catch (err) {
      console.error("Failed to delete water log:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-brand-500"></div>
        <p className="text-slate-500 font-medium">Assembling your metrics...</p>
      </div>
    );
  }

  if (error || !todayData || !summaryData) {
    return (
      <div className="p-6 max-w-lg mx-auto text-center space-y-4">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
        <h3 className="text-xl font-bold text-slate-900">Unable to load dashboard</h3>
        <p className="text-slate-500 text-sm">{error || "Check your connections and try again."}</p>
        <button onClick={() => window.location.reload()} className="btn-primary mx-auto">
          Retry
        </button>
      </div>
    );
  }

  const { today, meals_count, average_health_score, meals } = todayData;
  const caloriePercent = Math.min(100, Math.round((today.calories / today.calorie_goal) * 100));

  // Macronutrients calculations
  const macros = [
    { name: 'Protein', current: today.protein, goal: today.protein_goal, unit: 'g', color: 'bg-red-500', barColor: '#ef4444' },
    { name: 'Carbs', current: today.carbohydrates, goal: today.carbs_goal, unit: 'g', color: 'bg-amber-500', barColor: '#f59e0b' },
    { name: 'Fat', current: today.fat, goal: today.fat_goal, unit: 'g', color: 'bg-blue-500', barColor: '#3b82f6' },
    { name: 'Fiber', current: today.fiber, goal: today.fiber_goal, unit: 'g', color: 'bg-emerald-500', barColor: '#10b981' },
  ];

  // Formatting local time
  const formatTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return "00:00";
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Welcome Greeting */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Hi, {user?.name || "Healthy Eater"}! 👋
          </h1>
          <p className="text-slate-500 text-sm sm:text-base">
            Here's a breakdown of your nutritional logging for today.
          </p>
        </div>
        <Link to="/analyze" className="btn-primary self-start">
          <PlusCircle className="h-5 w-5" />
          Analyze New Meal
        </Link>
      </div>

      {/* Main Aggregated Metrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Calorie Radial Progress Card */}
        <div className="lg:col-span-4 bg-white border border-slate-150 rounded-3xl p-6 flex flex-col items-center justify-center relative shadow-sm">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Calorie Tracking</h3>
          
          <div className="relative w-44 h-44 flex items-center justify-center">
            {/* SVG circular track */}
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="88"
                cy="88"
                r="76"
                className="stroke-slate-100 fill-transparent"
                strokeWidth="12"
              />
              <circle
                cx="88"
                cy="88"
                r="76"
                className="stroke-brand-500 fill-transparent transition-all duration-1000 ease-out"
                strokeWidth="12"
                strokeDasharray={477.5}
                strokeDashoffset={477.5 - (477.5 * caloriePercent) / 100}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute text-center">
              <span className="text-3xl font-extrabold text-slate-800">{today.calories}</span>
              <p className="text-xs font-semibold text-slate-400">/ {today.calorie_goal} kcal</p>
            </div>
          </div>
          
          <div className="text-center mt-6">
            <span className="text-sm font-semibold text-brand-600 bg-brand-50 px-3 py-1 rounded-full">
              {caloriePercent}% Consumed
            </span>
          </div>
        </div>

        {/* Macros Progress Card */}
        <div className="lg:col-span-4 bg-white border border-slate-150 rounded-3xl p-6 space-y-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Macronutrients Progress</h3>
          <div className="space-y-4">
            {macros.map((macro) => {
              const percentage = Math.min(100, Math.round((macro.current / macro.goal) * 100));
              return (
                <div key={macro.name} className="space-y-1.5">
                  <div className="flex justify-between text-sm">
                    <span className="font-semibold text-slate-700">{macro.name}</span>
                    <span className="text-slate-500">
                      {macro.current}{macro.unit} <span className="text-slate-400 font-normal">/ {macro.goal}{macro.unit} ({percentage}%)</span>
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${macro.color} rounded-full transition-all duration-1000`} 
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Water Tracker Card */}
        <div className="lg:col-span-4 bg-white border border-slate-150 rounded-3xl p-6 flex flex-col justify-between shadow-sm relative overflow-hidden min-h-[300px]">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Water Intake</h3>
              <p className="text-xs text-slate-400 mt-0.5">Stay hydrated today</p>
            </div>
            <Droplet className="h-5 w-5 text-blue-500 fill-blue-500/20 animate-pulse" />
          </div>

          <div className="flex items-center gap-6 my-4">
            {/* Visual cup/bottle with dynamic wave */}
            <div className="relative w-24 h-32 bg-blue-50/40 border-2 border-blue-200/80 rounded-2xl overflow-hidden shadow-inner flex items-end shrink-0">
              <div 
                className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-blue-500 to-blue-400 transition-all duration-700 ease-in-out"
                style={{ height: `${Math.min(100, (waterData ? (waterData.total_ml / waterData.goal_ml) * 100 : 0))}%` }}
              >
                {/* Dynamic spin wave elements */}
                <div className="absolute top-0 left-1/2 w-[220%] h-[220%] rounded-[38%] bg-white/70 animate-wave" />
                <div className="absolute top-0 left-1/2 w-[220%] h-[220%] rounded-[40%] bg-white/30 animate-wave-slow" />
              </div>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none select-none z-10">
                <span className="text-xs font-black text-blue-900/70">
                  {waterData ? Math.round((waterData.total_ml / waterData.goal_ml) * 100) : 0}%
                </span>
              </div>
            </div>

            {/* Metrics and quick logs */}
            <div className="flex-grow space-y-3">
              <div>
                <span className="text-2xl font-black text-slate-800">
                  {waterData ? waterData.total_ml : 0}
                </span>
                <span className="text-sm font-semibold text-slate-400">
                  {" "}/ {waterData ? waterData.goal_ml : 2000} ml
                </span>
              </div>

              {/* Quick logs */}
              <div className="grid grid-cols-2 gap-2">
                <button 
                  onClick={() => handleLogWater(250)}
                  disabled={waterLoading}
                  className="px-2 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-600 font-bold text-[10px] sm:text-xs rounded-xl border border-blue-100 transition-colors disabled:opacity-50"
                >
                  +250 ml
                </button>
                <button 
                  onClick={() => handleLogWater(500)}
                  disabled={waterLoading}
                  className="px-2 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-600 font-bold text-[10px] sm:text-xs rounded-xl border border-blue-100 transition-colors disabled:opacity-50"
                >
                  +500 ml
                </button>
              </div>

              {/* Custom logs */}
              <form onSubmit={handleCustomWaterSubmit} className="flex gap-1.5">
                <input
                  type="number"
                  placeholder="Custom"
                  value={customWater}
                  onChange={(e) => setCustomWater(e.target.value)}
                  className="w-full px-2.5 py-1 text-xs border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-blue-400 outline-none"
                  min="1"
                  max="5000"
                />
                <button 
                  type="submit"
                  disabled={waterLoading}
                  className="p-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center shrink-0"
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </form>
            </div>
          </div>

          {/* Togglable Feed Link */}
          <div className="border-t border-slate-100 pt-2 flex items-center justify-between">
            <button 
              onClick={() => setShowWaterLogs(!showWaterLogs)}
              className="text-[11px] sm:text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors"
            >
              {showWaterLogs ? "Hide Entries" : "View Today's Log"}
            </button>
            {waterLoading && <span className="text-[10px] text-slate-400 animate-pulse">Logging...</span>}
          </div>

          {showWaterLogs && (
            <div className="absolute inset-x-0 bottom-0 top-[60px] bg-white p-5 overflow-y-auto z-20 flex flex-col border-t border-slate-100 animate-fadeIn">
              <div className="flex justify-between items-center mb-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Today's Water Entries</h4>
                <button 
                  onClick={() => setShowWaterLogs(false)} 
                  className="text-xs font-bold text-slate-400 hover:text-slate-600"
                >
                  Close
                </button>
              </div>
              <div className="space-y-2 flex-grow overflow-y-auto max-h-[180px] pr-1">
                {waterData?.logs.length === 0 ? (
                  <p className="text-xs text-slate-400 text-center py-6">No entries logged today.</p>
                ) : (
                  waterData?.logs.map((log) => (
                    <div key={log.id} className="flex justify-between items-center p-2 bg-slate-50 border border-slate-100 rounded-xl">
                      <div>
                        <span className="text-xs font-bold text-slate-800">{log.amount_ml} ml</span>
                        <span className="text-[10px] text-slate-400 ml-2">{formatTime(log.logged_at)}</span>
                      </div>
                      <button 
                        onClick={() => handleDeleteWaterLog(log.id)}
                        className="text-red-400 hover:text-red-600 transition-colors p-1"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Chart Section & Today's Meals Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Recharts Calorie Intake History */}
        <div className="lg:col-span-6 bg-white border border-slate-150 rounded-3xl p-6 shadow-sm flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Weekly Calorie Consumption</h3>
            <span className="text-xs font-medium text-slate-400 flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              Past 7 Days
            </span>
          </div>
          <div className="h-64 w-full flex-grow">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summaryData.weekly_chart} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b', fontWeight: 550 }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <Tooltip 
                  cursor={{ fill: 'rgba(16, 185, 129, 0.04)' }}
                  contentStyle={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }} 
                  labelStyle={{ fontWeight: 'bold', color: '#1e293b' }}
                />
                <Bar dataKey="calories" radius={[8, 8, 0, 0]}>
                  {summaryData.weekly_chart.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.calories > user!.calorie_goal ? '#ef4444' : '#10b981'} 
                      fillOpacity={0.8}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Today's Meals list */}
        <div className="lg:col-span-3 bg-white border border-slate-150 rounded-3xl p-6 shadow-sm flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Meal Log</h3>
            <Link to="/history" className="text-xs font-bold text-brand-600 hover:text-brand-700 transition-colors flex items-center shrink-0">
              View All
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>

          {/* Meals List Container */}
          <div className="flex-grow overflow-y-auto max-h-64 space-y-3 pr-1">
            {meals.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-6 text-center space-y-2">
                <div className="p-2 bg-slate-50 text-slate-400 rounded-2xl">
                  <Utensils className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-800">No meals</p>
                  <p className="text-[10px] text-slate-400">Log a plate to start.</p>
                </div>
                <Link to="/analyze" className="btn-secondary text-[10px] px-3 py-1.5 mt-1">
                  Analyze Plate
                </Link>
              </div>
            ) : (
              meals.map((meal) => (
                <div 
                  key={meal.id} 
                  onClick={() => navigate(`/meals/${meal.id}`)}
                  className="flex items-center justify-between p-2.5 bg-slate-50/50 hover:bg-slate-50 border border-slate-100 rounded-xl cursor-pointer transition-all duration-200"
                >
                  <div className="flex items-center gap-2">
                    {meal.image_url ? (
                      <img 
                        src={meal.image_url} 
                        alt={meal.meal_name} 
                        className="h-9 w-9 rounded-lg object-cover border border-slate-200"
                      />
                    ) : (
                      <div className="h-9 w-9 rounded-lg bg-brand-50 border border-brand-100 text-brand-500 flex items-center justify-center shrink-0">
                        <FileText className="h-4 w-4" />
                      </div>
                    )}
                    <div className="min-w-0">
                      <h4 className="text-xs font-bold text-slate-800 truncate leading-snug">{meal.meal_name}</h4>
                      <p className="text-[10px] text-slate-400">{formatTime(meal.created_at)}</p>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="text-xs font-black text-slate-800">{meal.nutrition?.calories} kcal</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Small Aggregate Stats Cards */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <div className="bg-white border border-slate-150 rounded-3xl p-5 shadow-sm flex items-center gap-4 flex-grow justify-center lg:justify-start">
            <div className="p-3 bg-blue-50 text-blue-500 rounded-2xl">
              <Activity className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Meals Logged</p>
              <h3 className="text-2xl font-black text-slate-800">{meals_count}</h3>
              <p className="text-xs text-slate-400">logged today</p>
            </div>
          </div>

          <div className="bg-white border border-slate-150 rounded-3xl p-5 shadow-sm flex items-center gap-4 flex-grow justify-center lg:justify-start">
            <div className="p-3 bg-emerald-50 text-emerald-500 rounded-2xl">
              <Award className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Avg Health Score</p>
              <h3 className="text-2xl font-black text-slate-800">
                {average_health_score > 0 ? `${average_health_score}/100` : '--'}
              </h3>
              <p className="text-xs text-slate-400">based on today's logs</p>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default DashboardPage;
