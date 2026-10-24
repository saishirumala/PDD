import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Image,
  ActivityIndicator,
  Alert,
  SafeAreaView,
  StatusBar,
  Platform,
  RefreshControl,
  Dimensions
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';

const { width } = Dimensions.get('window');

// Automatically connect to our running backend.
// Uses local Wi-Fi IP and falls back to live Cloudflare tunnel for mobile data.
const API_URL = 'http://192.168.29.149:8000/api';
const FALLBACK_API_URL = 'https://fever-situations-dozen-consultancy.trycloudflare.com/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

// Attach JWT token automatically
api.interceptors.request.use(async (config) => {
  try {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (e) {}
  return config;
});

export default function App() {
  const [user, setUser] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard'); // dashboard, analyze, history, profile
  const [refreshing, setRefreshing] = useState(false);

  // Auth states
  const [authMode, setAuthMode] = useState('signin'); // signin, signup, reset
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [authSubmitting, setAuthSubmitting] = useState(false);
  const [authError, setAuthError] = useState(null);
  const [authSuccess, setAuthSuccess] = useState(null);

  // Dashboard states
  const [todayData, setTodayData] = useState(null);
  const [waterData, setWaterData] = useState(null);
  const [dashboardLoading, setDashboardLoading] = useState(false);

  // Analyze states
  const [selectedImage, setSelectedImage] = useState(null);
  const [mealDescription, setMealDescription] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzedMeal, setAnalyzedMeal] = useState(null);

  // History states
  const [mealsHistory, setMealsHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Profile goals state
  const [calorieGoal, setCalorieGoal] = useState('2000');
  const [proteinGoal, setProteinGoal] = useState('150');
  const [carbsGoal, setCarbsGoal] = useState('225');
  const [fatGoal, setFatGoal] = useState('65');
  const [savingProfile, setSavingProfile] = useState(false);

  // 1. Initial Auth Check on App startup
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = await AsyncStorage.getItem('token');
        if (storedToken) {
          try {
            const res = await api.get('/auth/me');
            setUser(res.data);
            setCalorieGoal(String(res.data.calorie_goal || 2000));
            setProteinGoal(String(res.data.protein_goal || 150));
            setCarbsGoal(String(res.data.carbs_goal || 225));
            setFatGoal(String(res.data.fat_goal || 65));
          } catch (err) {
            // Token expired or invalid
            await AsyncStorage.removeItem('token');
            setUser(null);
          }
        }
      } catch (err) {
        console.log('Session check error', err);
      } finally {
        setInitialLoading(false);
      }
    };
    initAuth();
  }, []);

  // 2. Fetch dashboard data when user logs in
  const fetchDashboardData = async () => {
    if (!user) return;
    setDashboardLoading(true);
    try {
      const [todayRes, waterRes] = await Promise.all([
        api.get('/dashboard/today').catch(() => null),
        api.get('/water/today').catch(() => null)
      ]);
      if (todayRes?.data) setTodayData(todayRes.data);
      if (waterRes?.data) setWaterData(waterRes.data);
    } catch (err) {
      console.log('Dashboard fetch error', err);
    } finally {
      setDashboardLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  // 3. Auth Handlers
  const handleAuthSubmit = async () => {
    setAuthError(null);
    setAuthSuccess(null);
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanEmail) {
      setAuthError('Please enter your email address.');
      return;
    }

    if (authMode === 'reset') {
      if (!password || password.length < 6) {
        setAuthError('New password must be at least 6 characters.');
        return;
      }
      if (password !== confirmPassword) {
        setAuthError('Passwords do not match.');
        return;
      }

      setAuthSubmitting(true);
      try {
        const res = await api.post('/auth/reset-password', {
          email: cleanEmail,
          new_password: password
        });
        setAuthSuccess(res.data?.message || 'Password updated! You can now log in.');
        setPassword('');
        setConfirmPassword('');
        setTimeout(() => setAuthMode('signin'), 2000);
      } catch (err) {
        const detail = err.response?.data?.detail;
        setAuthError(typeof detail === 'string' ? detail : 'Failed to reset password. Please verify the email.');
      } finally {
        setAuthSubmitting(false);
      }
      return;
    }

    if (!password) {
      setAuthError('Please enter your password.');
      return;
    }

    if (authMode === 'signup') {
      if (!name.trim()) {
        setAuthError('Please enter your full name.');
        return;
      }
      if (password.length < 6) {
        setAuthError('Password must be at least 6 characters.');
        return;
      }
      if (password !== confirmPassword) {
        setAuthError('Passwords do not match.');
        return;
      }
    }

    setAuthSubmitting(true);
    try {
      if (authMode === 'signup') {
        await api.post('/auth/register', {
          name: name.trim(),
          email: cleanEmail,
          password
        });
      }

      // Login
      const loginRes = await api.post('/auth/login', {
        email: cleanEmail,
        password
      });

      const token = loginRes.data.access_token;
      await AsyncStorage.setItem('token', token);

      const meRes = await api.get('/auth/me');
      setUser(meRes.data);
      setCalorieGoal(String(meRes.data.calorie_goal || 2000));
      setProteinGoal(String(meRes.data.protein_goal || 150));
      setCarbsGoal(String(meRes.data.carbs_goal || 225));
      setFatGoal(String(meRes.data.fat_goal || 65));
      setActiveTab('dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail;
      let msg = 'Authentication failed. Please verify credentials.';
      if (typeof detail === 'string') {
        msg = detail;
      } else if (err.message) {
        msg = err.message;
      }
      setAuthError(msg);
    } finally {
      setAuthSubmitting(false);
    }
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('token');
    setUser(null);
    setTodayData(null);
    setWaterData(null);
    setAnalyzedMeal(null);
    setAuthMode('signin');
  };

  // 4. Water Logging Handler
  const handleLogWater = async (amount) => {
    try {
      await api.post('/water', { amount_ml: amount });
      const res = await api.get('/water/today');
      setWaterData(res.data);
    } catch (err) {
      Alert.alert('Error', 'Failed to log water.');
    }
  };

  // 5. Image Picker Handlers
  const handleTakePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Camera Permission', 'Please enable camera access to take food photos.');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });
    if (!result.canceled && result.assets && result.assets.length > 0) {
      setSelectedImage(result.assets[0]);
    }
  };

  const handlePickFromGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Gallery Permission', 'Please enable gallery access to choose food photos.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });
    if (!result.canceled && result.assets && result.assets.length > 0) {
      setSelectedImage(result.assets[0]);
    }
  };

  // 6. Meal Analysis Handler
  const handleAnalyzeMeal = async () => {
    if (!selectedImage && !mealDescription.trim()) {
      Alert.alert('Missing Input', 'Please snap/select a photo or enter a meal description.');
      return;
    }

    setAnalyzing(true);
    try {
      const formData = new FormData();
      if (mealDescription.trim()) {
        formData.append('description', mealDescription.trim());
      }
      if (selectedImage) {
        const uri = selectedImage.uri;
        const filename = uri.split('/').pop() || 'meal.jpg';
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `image/${match[1]}` : 'image/jpeg';

        formData.append('image', {
          uri: Platform.OS === 'android' ? uri : uri.replace('file://', ''),
          name: filename,
          type: type,
        });
      }

      const res = await api.post('/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAnalyzedMeal(res.data);
      setSelectedImage(null);
      setMealDescription('');
      fetchDashboardData();
    } catch (err) {
      const detail = err.response?.data?.detail;
      Alert.alert('Analysis Failed', typeof detail === 'string' ? detail : 'AI food analysis could not be completed.');
    } finally {
      setAnalyzing(false);
    }
  };

  // 7. Fetch History
  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await api.get('/meals');
      setMealsHistory(res.data || []);
    } catch (err) {
      console.log('History fetch error', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'history') {
      fetchHistory();
    }
  }, [activeTab]);

  // 8. Profile Goals Save
  const handleSaveProfile = async () => {
    setSavingProfile(true);
    try {
      const res = await api.put('/profile', {
        calorie_goal: parseInt(calorieGoal, 10) || 2000,
        protein_goal: parseFloat(proteinGoal) || 150,
        carbs_goal: parseFloat(carbsGoal) || 225,
        fat_goal: parseFloat(fatGoal) || 65,
      });
      setUser(res.data);
      Alert.alert('Success', 'Profile goals updated successfully!');
      fetchDashboardData();
    } catch (err) {
      Alert.alert('Error', 'Failed to update profile targets.');
    } finally {
      setSavingProfile(false);
    }
  };

  // Initial loading screen
  if (initialLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#10b981" />
        <Text style={styles.loadingText}>Initializing NutriGuide...</Text>
      </View>
    );
  }

  // -------------------------------------------------------------
  // AUTH SCREEN
  // -------------------------------------------------------------
  if (!user) {
    return (
      <SafeAreaView style={styles.authContainer}>
        <StatusBar barStyle="dark-content" />
        <ScrollView contentContainerStyle={styles.authScroll}>
          {/* Logo & Header */}
          <View style={styles.authHeader}>
            <View style={styles.logoBadge}>
              <Text style={styles.logoEmoji}>🥗</Text>
            </View>
            <Text style={styles.appTitle}>NutriGuide</Text>
            <Text style={styles.appSubtitle}>
              {authMode === 'signup'
                ? 'Create an account to track food & macros'
                : authMode === 'reset'
                ? 'Reset your account password'
                : 'Sign in to access your nutrition dashboard'}
            </Text>
          </View>

          {/* Success Banner */}
          {authSuccess && (
            <View style={styles.successBanner}>
              <Text style={styles.successText}>✓ {authSuccess}</Text>
            </View>
          )}

          {/* Error Banner */}
          {authError && (
            <View style={styles.errorBanner}>
              <Text style={styles.errorText}>⚠️ {authError}</Text>
              {authMode === 'signin' && authError.toLowerCase().includes('password') && (
                <TouchableOpacity
                  onPress={() => {
                    setAuthMode('reset');
                    setAuthError(null);
                  }}
                  style={styles.inlineActionBtn}
                >
                  <Text style={styles.inlineActionText}>🔑 Reset forgotten password</Text>
                </TouchableOpacity>
              )}
              {authMode === 'signup' && authError.toLowerCase().includes('already exists') && (
                <TouchableOpacity
                  onPress={() => {
                    setAuthMode('signin');
                    setAuthError(null);
                  }}
                  style={styles.inlineActionBtn}
                >
                  <Text style={styles.inlineActionText}>👉 Switch to Sign In</Text>
                </TouchableOpacity>
              )}
            </View>
          )}

          {/* Input Fields */}
          <View style={styles.formCard}>
            {authMode === 'signup' && (
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Full Name</Text>
                <TextInput
                  style={styles.textInput}
                  placeholder="John Doe"
                  value={name}
                  onChangeText={setName}
                  autoCapitalize="words"
                />
              </View>
            )}

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Email Address</Text>
              <TextInput
                style={styles.textInput}
                placeholder="name@domain.com"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <View style={styles.labelRow}>
                <Text style={styles.inputLabel}>
                  {authMode === 'reset' ? 'New Password' : 'Password'}
                </Text>
                {authMode === 'signin' && (
                  <TouchableOpacity
                    onPress={() => {
                      setAuthMode('reset');
                      setAuthError(null);
                    }}
                  >
                    <Text style={styles.forgotLink}>Forgot password?</Text>
                  </TouchableOpacity>
                )}
              </View>
              <View style={styles.passwordRow}>
                <TextInput
                  style={[styles.textInput, { flex: 1 }]}
                  placeholder="••••••••"
                  secureTextEntry={!showPassword}
                  value={password}
                  onChangeText={setPassword}
                  autoCapitalize="none"
                />
                <TouchableOpacity
                  style={styles.eyeBtn}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Text style={styles.eyeText}>{showPassword ? 'Hide' : 'Show'}</Text>
                </TouchableOpacity>
              </View>
            </View>

            {(authMode === 'signup' || authMode === 'reset') && (
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>
                  {authMode === 'reset' ? 'Confirm New Password' : 'Confirm Password'}
                </Text>
                <TextInput
                  style={styles.textInput}
                  placeholder="••••••••"
                  secureTextEntry={!showPassword}
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                  autoCapitalize="none"
                />
              </View>
            )}

            <TouchableOpacity
              style={styles.primaryBtn}
              onPress={handleAuthSubmit}
              disabled={authSubmitting}
            >
              {authSubmitting ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.primaryBtnText}>
                  {authMode === 'signup'
                    ? 'Create Account'
                    : authMode === 'reset'
                    ? 'Reset Password'
                    : 'Sign In'}
                </Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Switch Modes */}
          <View style={styles.authFooter}>
            {authMode === 'reset' ? (
              <TouchableOpacity
                onPress={() => {
                  setAuthMode('signin');
                  setAuthError(null);
                }}
              >
                <Text style={styles.footerLink}>← Back to Sign In</Text>
              </TouchableOpacity>
            ) : authMode === 'signup' ? (
              <View style={styles.footerRow}>
                <Text style={styles.footerText}>Already have an account? </Text>
                <TouchableOpacity
                  onPress={() => {
                    setAuthMode('signin');
                    setAuthError(null);
                  }}
                >
                  <Text style={styles.footerLink}>Sign In</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <View style={styles.footerRow}>
                <Text style={styles.footerText}>Don't have an account? </Text>
                <TouchableOpacity
                  onPress={() => {
                    setAuthMode('signup');
                    setAuthError(null);
                  }}
                >
                  <Text style={styles.footerLink}>Sign Up</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // -------------------------------------------------------------
  // MEAL REPORT MODAL (After Analyzing)
  // -------------------------------------------------------------
  if (analyzedMeal) {
    const nutrition = analyzedMeal.nutrition || {};
    const insight = analyzedMeal.insight || {};
    const score = insight.health_score || 0;
    const isNonFood = score === 0 && nutrition.calories === 0;

    return (
      <SafeAreaView style={styles.appContainer}>
        <StatusBar barStyle="dark-content" />
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.reportCard}>
            <Text style={styles.reportSuper}>Analysis Complete</Text>
            <Text style={styles.reportTitle}>{analyzedMeal.meal_name}</Text>

            {analyzedMeal.image_url && (
              <Image
                source={{ uri: `${API_URL.replace('/api', '')}${analyzedMeal.image_url}` }}
                style={styles.reportImage}
                resizeMode="cover"
              />
            )}

            {/* Score Badge */}
            <View style={[styles.scoreBadge, { backgroundColor: isNonFood ? '#f1f5f9' : score >= 80 ? '#ecfdf5' : score >= 50 ? '#fffbeb' : '#fef2f2' }]}>
              <Text style={[styles.scoreNumber, { color: isNonFood ? '#64748b' : score >= 80 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444' }]}>
                {isNonFood ? 'Non-Food Item' : `${score} / 100`}
              </Text>
              <Text style={styles.scoreSub}>
                {isNonFood ? 'No nutritional calories assigned' : 'Nutritional Health Score'}
              </Text>
            </View>

            {/* Calories & Macros Grid */}
            <Text style={styles.sectionHeader}>Macronutrients</Text>
            <View style={styles.macroGrid}>
              <View style={styles.macroBox}>
                <Text style={styles.macroVal}>{nutrition.calories || 0}</Text>
                <Text style={styles.macroLbl}>Calories</Text>
              </View>
              <View style={[styles.macroBox, { borderLeftColor: '#ef4444', borderLeftWidth: 3 }]}>
                <Text style={styles.macroVal}>{nutrition.protein || 0}g</Text>
                <Text style={styles.macroLbl}>Protein</Text>
              </View>
              <View style={[styles.macroBox, { borderLeftColor: '#f59e0b', borderLeftWidth: 3 }]}>
                <Text style={styles.macroVal}>{nutrition.carbohydrates || 0}g</Text>
                <Text style={styles.macroLbl}>Carbs</Text>
              </View>
              <View style={[styles.macroBox, { borderLeftColor: '#3b82f6', borderLeftWidth: 3 }]}>
                <Text style={styles.macroVal}>{nutrition.fat || 0}g</Text>
                <Text style={styles.macroLbl}>Fat</Text>
              </View>
            </View>

            {/* AI Insights & Summary */}
            {insight.summary && (
              <View style={styles.insightBox}>
                <Text style={styles.insightTitle}>💡 AI Nutritionist Summary</Text>
                <Text style={styles.insightText}>{insight.summary}</Text>
              </View>
            )}

            {insight.recommendations && insight.recommendations.length > 0 && (
              <View style={styles.recsBox}>
                <Text style={styles.recsTitle}>Recommendations</Text>
                {insight.recommendations.map((rec, i) => (
                  <Text key={i} style={styles.recItem}>• {rec}</Text>
                ))}
              </View>
            )}

            <TouchableOpacity
              style={styles.primaryBtn}
              onPress={() => {
                setAnalyzedMeal(null);
                setActiveTab('dashboard');
              }}
            >
              <Text style={styles.primaryBtnText}>✓ Save & View in Dashboard</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // -------------------------------------------------------------
  // MAIN APP SCREEN (Dashboard / Analyze / History / Profile)
  // -------------------------------------------------------------
  return (
    <SafeAreaView style={styles.appContainer}>
      <StatusBar barStyle="dark-content" />

      {/* Top Header */}
      <View style={styles.appHeader}>
        <View>
          <Text style={styles.welcomeSuper}>Welcome back,</Text>
          <Text style={styles.welcomeName}>{user.name || 'Eater'} 👋</Text>
        </View>
        <TouchableOpacity style={styles.avatarBtn} onPress={() => setActiveTab('profile')}>
          <Text style={styles.avatarText}>{(user.name || 'U').charAt(0).toUpperCase()}</Text>
        </TouchableOpacity>
      </View>

      {/* Main Tab Content */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => {
            setRefreshing(true);
            fetchDashboardData();
          }} />
        }
      >
        {/* ----------------- DASHBOARD TAB ----------------- */}
        {activeTab === 'dashboard' && (
          <View style={styles.tabContent}>
            {/* Calories Card */}
            <View style={styles.card}>
              <Text style={styles.cardSuper}>TODAY'S CALORIES</Text>
              <View style={styles.calorieRow}>
                <Text style={styles.calorieCurrent}>
                  {todayData?.today?.calories || 0}
                </Text>
                <Text style={styles.calorieGoal}>
                  / {todayData?.today?.calorie_goal || 2000} kcal
                </Text>
              </View>
              {/* Progress Bar */}
              <View style={styles.progressBarBg}>
                <View
                  style={[
                    styles.progressBarFill,
                    {
                      width: `${Math.min(
                        100,
                        Math.round(
                          ((todayData?.today?.calories || 0) /
                            (todayData?.today?.calorie_goal || 2000)) *
                            100
                        )
                      )}%`,
                    },
                  ]}
                />
              </View>
            </View>

            {/* Macros Row */}
            <View style={styles.card}>
              <Text style={styles.cardSuper}>TARGET MACRONUTRIENTS</Text>
              <View style={styles.macroPillRow}>
                <View style={styles.macroPill}>
                  <Text style={[styles.macroPillName, { color: '#ef4444' }]}>Protein</Text>
                  <Text style={styles.macroPillVal}>{todayData?.today?.protein || 0}g</Text>
                  <Text style={styles.macroPillTarget}>of {todayData?.today?.protein_goal || 150}g</Text>
                </View>
                <View style={styles.macroPill}>
                  <Text style={[styles.macroPillName, { color: '#f59e0b' }]}>Carbs</Text>
                  <Text style={styles.macroPillVal}>{todayData?.today?.carbohydrates || 0}g</Text>
                  <Text style={styles.macroPillTarget}>of {todayData?.today?.carbs_goal || 225}g</Text>
                </View>
                <View style={styles.macroPill}>
                  <Text style={[styles.macroPillName, { color: '#3b82f6' }]}>Fat</Text>
                  <Text style={styles.macroPillVal}>{todayData?.today?.fat || 0}g</Text>
                  <Text style={styles.macroPillTarget}>of {todayData?.today?.fat_goal || 65}g</Text>
                </View>
                <View style={styles.macroPill}>
                  <Text style={[styles.macroPillName, { color: '#10b981' }]}>Fiber</Text>
                  <Text style={styles.macroPillVal}>{todayData?.today?.fiber || 0}g</Text>
                  <Text style={styles.macroPillTarget}>of {todayData?.today?.fiber_goal || 30}g</Text>
                </View>
              </View>
            </View>

            {/* Water Tracker Card */}
            <View style={styles.card}>
              <View style={styles.waterHeader}>
                <Text style={styles.cardSuper}>💧 HYDRATION TRACKER</Text>
                <Text style={styles.waterCount}>
                  {waterData?.total_ml || 0} / 2000 ml
                </Text>
              </View>
              <View style={styles.waterBtnRow}>
                <TouchableOpacity style={styles.waterBtn} onPress={() => handleLogWater(250)}>
                  <Text style={styles.waterBtnText}>+250 ml</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.waterBtn} onPress={() => handleLogWater(500)}>
                  <Text style={styles.waterBtnText}>+500 ml</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.waterBtn} onPress={() => handleLogWater(750)}>
                  <Text style={styles.waterBtnText}>+750 ml</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Quick Action Banner */}
            <TouchableOpacity
              style={styles.analyzeBanner}
              onPress={() => setActiveTab('analyze')}
            >
              <Text style={styles.bannerEmoji}>📸</Text>
              <View style={{ flex: 1 }}>
                <Text style={styles.bannerTitle}>Analyze a New Plate</Text>
                <Text style={styles.bannerSub}>Snap a food photo to detect calories & macros</Text>
              </View>
              <Text style={styles.bannerArrow}>→</Text>
            </TouchableOpacity>

            {/* Recent Meals Section */}
            <View style={styles.recentSection}>
              <Text style={styles.sectionTitle}>Today's Logged Plates</Text>
              {todayData?.meals && todayData.meals.length > 0 ? (
                todayData.meals.map((meal) => (
                  <View key={meal.id} style={styles.mealCard}>
                    <View style={styles.mealLeft}>
                      <Text style={styles.mealIcon}>🍽️</Text>
                      <View>
                        <Text style={styles.mealName}>{meal.meal_name}</Text>
                        <Text style={styles.mealSub}>{meal.nutrition?.protein || 0}g Protein • {meal.nutrition?.carbohydrates || 0}g Carbs</Text>
                      </View>
                    </View>
                    <Text style={styles.mealCalories}>{meal.nutrition?.calories || 0} kcal</Text>
                  </View>
                ))
              ) : (
                <View style={styles.emptyCard}>
                  <Text style={styles.emptyText}>No plates logged yet today. Snap a photo to start!</Text>
                </View>
              )}
            </View>
          </View>
        )}

        {/* ----------------- ANALYZE TAB ----------------- */}
        {activeTab === 'analyze' && (
          <View style={styles.tabContent}>
            <View style={styles.card}>
              <Text style={styles.analyzeHeaderTitle}>AI Food Scanner</Text>
              <Text style={styles.analyzeHeaderSub}>
                Take a photo or choose an image of your meal to calculate instant calories and nutrients.
              </Text>

              {/* Photo Preview or Select Buttons */}
              {selectedImage ? (
                <View style={styles.previewContainer}>
                  <Image source={{ uri: selectedImage.uri }} style={styles.previewImage} />
                  <TouchableOpacity
                    style={styles.changePhotoBtn}
                    onPress={() => setSelectedImage(null)}
                  >
                    <Text style={styles.changePhotoText}>✕ Remove Photo</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <View style={styles.photoActionRow}>
                  <TouchableOpacity style={styles.photoBtn} onPress={handleTakePhoto}>
                    <Text style={styles.photoBtnIcon}>📷</Text>
                    <Text style={styles.photoBtnText}>Take Photo</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.photoBtn} onPress={handlePickFromGallery}>
                    <Text style={styles.photoBtnIcon}>🖼️</Text>
                    <Text style={styles.photoBtnText}>Pick Gallery</Text>
                  </TouchableOpacity>
                </View>
              )}

              {/* Description Input */}
              <View style={[styles.inputGroup, { marginTop: 16 }]}>
                <Text style={styles.inputLabel}>Meal Description (Optional)</Text>
                <TextInput
                  style={[styles.textInput, { height: 75, textAlignVertical: 'top' }]}
                  placeholder="e.g. 2 South Indian dosas with sambar and coconut chutney"
                  value={mealDescription}
                  onChangeText={setMealDescription}
                  multiline
                />
              </View>

              <TouchableOpacity
                style={[styles.primaryBtn, { marginTop: 12 }]}
                onPress={handleAnalyzeMeal}
                disabled={analyzing}
              >
                {analyzing ? (
                  <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <ActivityIndicator color="#ffffff" style={{ marginRight: 8 }} />
                    <Text style={styles.primaryBtnText}>Analyzing with Gemini AI...</Text>
                  </View>
                ) : (
                  <Text style={styles.primaryBtnText}>✨ Analyze Plate with AI</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* ----------------- HISTORY TAB ----------------- */}
        {activeTab === 'history' && (
          <View style={styles.tabContent}>
            <Text style={styles.sectionTitle}>Meal History Logs</Text>
            {historyLoading ? (
              <ActivityIndicator color="#10b981" style={{ marginVertical: 20 }} />
            ) : mealsHistory.length > 0 ? (
              mealsHistory.map((meal) => (
                <View key={meal.id} style={styles.historyCard}>
                  <View style={styles.historyTopRow}>
                    <Text style={styles.historyName}>{meal.meal_name}</Text>
                    <Text style={styles.historyCalories}>{meal.nutrition?.calories || 0} kcal</Text>
                  </View>
                  <Text style={styles.historyDate}>
                    {new Date(meal.created_at).toLocaleDateString([], {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </Text>
                  <View style={styles.historyMacrosRow}>
                    <Text style={styles.historyMacro}>P: {meal.nutrition?.protein || 0}g</Text>
                    <Text style={styles.historyMacro}>C: {meal.nutrition?.carbohydrates || 0}g</Text>
                    <Text style={styles.historyMacro}>F: {meal.nutrition?.fat || 0}g</Text>
                    <Text style={styles.historyScore}>
                      {meal.insight?.health_score ? `Score: ${meal.insight.health_score}` : 'Non-Food'}
                    </Text>
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.emptyCard}>
                <Text style={styles.emptyText}>No meal records found in your log history.</Text>
              </View>
            )}
          </View>
        )}

        {/* ----------------- PROFILE TAB ----------------- */}
        {activeTab === 'profile' && (
          <View style={styles.tabContent}>
            <View style={styles.card}>
              <Text style={styles.sectionTitle}>Daily Nutrition Targets</Text>
              <Text style={styles.analyzeHeaderSub}>
                Set your daily calorie and macronutrient goals to calculate your daily progress.
              </Text>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Daily Calorie Goal (kcal)</Text>
                <TextInput
                  style={styles.textInput}
                  value={calorieGoal}
                  onChangeText={setCalorieGoal}
                  keyboardType="numeric"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Target Protein (grams)</Text>
                <TextInput
                  style={styles.textInput}
                  value={proteinGoal}
                  onChangeText={setProteinGoal}
                  keyboardType="numeric"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Target Carbohydrates (grams)</Text>
                <TextInput
                  style={styles.textInput}
                  value={carbsGoal}
                  onChangeText={setCarbsGoal}
                  keyboardType="numeric"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Target Fat (grams)</Text>
                <TextInput
                  style={styles.textInput}
                  value={fatGoal}
                  onChangeText={setFatGoal}
                  keyboardType="numeric"
                />
              </View>

              <TouchableOpacity
                style={styles.primaryBtn}
                onPress={handleSaveProfile}
                disabled={savingProfile}
              >
                {savingProfile ? (
                  <ActivityIndicator color="#ffffff" />
                ) : (
                  <Text style={styles.primaryBtnText}>Save Targets</Text>
                )}
              </TouchableOpacity>
            </View>

            {/* Account Details & Logout */}
            <View style={styles.card}>
              <Text style={styles.inputLabel}>Account Signed In</Text>
              <Text style={styles.accountEmail}>{user.email}</Text>

              <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
                <Text style={styles.logoutText}>Log Out of NutriGuide</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </ScrollView>

      {/* ----------------- BOTTOM TAB BAR ----------------- */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'dashboard' && styles.tabItemActive]}
          onPress={() => setActiveTab('dashboard')}
        >
          <Text style={styles.tabIcon}>📊</Text>
          <Text style={[styles.tabLabel, activeTab === 'dashboard' && styles.tabLabelActive]}>
            Dashboard
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'analyze' && styles.tabItemActive]}
          onPress={() => setActiveTab('analyze')}
        >
          <Text style={styles.tabIcon}>📷</Text>
          <Text style={[styles.tabLabel, activeTab === 'analyze' && styles.tabLabelActive]}>
            Analyze
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'history' && styles.tabItemActive]}
          onPress={() => setActiveTab('history')}
        >
          <Text style={styles.tabIcon}>📜</Text>
          <Text style={[styles.tabLabel, activeTab === 'history' && styles.tabLabelActive]}>
            History
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'profile' && styles.tabItemActive]}
          onPress={() => setActiveTab('profile')}
        >
          <Text style={styles.tabIcon}>👤</Text>
          <Text style={[styles.tabLabel, activeTab === 'profile' && styles.tabLabelActive]}>
            Profile
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

// -------------------------------------------------------------
// STYLES
// -------------------------------------------------------------
const styles = StyleSheet.create({
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 15,
    fontWeight: '600',
    color: '#64748b',
  },
  authContainer: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  authScroll: {
    padding: 24,
    justifyContent: 'center',
    minHeight: '100%',
  },
  authHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  logoBadge: {
    width: 60,
    height: 60,
    borderRadius: 20,
    backgroundColor: '#ecfdf5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  logoEmoji: {
    fontSize: 30,
  },
  appTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#0f172a',
    letterSpacing: -0.5,
  },
  appSubtitle: {
    fontSize: 13,
    color: '#64748b',
    textAlign: 'center',
    marginTop: 6,
    paddingHorizontal: 20,
  },
  formCard: {
    backgroundColor: '#ffffff',
    borderRadius: 24,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
    elevation: 3,
  },
  inputGroup: {
    marginBottom: 14,
  },
  inputLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#64748b',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 6,
  },
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  forgotLink: {
    fontSize: 12,
    fontWeight: '700',
    color: '#10b981',
  },
  textInput: {
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 14,
    color: '#0f172a',
  },
  passwordRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  eyeBtn: {
    position: 'absolute',
    right: 12,
    padding: 6,
  },
  eyeText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748b',
  },
  primaryBtn: {
    backgroundColor: '#10b981',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 8,
    shadowColor: '#10b981',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 3,
  },
  primaryBtnText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '800',
  },
  errorBanner: {
    backgroundColor: '#fef2f2',
    borderWidth: 1,
    borderColor: '#fecaca',
    borderRadius: 14,
    padding: 12,
    marginBottom: 16,
  },
  errorText: {
    color: '#b91c1c',
    fontSize: 13,
    fontWeight: '600',
  },
  inlineActionBtn: {
    marginTop: 8,
    backgroundColor: '#ffffff',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#fca5a5',
  },
  inlineActionText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#b91c1c',
  },
  successBanner: {
    backgroundColor: '#ecfdf5',
    borderWidth: 1,
    borderColor: '#a7f3d0',
    borderRadius: 14,
    padding: 12,
    marginBottom: 16,
  },
  successText: {
    color: '#047857',
    fontSize: 13,
    fontWeight: '700',
  },
  authFooter: {
    marginTop: 20,
    alignItems: 'center',
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  footerText: {
    fontSize: 13,
    color: '#64748b',
  },
  footerLink: {
    fontSize: 13,
    fontWeight: '800',
    color: '#10b981',
  },

  // App Layout Styles
  appContainer: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  appHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 14,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  welcomeSuper: {
    fontSize: 11,
    fontWeight: '700',
    color: '#94a3b8',
    textTransform: 'uppercase',
  },
  welcomeName: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
  },
  avatarBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#10b981',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '800',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 90,
  },
  tabContent: {
    gap: 14,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: '#f1f5f9',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 2,
  },
  cardSuper: {
    fontSize: 11,
    fontWeight: '800',
    color: '#94a3b8',
    letterSpacing: 0.5,
  },
  calorieRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginVertical: 6,
  },
  calorieCurrent: {
    fontSize: 32,
    fontWeight: '900',
    color: '#0f172a',
  },
  calorieGoal: {
    fontSize: 14,
    color: '#64748b',
    marginLeft: 6,
    fontWeight: '600',
  },
  progressBarBg: {
    height: 10,
    backgroundColor: '#f1f5f9',
    borderRadius: 5,
    overflow: 'hidden',
    marginTop: 4,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#10b981',
    borderRadius: 5,
  },
  macroPillRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
  },
  macroPill: {
    alignItems: 'center',
    flex: 1,
  },
  macroPillName: {
    fontSize: 11,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
  macroPillVal: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0f172a',
    marginTop: 2,
  },
  macroPillTarget: {
    fontSize: 10,
    color: '#94a3b8',
    marginTop: 1,
  },
  waterHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  waterCount: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0284c7',
  },
  waterBtnRow: {
    flexDirection: 'row',
    gap: 8,
  },
  waterBtn: {
    flex: 1,
    backgroundColor: '#e0f2fe',
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: 'center',
  },
  waterBtnText: {
    color: '#0284c7',
    fontSize: 12,
    fontWeight: '800',
  },
  analyzeBanner: {
    backgroundColor: '#0f172a',
    borderRadius: 20,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  bannerEmoji: {
    fontSize: 28,
    marginRight: 12,
  },
  bannerTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '800',
  },
  bannerSub: {
    color: '#94a3b8',
    fontSize: 11,
    marginTop: 2,
  },
  bannerArrow: {
    color: '#10b981',
    fontSize: 22,
    fontWeight: '900',
    marginLeft: 8,
  },
  recentSection: {
    marginTop: 6,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 10,
  },
  mealCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 14,
    marginBottom: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  mealLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  mealIcon: {
    fontSize: 22,
    marginRight: 10,
  },
  mealName: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0f172a',
  },
  mealSub: {
    fontSize: 11,
    color: '#94a3b8',
    marginTop: 2,
  },
  mealCalories: {
    fontSize: 13,
    fontWeight: '800',
    color: '#10b981',
    marginLeft: 8,
  },
  emptyCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  emptyText: {
    color: '#94a3b8',
    fontSize: 13,
    textAlign: 'center',
  },

  // Analyze Tab Styles
  analyzeHeaderTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0f172a',
  },
  analyzeHeaderSub: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 4,
    lineHeight: 18,
  },
  photoActionRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  photoBtn: {
    flex: 1,
    backgroundColor: '#f0fdf4',
    borderWidth: 1.5,
    borderStyle: 'dashed',
    borderColor: '#86efac',
    borderRadius: 16,
    paddingVertical: 24,
    alignItems: 'center',
  },
  photoBtnIcon: {
    fontSize: 32,
    marginBottom: 6,
  },
  photoBtnText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#166534',
  },
  previewContainer: {
    marginTop: 16,
    alignItems: 'center',
  },
  previewImage: {
    width: '100%',
    height: 220,
    borderRadius: 16,
  },
  changePhotoBtn: {
    marginTop: 8,
    backgroundColor: '#fef2f2',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  changePhotoText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#ef4444',
  },

  // Report Modal Styles
  reportCard: {
    backgroundColor: '#ffffff',
    borderRadius: 24,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
    elevation: 3,
  },
  reportSuper: {
    fontSize: 11,
    fontWeight: '800',
    color: '#10b981',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  reportTitle: {
    fontSize: 22,
    fontWeight: '900',
    color: '#0f172a',
    marginTop: 4,
    marginBottom: 12,
  },
  reportImage: {
    width: '100%',
    height: 200,
    borderRadius: 16,
    marginBottom: 14,
  },
  scoreBadge: {
    padding: 14,
    borderRadius: 16,
    alignItems: 'center',
    marginBottom: 16,
  },
  scoreNumber: {
    fontSize: 24,
    fontWeight: '900',
  },
  scoreSub: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748b',
    marginTop: 2,
  },
  sectionHeader: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 8,
  },
  macroGrid: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  macroBox: {
    flex: 1,
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    padding: 10,
    alignItems: 'center',
  },
  macroVal: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0f172a',
  },
  macroLbl: {
    fontSize: 10,
    fontWeight: '600',
    color: '#64748b',
    marginTop: 2,
  },
  insightBox: {
    backgroundColor: '#f0fdf4',
    padding: 14,
    borderRadius: 14,
    marginBottom: 12,
  },
  insightTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#166534',
    marginBottom: 4,
  },
  insightText: {
    fontSize: 12,
    color: '#15803d',
    lineHeight: 18,
  },
  recsBox: {
    backgroundColor: '#f8fafc',
    padding: 14,
    borderRadius: 14,
    marginBottom: 16,
  },
  recsTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#334155',
    marginBottom: 6,
  },
  recItem: {
    fontSize: 12,
    color: '#475569',
    marginBottom: 4,
    lineHeight: 18,
  },

  // History Tab Styles
  historyCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  historyTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  historyName: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0f172a',
    flex: 1,
  },
  historyCalories: {
    fontSize: 14,
    fontWeight: '800',
    color: '#10b981',
    marginLeft: 8,
  },
  historyDate: {
    fontSize: 11,
    color: '#94a3b8',
    marginTop: 2,
    marginBottom: 8,
  },
  historyMacrosRow: {
    flexDirection: 'row',
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingTop: 8,
  },
  historyMacro: {
    fontSize: 11,
    color: '#64748b',
    fontWeight: '600',
  },
  historyScore: {
    fontSize: 11,
    fontWeight: '700',
    color: '#10b981',
    marginLeft: 'auto',
  },

  // Profile Tab Styles
  accountEmail: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0f172a',
    marginTop: 4,
    marginBottom: 16,
  },
  logoutBtn: {
    backgroundColor: '#fef2f2',
    borderWidth: 1,
    borderColor: '#fecaca',
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: 'center',
  },
  logoutText: {
    color: '#ef4444',
    fontSize: 13,
    fontWeight: '700',
  },

  // Bottom Tab Bar
  tabBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#ffffff',
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingVertical: 10,
    paddingHorizontal: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 8,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 4,
    borderRadius: 12,
  },
  tabItemActive: {
    backgroundColor: '#ecfdf5',
  },
  tabIcon: {
    fontSize: 20,
    marginBottom: 2,
  },
  tabLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: '#94a3b8',
  },
  tabLabelActive: {
    color: '#10b981',
    fontWeight: '800',
  },
});
