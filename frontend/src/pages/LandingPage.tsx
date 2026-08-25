import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import { 
  Camera, 
  Sparkles, 
  Heart, 
  Scale, 
  CheckCircle,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  ChefHat
} from 'lucide-react';

const LandingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'image' | 'text'>('image');

  return (
    <MainLayout>
      <div className="relative overflow-hidden pt-8 pb-16">
        
        {/* Decorative background blobs */}
        <div className="absolute top-10 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-brand-100/30 rounded-full blur-3xl pointer-events-none -z-10" />
        <div className="absolute top-40 right-10 w-[300px] h-[300px] bg-accent-100/20 rounded-full blur-3xl pointer-events-none -z-10" />

        {/* Hero Section */}
        <div className="text-center max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-brand-50 border border-brand-100 text-brand-700 rounded-full text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="h-3.5 w-3.5" />
            Empowered by Advanced Gemini AI
          </div>
          
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 leading-tight">
            AI-Powered Nutrition Analysis <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-brand-500 to-emerald-600 bg-clip-text text-transparent">
              In a Single Glance
            </span>
          </h1>

          <p className="text-base sm:text-lg md:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Snap a food photo or type a meal description. Get instant, conservative calorie estimates, macros, micronutrient breakdowns, and personalized health scores.
          </p>

          <div className="flex flex-col sm:flex-row justify-center items-center gap-4 pt-4">
            <Link to="/auth?signup=true" className="btn-primary w-full sm:w-auto px-8 py-3.5 text-base shadow-lg shadow-brand-500/10">
              Analyze Your Meal Now
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link to="/auth" className="btn-secondary w-full sm:w-auto px-8 py-3.5 text-base">
              Sign In to Your Log
            </Link>
          </div>
        </div>

        {/* Interactive Mockup Preview */}
        <div className="mt-16 max-w-5xl mx-auto glass-card rounded-3xl p-6 sm:p-8 border border-slate-200/60 shadow-xl relative">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Input Mockup */}
            <div className="lg:col-span-5 space-y-6">
              <div className="flex border-b border-slate-100 pb-2">
                <button 
                  onClick={() => setActiveTab('image')}
                  className={`flex-1 pb-3 text-sm font-semibold transition-colors flex items-center justify-center gap-2 border-b-2 ${
                    activeTab === 'image' ? 'border-brand-500 text-brand-600' : 'border-transparent text-slate-400 hover:text-slate-600'
                  }`}
                >
                  <Camera className="h-4 w-4" />
                  Food Photograph
                </button>
                <button 
                  onClick={() => setActiveTab('text')}
                  className={`flex-1 pb-3 text-sm font-semibold transition-colors flex items-center justify-center gap-2 border-b-2 ${
                    activeTab === 'text' ? 'border-brand-500 text-brand-600' : 'border-transparent text-slate-400 hover:text-slate-600'
                  }`}
                >
                  <ChefHat className="h-4 w-4" />
                  Text Description
                </button>
              </div>

              {activeTab === 'image' ? (
                <div className="border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer group">
                  <div className="p-3 bg-white rounded-xl shadow-sm inline-block mb-3 group-hover:scale-105 transition-transform">
                    <Camera className="h-6 w-6 text-brand-500" />
                  </div>
                  <p className="text-sm font-semibold text-slate-700">Salmon_Quinoa_Bowl.jpg</p>
                  <p className="text-xs text-slate-400 mt-1">Image selected (1.2 MB)</p>
                </div>
              ) : (
                <div className="border border-slate-200 rounded-2xl p-4 bg-slate-50/50">
                  <p className="text-sm font-medium text-slate-800 italic">
                    "Pan-seared salmon fillet over 1 cup cooked quinoa with 6 spears of steamed asparagus."
                  </p>
                </div>
              )}

              <button className="btn-primary w-full justify-center opacity-90 cursor-default">
                <BrainCircuit className="h-5 w-5" />
                Analyze Plate (Demo)
              </button>
            </div>

            {/* Output Mockup */}
            <div className="lg:col-span-7 bg-slate-50/80 border border-slate-200/50 rounded-2xl p-6 space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">Seared Salmon Quinoa Bowl</h3>
                  <p className="text-xs text-slate-400">AI Nutrition Estimate</p>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">
                  <CheckCircle className="h-3.5 w-3.5" />
                  Score: 95/100
                </div>
              </div>

              {/* Macros pills */}
              <div className="grid grid-cols-4 gap-2">
                <div className="bg-white p-3 rounded-xl border border-slate-100 text-center">
                  <p className="text-xs text-slate-400">Calories</p>
                  <p className="text-sm font-bold text-slate-800">557 kcal</p>
                </div>
                <div className="bg-white p-3 rounded-xl border border-slate-100 text-center">
                  <p className="text-xs text-slate-400">Protein</p>
                  <p className="text-sm font-bold text-slate-800">44.3g</p>
                </div>
                <div className="bg-white p-3 rounded-xl border border-slate-100 text-center">
                  <p className="text-xs text-slate-400">Carbs</p>
                  <p className="text-sm font-bold text-slate-800">43.8g</p>
                </div>
                <div className="bg-white p-3 rounded-xl border border-slate-100 text-center">
                  <p className="text-xs text-slate-400">Fat</p>
                  <p className="text-sm font-bold text-slate-800">21.8g</p>
                </div>
              </div>

              {/* Identified foods */}
              <div className="space-y-2">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Identified Items</p>
                <div className="space-y-1.5 text-xs text-slate-600">
                  <div className="flex justify-between">
                    <span>🐟 Salmon Fillet (Pan-seared)</span>
                    <span className="font-semibold text-slate-800">150g (310 kcal)</span>
                  </div>
                  <div className="flex justify-between">
                    <span>🌾 Cooked Quinoa</span>
                    <span className="font-semibold text-slate-800">1 cup (222 kcal)</span>
                  </div>
                  <div className="flex justify-between">
                    <span>🥦 Steamed Asparagus</span>
                    <span className="font-semibold text-slate-800">6 spears (25 kcal)</span>
                  </div>
                </div>
              </div>

              {/* Insights */}
              <div className="bg-brand-50/50 border border-brand-100 rounded-xl p-3.5 text-xs text-brand-900 leading-relaxed">
                <span className="font-bold text-brand-800">AI Insight:</span> Rich in Omega-3 fatty acids, promoting cardiac health. Quinoa provides a complete plant protein and complex fiber, stabilizing blood sugars.
              </div>
            </div>
            
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="mt-24 max-w-7xl mx-auto space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-extrabold text-slate-900">
              Complete Nutritional Visibility
            </h2>
            <p className="text-slate-600 max-w-xl mx-auto text-sm sm:text-base">
              A comprehensive set of tools built on state-of-the-art vision models to evaluate what you consume daily.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Feature 1 */}
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-4 hover:-translate-y-1 transition-transform duration-200">
              <div className="p-3 bg-brand-50 rounded-xl inline-block text-brand-500">
                <BrainCircuit className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Visual Image Parser</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Upload photos of your breakfast, lunches, or snacks. The system uses a vision model to detect items, assess portion sizes, and calculate estimates.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-4 hover:-translate-y-1 transition-transform duration-200">
              <div className="p-3 bg-blue-50 rounded-xl inline-block text-blue-500">
                <Scale className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Full Nutrient Profiling</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Goes beyond calories. Evaluates proteins, carbohydrates, healthy fats, fiber, sugars, sodium, and key minerals like iron, calcium, and potassium.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-4 hover:-translate-y-1 transition-transform duration-200">
              <div className="p-3 bg-accent-50 rounded-xl inline-block text-accent-500">
                <Heart className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Smart Calibration Score</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Aggregates nutritional statistics into a transparent index (0-100) and prints educational feedback for adjusting intake.
              </p>
            </div>

          </div>
        </div>

        {/* Step-by-Step Workflow */}
        <div className="mt-28 bg-white border border-slate-150 rounded-3xl p-8 sm:p-12 max-w-5xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 text-center mb-12">
            How It Works in 3 Steps
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            
            <div className="space-y-3 text-center relative z-10">
              <div className="w-12 h-12 bg-brand-50 border-2 border-brand-500 text-brand-700 font-extrabold text-lg flex items-center justify-center rounded-full mx-auto shadow-sm">
                1
              </div>
              <h4 className="font-bold text-slate-800">Input Meal</h4>
              <p className="text-slate-600 text-xs sm:text-sm">
                Upload a clear food photo or describe your meal in plain English.
              </p>
            </div>

            <div className="space-y-3 text-center relative z-10">
              <div className="w-12 h-12 bg-brand-50 border-2 border-brand-500 text-brand-700 font-extrabold text-lg flex items-center justify-center rounded-full mx-auto shadow-sm">
                2
              </div>
              <h4 className="font-bold text-slate-800">AI Estimation</h4>
              <p className="text-slate-600 text-xs sm:text-sm">
                The Gemini model parses text and images to evaluate weights and nutrition metrics.
              </p>
            </div>

            <div className="space-y-3 text-center relative z-10">
              <div className="w-12 h-12 bg-brand-50 border-2 border-brand-500 text-brand-700 font-extrabold text-lg flex items-center justify-center rounded-full mx-auto shadow-sm">
                3
              </div>
              <h4 className="font-bold text-slate-800">View & Save</h4>
              <p className="text-slate-600 text-xs sm:text-sm">
                Unlock charts, macro totals, fiber calculations, and logs in your history tracker.
              </p>
            </div>

          </div>
        </div>

        {/* CTA Banner */}
        <div className="mt-24 text-center space-y-6 max-w-xl mx-auto">
          <h2 className="text-3xl font-extrabold text-slate-900">Ready to track smarter?</h2>
          <p className="text-slate-600 text-sm">
            Sign up today to analyze meals, set personal macronutrient targets, and monitor your daily calorie limits.
          </p>
          <Link to="/auth?signup=true" className="btn-primary inline-flex px-8 py-3.5">
            Create Your Account
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>

      </div>
    </MainLayout>
  );
};

export default LandingPage;
