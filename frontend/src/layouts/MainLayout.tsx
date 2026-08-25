import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Menu, 
  X, 
  Salad, 
  LayoutDashboard, 
  PlusCircle, 
  History, 
  User as UserIcon, 
  LogOut,
  ShieldCheck,
  FileText
} from 'lucide-react';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Analyze Meal', href: '/analyze', icon: PlusCircle },
    { name: 'History Log', href: '/history', icon: History },
    { name: 'My Profile', href: '/profile', icon: UserIcon },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col bg-slate-50/50">
      {/* Navigation */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            
            {/* Logo */}
            <div className="flex items-center gap-2">
              <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2 text-brand-600 hover:opacity-90 transition-opacity">
                <div className="p-2 bg-brand-50 rounded-xl">
                  <Salad className="h-6 w-6 text-brand-500" />
                </div>
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-brand-600 to-emerald-500 bg-clip-text text-transparent">
                  NutriGuide
                </span>
              </Link>
            </div>

            {/* Desktop Navigation Links */}
            {user && (
              <nav className="hidden md:flex space-x-1">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                        active 
                          ? 'bg-brand-50 text-brand-600' 
                          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                      }`}
                    >
                      <Icon className="h-4.5 w-4.5" />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            )}

            {/* User Profile / Logout Button (Desktop) */}
            <div className="hidden md:flex items-center gap-4">
              {user ? (
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-sm font-semibold text-slate-900">{user.name}</p>
                    <p className="text-xs text-slate-500">{user.email}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="p-2.5 text-slate-400 hover:text-red-500 hover:bg-red-50/50 rounded-xl transition-all duration-200"
                    title="Log Out"
                  >
                    <LogOut className="h-5 w-5" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <Link to="/auth" className="btn-secondary px-4 py-2 text-sm">
                    Sign In
                  </Link>
                  <Link to="/auth?signup=true" className="btn-primary px-4 py-2 text-sm">
                    Get Started
                  </Link>
                </div>
              )}
            </div>

            {/* Mobile Menu Button */}
            <div className="flex items-center md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-b border-slate-100 bg-white">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {user ? (
                <>
                  <div className="px-3 py-2 border-b border-slate-100 mb-2">
                    <p className="text-sm font-bold text-slate-800">{user.name}</p>
                    <p className="text-xs text-slate-500">{user.email}</p>
                  </div>
                  {navigation.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex items-center gap-3 px-3 py-2 rounded-xl text-base font-medium transition-colors ${
                          active 
                            ? 'bg-brand-50 text-brand-600' 
                            : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                        }`}
                      >
                        <Icon className="h-5 w-5" />
                        {item.name}
                      </Link>
                    );
                  })}
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      handleLogout();
                    }}
                    className="flex w-full items-center gap-3 px-3 py-2 rounded-xl text-base font-medium text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="h-5 w-5" />
                    Logout
                  </button>
                </>
              ) : (
                <div className="p-3 space-y-2">
                  <Link
                    to="/auth"
                    onClick={() => setMobileMenuOpen(false)}
                    className="btn-secondary w-full justify-center text-sm"
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/auth?signup=true"
                    onClick={() => setMobileMenuOpen(false)}
                    className="btn-primary w-full justify-center text-sm"
                  >
                    Get Started
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Content Area */}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-100 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <Salad className="h-5 w-5 text-brand-500" />
            <span className="font-bold text-slate-800">NutriGuide</span>
            <span className="text-slate-400 text-sm">|</span>
            <span className="text-slate-500 text-sm">© {new Date().getFullYear()} All rights reserved.</span>
          </div>
          <div className="flex items-center gap-6">
            <Link to="/privacy" className="text-sm text-slate-500 hover:text-brand-500 flex items-center gap-1.5 transition-colors">
              <ShieldCheck className="h-4 w-4" />
              Privacy Policy
            </Link>
            <Link to="/terms" className="text-sm text-slate-500 hover:text-brand-500 flex items-center gap-1.5 transition-colors">
              <FileText className="h-4 w-4" />
              Terms of Service
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
