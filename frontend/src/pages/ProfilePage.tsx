import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  User as UserIcon, 
  Target, 
  CheckCircle2, 
  AlertCircle,
  Calendar,
  Lock,
  Heart,
  Droplet
} from 'lucide-react';

const ProfilePage: React.FC = () => {
  const { user, updateGoals } = useAuth();
  
  const [name, setName] = useState(user?.name || '');
  const [calorieGoal, setCalorieGoal] = useState(user?.calorie_goal.toString() || '2000');
  const [proteinGoal, setProteinGoal] = useState(user?.protein_goal.toString() || '150');
  const [carbsGoal, setCarbsGoal] = useState(user?.carbs_goal.toString() || '225');
  const [fatGoal, setFatGoal] = useState(user?.fat_goal.toString() || '65');
  const [fiberGoal, setFiberGoal] = useState(user?.fiber_goal.toString() || '30');
  
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    // Validation
    const cVal = parseInt(calorieGoal);
    const pVal = parseFloat(proteinGoal);
    const cbVal = parseFloat(carbsGoal);
    const fVal = parseFloat(fatGoal);
    const fbVal = parseFloat(fiberGoal);

    if (!name.trim()) {
      setError("Name cannot be blank.");
      return;
    }
    if (isNaN(cVal) || cVal < 500 || cVal > 10000) {
      setError("Daily calorie target must be between 500 kcal and 10,000 kcal.");
      return;
    }
    if (isNaN(pVal) || pVal < 0 || isNaN(cbVal) || cbVal < 0 || isNaN(fVal) || fVal < 0 || isNaN(fbVal) || fbVal < 0) {
      setError("Macronutrient goals cannot be negative values.");
      return;
    }

    setSaving(true);
    try {
      await updateGoals({
        name: name.trim(),
        calorie_goal: cVal,
        protein_goal: pVal,
        carbs_goal: cbVal,
        fat_goal: fVal,
        fiber_goal: fbVal
      });
      setSuccess(true);
      // Auto fade success message
      setTimeout(() => setSuccess(false), 4000);
    } catch (err: any) {
      console.error("Failed to update profile goals:", err);
      setError(err.response?.data?.detail || "Failed to update profile targets. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString([], { dateStyle: 'long' });
    } catch {
      return "";
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      
      {/* Title */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">My Profile Settings</h1>
        <p className="text-slate-500 text-sm">
          Customize your daily calorie intake goals, target macronutrient targets, and details.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        
        {/* Left: General user info summary */}
        <div className="md:col-span-4 bg-white border border-slate-150 rounded-3xl p-6 shadow-sm space-y-6">
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="h-16 w-16 bg-brand-50 border border-brand-100 text-brand-500 rounded-full flex items-center justify-center">
              <UserIcon className="h-8 w-8" />
            </div>
            <div>
              <h3 className="text-lg font-extrabold text-slate-800">{user?.name}</h3>
              <p className="text-xs text-slate-400">{user?.email}</p>
            </div>
          </div>
          
          <div className="border-t border-slate-50 pt-4 space-y-3 text-xs text-slate-500 font-medium">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-slate-400" />
              <span>Joined on {formatDate(user?.created_at)}</span>
            </div>
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-slate-400" />
              <span>Session Authenticated</span>
            </div>
          </div>
        </div>

        {/* Right: Goals updates Form */}
        <div className="md:col-span-8 bg-white border border-slate-150 rounded-3xl p-6 sm:p-8 shadow-sm">
          
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Action status alerts */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 text-red-900 rounded-xl text-sm flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-red-500 shrink-0 animate-bounce" />
                <span className="font-semibold">{error}</span>
              </div>
            )}
            
            {success && (
              <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded-xl text-sm flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
                <span className="font-semibold">Nutrition targets updated successfully!</span>
              </div>
            )}

            {/* Profile section */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <UserIcon className="h-4.5 w-4.5 text-slate-400" />
                General Account Info
              </h3>
              
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="form-input"
                  required
                />
              </div>
            </div>

            <hr className="border-slate-100" />

            {/* Target targets section */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Target className="h-4.5 w-4.5 text-brand-500" />
                Daily Nutrition Targets
              </h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Calorie Intake (kcal)</label>
                  <input
                    type="number"
                    value={calorieGoal}
                    onChange={(e) => setCalorieGoal(e.target.value)}
                    className="form-input"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Protein Goal (g)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={proteinGoal}
                    onChange={(e) => setProteinGoal(e.target.value)}
                    className="form-input"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Carbs Goal (g)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={carbsGoal}
                    onChange={(e) => setCarbsGoal(e.target.value)}
                    className="form-input"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Fat Goal (g)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={fatGoal}
                    onChange={(e) => setFatGoal(e.target.value)}
                    className="form-input"
                    required
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Fiber Goal (g)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={fiberGoal}
                    onChange={(e) => setFiberGoal(e.target.value)}
                    className="form-input"
                    required
                  />
                </div>

              </div>
            </div>

            {/* BMR & TDEE Goal Calculator Helper */}
            <div className="p-5 bg-gradient-to-br from-brand-50/50 to-blue-50/50 border border-brand-100/60 rounded-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-brand-700 uppercase tracking-wider flex items-center gap-1.5">
                  <Heart className="h-4 w-4 text-brand-500" />
                  Calorie & Macro Calculator (BMR / TDEE)
                </h4>
              </div>
              <p className="text-xs text-slate-500">
                Not sure about your targets? Calculate your Total Daily Energy Expenditure (TDEE) based on your body metrics.
              </p>
              
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div>
                  <label className="font-semibold text-slate-600 block mb-1">Gender</label>
                  <select 
                    id="calc-gender"
                    defaultValue="male"
                    className="w-full p-2 bg-white border border-slate-200 rounded-xl outline-none"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
                <div>
                  <label className="font-semibold text-slate-600 block mb-1">Age (yrs)</label>
                  <input 
                    id="calc-age"
                    type="number" 
                    defaultValue="25" 
                    className="w-full p-2 bg-white border border-slate-200 rounded-xl outline-none"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-600 block mb-1">Weight (kg)</label>
                  <input 
                    id="calc-weight"
                    type="number" 
                    defaultValue="70" 
                    className="w-full p-2 bg-white border border-slate-200 rounded-xl outline-none"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-600 block mb-1">Height (cm)</label>
                  <input 
                    id="calc-height"
                    type="number" 
                    defaultValue="175" 
                    className="w-full p-2 bg-white border border-slate-200 rounded-xl outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="font-semibold text-slate-600 block mb-1">Activity Level</label>
                  <select 
                    id="calc-activity"
                    defaultValue="1.375"
                    className="w-full p-2 bg-white border border-slate-200 rounded-xl outline-none"
                  >
                    <option value="1.2">Sedentary (Little/no exercise)</option>
                    <option value="1.375">Light (1-3 days/week)</option>
                    <option value="1.55">Moderate (3-5 days/week)</option>
                    <option value="1.725">Very Active (6-7 days/week)</option>
                  </select>
                </div>
                <div>
                  <label className="font-semibold text-slate-600 block mb-1">Primary Goal</label>
                  <select 
                    id="calc-goal"
                    defaultValue="maintain"
                    className="w-full p-2 bg-white border border-slate-200 rounded-xl outline-none"
                  >
                    <option value="lose">Weight Loss (-500 kcal)</option>
                    <option value="maintain">Weight Maintenance</option>
                    <option value="gain">Muscle Gain (+300 kcal)</option>
                  </select>
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  const gender = (document.getElementById('calc-gender') as HTMLSelectElement).value;
                  const age = parseFloat((document.getElementById('calc-age') as HTMLInputElement).value) || 25;
                  const weight = parseFloat((document.getElementById('calc-weight') as HTMLInputElement).value) || 70;
                  const height = parseFloat((document.getElementById('calc-height') as HTMLInputElement).value) || 175;
                  const activity = parseFloat((document.getElementById('calc-activity') as HTMLSelectElement).value) || 1.375;
                  const goal = (document.getElementById('calc-goal') as HTMLSelectElement).value;

                  // Mifflin-St Jeor BMR Equation
                  let bmr = (10 * weight) + (6.25 * height) - (5 * age);
                  bmr += gender === 'male' ? 5 : -161;

                  let tdee = bmr * activity;
                  if (goal === 'lose') tdee -= 500;
                  if (goal === 'gain') tdee += 300;

                  const targetCalories = Math.round(tdee);
                  // Standard Macro Split (30% Protein, 40% Carbs, 30% Fat)
                  const targetProtein = Math.round((targetCalories * 0.30) / 4);
                  const targetCarbs = Math.round((targetCalories * 0.40) / 4);
                  const targetFat = Math.round((targetCalories * 0.30) / 9);

                  setCalorieGoal(targetCalories.toString());
                  setProteinGoal(targetProtein.toString());
                  setCarbsGoal(targetCarbs.toString());
                  setFatGoal(targetFat.toString());
                  setFiberGoal("30");
                }}
                className="w-full py-2 bg-white hover:bg-brand-50 text-brand-600 font-bold border border-brand-200 rounded-xl text-xs transition-colors shadow-sm"
              >
                ⚡ Calculate & Apply Recommended Goals
              </button>
            </div>

            <button
              type="submit"
              disabled={saving}
              className="btn-primary w-full py-3 justify-center shadow-lg shadow-brand-500/10 text-base"
            >
              {saving ? (
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
              ) : (
                'Save Profile Goals'
              )}
            </button>

          </form>

        </div>

      </div>

    </div>
  );
};

export default ProfilePage;
