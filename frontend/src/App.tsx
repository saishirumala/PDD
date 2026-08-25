import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';

// Import Pages
import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import AnalyzePage from './pages/AnalyzePage';
import HistoryPage from './pages/HistoryPage';
import MealReportPage from './pages/MealReportPage';
import ProfilePage from './pages/ProfilePage';

// Simple fallback legal pages
const PrivacyPage: React.FC = () => (
  <MainLayout>
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
      <h1 className="text-3xl font-extrabold text-slate-900 mb-6">Privacy Policy</h1>
      <p className="text-slate-600 mb-4">Effective Date: August 24, 2026</p>
      <p className="text-slate-600 mb-4">
        Welcome to NutriGuide. We value your privacy. This privacy policy describes how we collect, use, process, and protect your information when you use our AI-powered meal analysis service.
      </p>
      <h2 className="text-xl font-bold text-slate-800 mt-6 mb-3">1. Information We Collect</h2>
      <p className="text-slate-600 mb-4">
        When you upload food photos or type meal descriptions, we transmit them to our secure backend and relevant AI providers for analysis. We store the resulting data in our databases so you can access your historical logs.
      </p>
      <h2 className="text-xl font-bold text-slate-800 mt-6 mb-3">2. How We Use Information</h2>
      <p className="text-slate-600 mb-4">
        We use your data solely to calculate nutrient estimates, generate insights, maintain logs, and support your nutrition tracking targets. We never sell your personal details to third parties.
      </p>
      <h2 className="text-xl font-bold text-slate-800 mt-6 mb-3">3. Security</h2>
      <p className="text-slate-600 mb-4">
        Passwords are securely hashed. All communications between the app client and API server use SSL encryption.
      </p>
    </div>
  </MainLayout>
);

const TermsPage: React.FC = () => (
  <MainLayout>
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
      <h1 className="text-3xl font-extrabold text-slate-900 mb-6">Terms of Service</h1>
      <p className="text-slate-600 mb-4">Last Updated: August 24, 2026</p>
      <p className="text-slate-600 mb-4">
        By signing up for and using NutriGuide, you agree to these Terms of Service.
      </p>
      <h2 className="text-xl font-bold text-slate-800 mt-6 mb-3">1. AI Estimations Disclaimer</h2>
      <div className="p-4 bg-amber-50 border border-amber-200 text-amber-900 rounded-xl mb-4 text-sm font-medium">
        IMPORTANT: NutriGuide values are AI-generated nutritional estimates. They are provided for educational and tracking support purposes only. They are not medical facts, diagnoses, prescriptions, or advice. Always consult a certified healthcare professional before making major dietary adjustments.
      </div>
      <h2 className="text-xl font-bold text-slate-800 mt-6 mb-3">2. Service Usage</h2>
      <p className="text-slate-600 mb-4">
        You agree to upload only legitimate, relevant food photos and not to attempt any SQL injection, file upload exploits, or system attacks.
      </p>
    </div>
  </MainLayout>
);

// Protected Route Guard
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-brand-500"></div>
          <p className="text-slate-500 font-medium text-sm">Authenticating session...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth" replace />;
  }

  return <>{children}</>;
};

// Redirect logged-in users away from auth pages (e.g. login)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (user) return <Navigate to="/dashboard" replace />;

  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <Routes>
      {/* Public Pages */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/terms" element={<TermsPage />} />
      
      {/* Auth Gate Pages */}
      <Route 
        path="/auth" 
        element={
          <PublicRoute>
            <AuthPage />
          </PublicRoute>
        } 
      />

      {/* Protected Dash Pages */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <DashboardPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/analyze" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <AnalyzePage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/history" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <HistoryPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/meals/:id" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <MealReportPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/profile" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <ProfilePage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />

      {/* 404 Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
