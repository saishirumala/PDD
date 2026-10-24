import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Salad, Eye, EyeOff, AlertCircle, CheckCircle2, ArrowLeft } from 'lucide-react';

type AuthMode = 'signin' | 'signup' | 'reset';

const AuthPage: React.FC = () => {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const [mode, setMode] = useState<AuthMode>('signin');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [resetSubmitting, setResetSubmitting] = useState(false);

  // Sync mode with URL queries (e.g. ?signup=true)
  useEffect(() => {
    const signupParam = searchParams.get('signup');
    if (signupParam === 'true') {
      setMode('signup');
    } else {
      setMode('signin');
    }
    setError(null);
    setSuccessMsg(null);
  }, [searchParams]);

  const switchMode = (newMode: AuthMode) => {
    setMode(newMode);
    setError(null);
    setSuccessMsg(null);
    setPassword('');
    setConfirmPassword('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setError("Please enter your email address.");
      return;
    }

    // Password reset handling
    if (mode === 'reset') {
      if (!password) {
        setError("Please enter a new password.");
        return;
      }
      if (password.length < 6) {
        setError("Password must be at least 6 characters long.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }

      setResetSubmitting(true);
      try {
        const res = await api.post('/api/auth/reset-password', {
          email: cleanEmail,
          new_password: password
        });
        setSuccessMsg(res.data?.message || "Password updated successfully! You can now sign in.");
        setPassword('');
        setConfirmPassword('');
        setTimeout(() => {
          switchMode('signin');
        }, 2000);
      } catch (err: any) {
        const detail = err.response?.data?.detail;
        setError(typeof detail === 'string' ? detail : "Failed to reset password. Please check the email address.");
      } finally {
        setResetSubmitting(false);
      }
      return;
    }

    // Sign in / Sign up validation
    if (!password) {
      setError("Please enter your password.");
      return;
    }

    if (mode === 'signup') {
      if (!name.trim()) {
        setError("Please enter your full name.");
        return;
      }
      if (password.length < 6) {
        setError("Password must be at least 6 characters long.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    }

    setSubmitting(true);
    try {
      if (mode === 'signup') {
        await register(name, cleanEmail, password);
      } else {
        await login(cleanEmail, password);
      }
      navigate('/dashboard');
    } catch (err: any) {
      let serverMsg = "Incorrect password or authentication failed. Please verify your credentials.";
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        serverMsg = detail;
      } else if (Array.isArray(detail) && detail.length > 0) {
        serverMsg = detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
      } else if (err.message) {
        serverMsg = err.message;
      }
      setError(serverMsg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-slate-50/50 px-4 sm:px-6 relative">
      
      {/* Background shapes */}
      <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-brand-100/20 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-accent-100/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Main card */}
      <div className="w-full max-w-md bg-white border border-slate-200/50 shadow-xl rounded-3xl p-8 space-y-6">
        
        {/* Branding header */}
        <div className="text-center space-y-2">
          <Link to="/" className="inline-flex items-center gap-2 text-brand-600 justify-center">
            <div className="p-2 bg-brand-50 rounded-xl">
              <Salad className="h-6 w-6 text-brand-500" />
            </div>
            <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-brand-600 to-emerald-500 bg-clip-text text-transparent">
              NutriGuide
            </span>
          </Link>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            {mode === 'signup' 
              ? 'Create your account' 
              : mode === 'reset' 
              ? 'Reset your password' 
              : 'Sign in to your account'}
          </h2>
          <p className="text-sm text-slate-500">
            {mode === 'signup' 
              ? 'Track foods, macros, and micro minerals' 
              : mode === 'reset' 
              ? 'Enter your email and create a new password' 
              : 'Welcome back! Log in to view your dashboard'}
          </p>
        </div>

        {/* Success Alert Box */}
        {successMsg && (
          <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded-xl text-sm flex items-start gap-2 animate-fadeIn">
            <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
            <div className="flex-1 space-y-1">
              <span className="font-medium block">{successMsg}</span>
              {mode === 'reset' && (
                <button
                  type="button"
                  onClick={() => switchMode('signin')}
                  className="text-xs font-bold text-emerald-700 underline mt-1 block"
                >
                  Proceed to Sign In now →
                </button>
              )}
            </div>
          </div>
        )}

        {/* Error Alert Box */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-900 rounded-xl text-sm flex items-start gap-2 animate-fadeIn">
            <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
            <div className="flex-1 space-y-2">
              <span className="font-medium block">{error}</span>
              {mode === 'signup' && error.includes("already exists") && (
                <button
                  type="button"
                  onClick={() => switchMode('signin')}
                  className="inline-flex items-center gap-1 text-xs font-bold text-brand-700 bg-white px-3 py-1.5 rounded-lg border border-red-200 shadow-sm hover:bg-red-50 transition-colors"
                >
                  👉 Switch to Sign In with this email
                </button>
              )}
              {mode === 'signin' && (error.toLowerCase().includes("password") || error.toLowerCase().includes("wrong")) && (
                <button
                  type="button"
                  onClick={() => switchMode('reset')}
                  className="inline-flex items-center gap-1 text-xs font-bold text-brand-700 bg-white px-3 py-1.5 rounded-lg border border-red-200 shadow-sm hover:bg-red-50 transition-colors"
                >
                  🔑 Reset forgotten password
                </button>
              )}
              {mode === 'signin' && (error.toLowerCase().includes("not found") || error.toLowerCase().includes("register")) && (
                <button
                  type="button"
                  onClick={() => switchMode('signup')}
                  className="inline-flex items-center gap-1 text-xs font-bold text-brand-700 bg-white px-3 py-1.5 rounded-lg border border-red-200 shadow-sm hover:bg-red-50 transition-colors"
                >
                  👉 Create new account with this email
                </button>
              )}
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          
          {mode === 'signup' && (
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                className="form-input"
                required
              />
            </div>
          )}

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@domain.com"
              className="form-input"
              required
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                {mode === 'reset' ? 'New Password' : 'Password'}
              </label>
              {mode === 'signin' && (
                <button
                  type="button"
                  onClick={() => switchMode('reset')}
                  className="text-xs font-semibold text-brand-600 hover:text-brand-700 hover:underline transition-colors"
                >
                  Forgot password?
                </button>
              )}
            </div>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="form-input pr-10"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {(mode === 'signup' || mode === 'reset') && (
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                {mode === 'reset' ? 'Confirm New Password' : 'Confirm Password'}
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="form-input pr-10"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || resetSubmitting}
            className="btn-primary w-full py-3 justify-center shadow-lg shadow-brand-500/10 mt-6"
          >
            {submitting || resetSubmitting ? (
              <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
            ) : mode === 'signup' ? (
              'Create Account'
            ) : mode === 'reset' ? (
              'Reset Password'
            ) : (
              'Sign In'
            )}
          </button>

        </form>

        {/* Footer switch links */}
        <div className="text-center pt-2">
          {mode === 'reset' ? (
            <button
              onClick={() => switchMode('signin')}
              className="inline-flex items-center gap-1.5 text-sm font-bold text-brand-600 hover:text-brand-700 hover:underline transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Sign In
            </button>
          ) : mode === 'signup' ? (
            <p className="text-sm text-slate-500">
              Already have an account?{' '}
              <button
                onClick={() => switchMode('signin')}
                className="font-bold text-brand-600 hover:text-brand-700 hover:underline transition-colors"
              >
                Sign In
              </button>
            </p>
          ) : (
            <p className="text-sm text-slate-500">
              Don't have an account?{' '}
              <button
                onClick={() => switchMode('signup')}
                className="font-bold text-brand-600 hover:text-brand-700 hover:underline transition-colors"
              >
                Sign Up
              </button>
            </p>
          )}
        </div>

      </div>
    </div>
  );
};

export default AuthPage;
