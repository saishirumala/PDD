import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { Meal } from '../types';
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
  ArrowLeft, 
  Trash2, 
  AlertCircle,
  Clock,
  Sparkles,
  Info,
  Calendar,
  Layers,
  Heart,
  Droplet
} from 'lucide-react';

const MealReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [meal, setMeal] = useState<Meal | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchMealDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.get<Meal>(`/api/meals/${id}`);
        setMeal(response.data);
      } catch (err: any) {
        console.error("Meal details fetch failed:", err);
        setError(err.response?.data?.detail || "Could not retrieve meal report details.");
      } finally {
        setLoading(false);
      }
    };
    if (id) {
      fetchMealDetails();
    }
  }, [id]);

  const handleDelete = async () => {
    if (!meal) return;
    setDeleting(true);
    try {
      await api.delete(`/api/meals/${meal.id}`);
      navigate('/dashboard');
    } catch (err) {
      console.error("Failed to delete meal:", err);
      alert("Failed to delete this meal record. Please try again.");
    } finally {
      setDeleting(false);
      setDeleteConfirmOpen(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-brand-500"></div>
        <p className="text-slate-500 font-medium">Retrieving meal log data...</p>
      </div>
    );
  }

  if (error || !meal) {
    return (
      <div className="p-6 max-w-lg mx-auto text-center space-y-4">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
        <h3 className="text-xl font-bold text-slate-900">Report unavailable</h3>
        <p className="text-slate-500 text-sm">{error || "The selected meal record could not be found."}</p>
        <Link to="/dashboard" className="btn-primary mx-auto inline-flex">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  // Formatting date/time
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    } catch {
      return "Date unknown";
    }
  };

  const formatTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return "";
    }
  };

  // Setup macronutrients chart data
  // Convert grams to calories to show proportions (optional) or just represent grams directly.
  // Representing grams is very standard.
  const macroChartData = [
    { name: 'Protein', grams: meal.nutrition.protein, color: '#ef4444' },
    { name: 'Carbs', grams: meal.nutrition.carbohydrates, color: '#f59e0b' },
    { name: 'Fat', grams: meal.nutrition.fat, color: '#3b82f6' },
    { name: 'Fiber', grams: meal.nutrition.fiber, color: '#10b981' }
  ];

  // Helper for health score color
  const getScoreColor = (score: number) => {
    if (score >= 80) return { text: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', fill: '#10b981' };
    if (score >= 50) return { text: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', fill: '#f59e0b' };
    return { text: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', fill: '#ef4444' };
  };
  const scoreTheme = getScoreColor(meal.insight.health_score);

  return (
    <div className="space-y-8 animate-fadeIn max-w-6xl mx-auto">
      
      {/* Header breadcrumb & Delete */}
      <div className="flex justify-between items-center pb-2">
        <Link to="/dashboard" className="text-slate-500 hover:text-slate-900 transition-colors flex items-center gap-1 text-sm font-semibold">
          <ArrowLeft className="h-4.5 w-4.5" />
          Back to Logs
        </Link>
        <button
          onClick={() => setDeleteConfirmOpen(true)}
          className="btn-secondary text-red-500 border-red-100 hover:bg-red-50 hover:text-red-600 py-2 px-3 text-xs"
        >
          <Trash2 className="h-4 w-4" />
          Delete Record
        </button>
      </div>

      {/* Hero card details */}
      <div className="bg-white border border-slate-150 rounded-3xl p-6 sm:p-8 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
          
          {/* Left: Meal Photo */}
          <div className="md:col-span-4 space-y-4">
            {meal.image_url ? (
              <div className="rounded-2xl overflow-hidden border border-slate-200 aspect-square">
                <img 
                  src={meal.image_url} 
                  alt={meal.meal_name} 
                  className="w-full h-full object-cover"
                />
              </div>
            ) : (
              <div className="rounded-2xl bg-brand-50 border border-brand-100 aspect-square flex flex-col items-center justify-center text-brand-500">
                <Layers className="h-16 w-16" />
                <span className="text-xs text-brand-400 font-semibold mt-2">No photo logged</span>
              </div>
            )}
            <div className="space-y-1.5 text-center md:text-left">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5 justify-center md:justify-start">
                <Calendar className="h-3.5 w-3.5" />
                {formatDate(meal.created_at)}
              </span>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5 justify-center md:justify-start">
                <Clock className="h-3.5 w-3.5" />
                Logged at {formatTime(meal.created_at)}
              </span>
            </div>
          </div>

          {/* Right: Score & basic info */}
          <div className="md:col-span-8 space-y-6">
            <div>
              <h1 className="text-3xl font-black text-slate-900 leading-tight">{meal.meal_name}</h1>
              {meal.description && (
                <p className="text-slate-500 mt-2 text-sm italic">
                  "{meal.description}"
                </p>
              )}
            </div>

            {/* Health score and summary */}
            <div className={`p-6 border ${scoreTheme.border} ${scoreTheme.bg} rounded-2xl flex flex-col sm:flex-row items-center gap-6`}>
              
              {/* Circular Gauge */}
              <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="48" cy="48" r="40" className="stroke-slate-200/50 fill-transparent" strokeWidth="8" />
                  <circle 
                    cx="48" 
                    cy="48" 
                    r="40" 
                    className="transition-all duration-1000" 
                    stroke={scoreTheme.fill}
                    fill="transparent" 
                    strokeWidth="8" 
                    strokeDasharray={251.2}
                    strokeDashoffset={251.2 - (251.2 * meal.insight.health_score) / 100}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute text-center">
                  <span className={`text-2xl font-black ${scoreTheme.text}`}>{meal.insight.health_score}</span>
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Score</p>
                </div>
              </div>

              {/* Summary text */}
              <div className="space-y-1.5 text-center sm:text-left">
                <h4 className={`font-bold text-base ${scoreTheme.text}`}>AI Nutrition Summary</h4>
                <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                  {meal.insight.summary}
                </p>
              </div>

            </div>

            {/* Overall caloric summary */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-center">
                <p className="text-xs text-slate-400 font-medium">Total Calories</p>
                <p className="text-xl font-black text-slate-800 mt-1">{meal.nutrition.calories} kcal</p>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-center">
                <p className="text-xs text-slate-400 font-medium">Sugar Content</p>
                <p className="text-xl font-black text-slate-800 mt-1">{meal.nutrition.sugar} g</p>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-center">
                <p className="text-xs text-slate-400 font-medium">Sodium Level</p>
                <p className="text-xl font-black text-slate-800 mt-1">{meal.nutrition.sodium} mg</p>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-center">
                <p className="text-xs text-slate-400 font-medium">Nutrient Count</p>
                <p className="text-xl font-black text-slate-800 mt-1">{meal.foods.length} items</p>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Macros, identified items & Micronutrients */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Identified items & macro chart */}
        <div className="lg:col-span-7 space-y-8">
          
          {/* Foods list table */}
          <div className="bg-white border border-slate-150 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Identified Foods & Portions</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-100 text-slate-400 text-xs font-bold uppercase tracking-wider pb-2">
                    <th className="py-2.5">Food Item</th>
                    <th className="py-2.5">Est. Portion</th>
                    <th className="py-2.5 text-right">Calories</th>
                    <th className="py-2.5 text-right">Protein</th>
                    <th className="py-2.5 text-right">Carbs</th>
                    <th className="py-2.5 text-right">Fat</th>
                  </tr>
                </thead>
                <tbody className="text-sm divide-y divide-slate-50 text-slate-700">
                  {meal.foods.map((food) => (
                    <tr key={food.id} className="hover:bg-slate-50/50">
                      <td className="py-3 font-semibold text-slate-800">{food.name}</td>
                      <td className="py-3 text-slate-500 font-medium">{food.estimated_quantity}</td>
                      <td className="py-3 text-right font-semibold text-slate-800">{food.calories} kcal</td>
                      <td className="py-3 text-right text-red-600 font-medium">{food.protein}g</td>
                      <td className="py-3 text-right text-amber-600 font-medium">{food.carbohydrates}g</td>
                      <td className="py-3 text-right text-blue-600 font-medium">{food.fat}g</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Macro bar chart */}
          <div className="bg-white border border-slate-150 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Macronutrients Breakdown (g)</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={macroChartData} layout="vertical" margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                  <XAxis type="number" tickLine={false} axisLine={false} />
                  <YAxis dataKey="name" type="category" tickLine={false} axisLine={false} tick={{ fontSize: 12, fontWeight: 'bold' }} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0' }}
                    formatter={(value) => [`${value} g`, 'Grams']}
                  />
                  <Bar dataKey="grams" radius={[0, 6, 6, 0]} barSize={20}>
                    {macroChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>

        {/* Micronutrients & AI Insights */}
        <div className="lg:col-span-5 space-y-8">
          
          {/* AI Insights and recommendations */}
          <div className="bg-white border border-slate-150 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 text-brand-700">
              <Sparkles className="h-4 w-4 text-brand-500" />
              Nutritional Insights
            </h3>
            <ul className="space-y-3">
              {meal.insight.recommendations.map((rec, index) => (
                <li key={index} className="text-sm text-slate-700 leading-relaxed flex gap-2.5">
                  <div className="p-1 bg-brand-50 text-brand-500 rounded-full h-5 w-5 flex items-center justify-center shrink-0 text-xs font-black mt-0.5">
                    ✓
                  </div>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Micronutrient table grid */}
          <div className="bg-white border border-slate-150 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Droplet className="h-4.5 w-4.5 text-blue-500" />
              Micronutrients & Vitamins
            </h3>
            <div className="grid grid-cols-2 gap-3.5">
              
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-500">Iron</span>
                <span className="font-bold text-slate-800">{meal.micronutrients.iron} mg</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-500">Calcium</span>
                <span className="font-bold text-slate-800">{meal.micronutrients.calcium} mg</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-500">Magnesium</span>
                <span className="font-bold text-slate-800">{meal.micronutrients.magnesium} mg</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-500">Potassium</span>
                <span className="font-bold text-slate-800">{meal.micronutrients.potassium} mg</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-500">Vitamin A</span>
                <span className="font-bold text-slate-800">{meal.micronutrients.vitamin_a} mcg</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-500">Vitamin C</span>
                <span className="font-bold text-slate-800">{meal.micronutrients.vitamin_c} mg</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-500">Vitamin D</span>
                <span className="font-bold text-slate-800">{meal.micronutrients.vitamin_d} mcg</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-500">Vitamin B12</span>
                <span className="font-bold text-slate-800">{meal.micronutrients.vitamin_b12} mcg</span>
              </div>

            </div>
          </div>

        </div>

      </div>

      {/* Delete Confirmation Modal Drawer */}
      {deleteConfirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white border border-slate-150 rounded-3xl p-6 sm:p-8 max-w-md w-full space-y-6 animate-scaleIn">
            <div className="flex gap-4">
              <div className="p-3 bg-red-50 text-red-500 rounded-2xl shrink-0 h-12 w-12 flex items-center justify-center">
                <Trash2 className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <h4 className="font-extrabold text-slate-800 text-lg">Delete Meal Log?</h4>
                <p className="text-slate-500 text-sm leading-relaxed">
                  Are you sure you want to delete the record for <strong>{meal.meal_name}</strong>? This action will permanently remove it from your history and cannot be undone.
                </p>
              </div>
            </div>
            
            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setDeleteConfirmOpen(false)}
                disabled={deleting}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="btn-danger flex items-center justify-center min-w-[100px]"
              >
                {deleting ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                ) : (
                  'Delete Permanent'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default MealReportPage;
