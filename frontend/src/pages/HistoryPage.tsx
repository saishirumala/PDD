import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Meal } from '../types';
import { 
  Search, 
  Trash2, 
  ChevronRight, 
  Utensils, 
  Calendar, 
  Activity, 
  FileText,
  AlertCircle,
  PlusCircle
} from 'lucide-react';

const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [meals, setMeals] = useState<Meal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<Meal | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Fetch meals on mount & when search changes (or filter locally)
  // Filtering locally is faster, but we can call API with ?search= query to test server-side filter!
  // Let's implement active search using a debounce or calling it on change.
  // Querying on query changes with local fallback is highly robust.
  useEffect(() => {
    const fetchMeals = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.get<Meal[]>(`/api/meals?search=${encodeURIComponent(searchQuery)}`);
        setMeals(response.data);
      } catch (err: any) {
        console.error("Meals log history fetch failed:", err);
        setError("Failed to fetch historical log data.");
      } finally {
        setLoading(false);
      }
    };

    const handler = setTimeout(() => {
      fetchMeals();
    }, 300); // 300ms debounce

    return () => clearTimeout(handler);
  }, [searchQuery]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await api.delete(`/api/meals/${deleteTarget.id}`);
      // Remove locally from state
      setMeals((prev) => prev.filter((m) => m.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err) {
      console.error("Failed to delete meal:", err);
      alert("Failed to delete meal log. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return "";
    }
  };

  if (loading && meals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-brand-500"></div>
        <p className="text-slate-500 font-medium">Loading history logs...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Meal History Log</h1>
          <p className="text-slate-500 text-sm">
            Review and manage all your previously analyzed and saved meals.
          </p>
        </div>
        <button onClick={() => navigate('/analyze')} className="btn-primary self-start">
          <PlusCircle className="h-5 w-5" />
          New Analysis
        </button>
      </div>

      {/* Search Input Bar */}
      <div className="relative max-w-md bg-white border border-slate-200/50 rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-brand-500/20 focus-within:border-brand-500 transition-all">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
          <Search className="h-5 w-5" />
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by meal name, ingredients..."
          className="w-full pl-11 pr-4 py-3 rounded-2xl border-none bg-transparent outline-none text-sm text-slate-800"
        />
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-900 rounded-xl text-sm flex items-start gap-2">
          <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {/* History Grid List */}
      {meals.length === 0 ? (
        <div className="bg-white border border-slate-150 rounded-3xl p-12 text-center space-y-4 max-w-lg mx-auto shadow-sm">
          <div className="p-4 bg-slate-50 text-slate-400 rounded-2xl inline-block">
            <Utensils className="h-10 w-10" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-800">No meal records found</h3>
            <p className="text-xs text-slate-400 mt-1">
              {searchQuery ? "No matches found. Try modifying your search query." : "You haven't logged any meals yet. Get started by analyzing your plate!"}
            </p>
          </div>
          {!searchQuery && (
            <button onClick={() => navigate('/analyze')} className="btn-primary mx-auto">
              Analyze Meal Plate
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {meals.map((meal) => (
            <div 
              key={meal.id} 
              className="bg-white border border-slate-150 rounded-3xl shadow-sm overflow-hidden flex flex-col justify-between hover:shadow-md transition-shadow group relative"
            >
              
              {/* Card Image banner */}
              <div className="aspect-video relative overflow-hidden bg-brand-50 border-b border-slate-100 shrink-0">
                {meal.image_url ? (
                  <img 
                    src={meal.image_url} 
                    alt={meal.meal_name} 
                    className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300 cursor-pointer"
                    onClick={() => navigate(`/meals/${meal.id}`)}
                  />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-brand-500">
                    <FileText className="h-10 w-10" />
                  </div>
                )}
                
                {/* Health score badge on image */}
                {meal.insight && (
                  <div className="absolute bottom-3 right-3 px-2.5 py-1 bg-white/90 backdrop-blur-sm rounded-full text-xs font-black shadow-sm flex items-center gap-1.5 border border-white/50">
                    <span className={`w-2 h-2 rounded-full ${
                      meal.insight.health_score >= 80 ? 'bg-emerald-500' : meal.insight.health_score >= 50 ? 'bg-amber-400' : 'bg-red-500'
                    }`} />
                    Score {meal.insight.health_score}
                  </div>
                )}
              </div>

              {/* Card details */}
              <div className="p-5 flex-grow space-y-4 flex flex-col justify-between">
                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(meal.created_at)}
                  </span>
                  <h3 
                    onClick={() => navigate(`/meals/${meal.id}`)}
                    className="text-base font-extrabold text-slate-800 line-clamp-1 group-hover:text-brand-600 transition-colors cursor-pointer"
                  >
                    {meal.meal_name}
                  </h3>
                  {meal.description && (
                    <p className="text-xs text-slate-400 line-clamp-1">
                      {meal.description}
                    </p>
                  )}
                </div>

                {/* Macros summary row */}
                <div className="grid grid-cols-4 gap-1.5 py-2.5 border-y border-slate-50 text-center text-[10px] shrink-0">
                  <div>
                    <span className="text-slate-400 font-medium">Calories</span>
                    <p className="font-bold text-slate-700 text-xs mt-0.5">{meal.nutrition.calories} kcal</p>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium text-red-500">Protein</span>
                    <p className="font-bold text-slate-700 text-xs mt-0.5">{meal.nutrition.protein}g</p>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium text-amber-500">Carbs</span>
                    <p className="font-bold text-slate-700 text-xs mt-0.5">{meal.nutrition.carbohydrates}g</p>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium text-blue-500">Fat</span>
                    <p className="font-bold text-slate-700 text-xs mt-0.5">{meal.nutrition.fat}g</p>
                  </div>
                </div>

                {/* Bottom triggers */}
                <div className="flex justify-between items-center pt-1.5 text-xs font-semibold">
                  <button 
                    onClick={() => navigate(`/meals/${meal.id}`)}
                    className="text-brand-600 hover:text-brand-700 flex items-center gap-0.5 transition-colors"
                  >
                    View Report
                    <ChevronRight className="h-4.5 w-4.5" />
                  </button>
                  <button 
                    onClick={() => setDeleteTarget(meal)}
                    className="text-slate-300 hover:text-red-500 transition-colors p-1.5 hover:bg-slate-50 rounded-lg"
                    title="Delete meal log"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>

              </div>

            </div>
          ))}
        </div>
      )}

      {/* Delete confirmation modal */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white border border-slate-150 rounded-3xl p-6 sm:p-8 max-w-md w-full space-y-6 animate-scaleIn">
            <div className="flex gap-4">
              <div className="p-3 bg-red-50 text-red-500 rounded-2xl shrink-0 h-12 w-12 flex items-center justify-center">
                <Trash2 className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <h4 className="font-extrabold text-slate-800 text-lg">Delete Meal Log?</h4>
                <p className="text-slate-500 text-sm leading-relaxed">
                  Are you sure you want to delete the record for <strong>{deleteTarget.meal_name}</strong>? This action cannot be undone.
                </p>
              </div>
            </div>
            
            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setDeleteTarget(null)}
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

export default HistoryPage;
