import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Salad, Eye, EyeOff, AlertCircle } from 'lucide-react';

const AuthPage: React.FC = () => {
  const { login, register, loading } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync mode with URL queries (e.g. ?signup=true)
  useEffect(() => {
    const signupParam = searchParams.get('signup');
    setIsSignUp(signupParam === 'true');
    setError(null);
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation checks
    if (!email || !password) {
      setError("Please fill in all required fields.");
      return;
    }

    if (isSignUp) {
      if (!name) {
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

    try {
      if (isSignUp) {
        await register(name, email, password);
      } else {
        await login(email, password);
      }
      navigate('/dashboard');
    } catch (err: any) {
      const serverMsg = err.response?.data?.detail || "Authentication failed. Please verify your credentials.";
      setError(serverMsg);
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
            {isSignUp ? 'Create your account' : 'Sign in to your account'}
          </h2>
          <p className="text-sm text-slate-500">
            {isSignUp ? 'Track foods, macros, and micro minerals' : 'Welcome back! Log in to view your dashboard'}
          </p>
        </div>

        {/* Error Alert Box */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-900 rounded-xl text-sm flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          
          {isSignUp && (
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
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Password</label>
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
              >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {isSignUp && (
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Confirm Password</label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="form-input"
                required
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-3 justify-center shadow-lg shadow-brand-500/10 mt-6"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
            ) : isSignUp ? (
              'Create Account'
            ) : (
              'Sign In'
            )}
          </button>

        </form>

        {/* Footer switch links */}
        <div className="text-center pt-2">
          <p className="text-sm text-slate-500">
            {isSignUp ? (
              <>
                Already have an account?{' '}
                <button
                  onClick={() => setIsSignUp(false)}
                  className="font-bold text-brand-600 hover:text-brand-700 hover:underline transition-colors"
                >
                  Sign In
                </button>
              </>
            ) : (
              <>
                Don't have an account?{' '}
                <button
                  onClick={() => setIsSignUp(true)}
                  className="font-bold text-brand-600 hover:text-brand-700 hover:underline transition-colors"
                >
                  Sign Up
                </button>
              </>
            )}
          </p>
        </div>

      </div>
    </div>
  );
};

export default AuthPage;
