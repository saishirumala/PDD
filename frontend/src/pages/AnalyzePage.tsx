import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Meal } from '../types';
import { 
  Camera, 
  Upload, 
  X, 
  FileText, 
  Sparkles, 
  AlertCircle,
  HelpCircle
} from 'lucide-react';

const loadingSteps = [
  "Uploading your food photograph...",
  "AI identifying ingredients on your plate...",
  "Estimating serving sizes and calories...",
  "Calibrating micronutrient densities...",
  "Formulating personalized dietary insights..."
];

const AnalyzePage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [description, setDescription] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Cycle loading messages during analysis
  useEffect(() => {
    let interval: any;
    if (loading) {
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < loadingSteps.length - 1 ? prev + 1 : prev));
      }, 2500);
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // Handle image selection
  const processFile = (file: File) => {
    setError(null);
    const maxBytes = 5 * 1024 * 1024; // 5MB
    
    if (file.size > maxBytes) {
      setError("File size exceeds the 5MB limit. Please upload a smaller image.");
      return;
    }
    
    const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/jpg"];
    if (!allowedTypes.includes(file.type.toLowerCase())) {
      setError("Unsupported format. Please select a JPG, JPEG, PNG, or WEBP image.");
      return;
    }

    setImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleRemoveImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!description.trim() && !imageFile) {
      setError("You must upload a food photograph or enter a description text of your meal.");
      return;
    }

    setLoading(true);
    setLoadingStep(0);

    const formData = new FormData();
    if (description.trim()) {
      formData.append('description', description.trim());
    }
    if (imageFile) {
      formData.append('image', imageFile);
    }

    try {
      const response = await api.post<Meal>('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      // Redirect to the newly generated report
      navigate(`/meals/${response.data.id}`);
    } catch (err: any) {
      console.error("Meal analysis error:", err);
      const serverMsg = err.response?.data?.detail || "AI analysis failed. Please review inputs and retry.";
      setError(serverMsg);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      
      {/* Title */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center justify-center gap-2">
          <Sparkles className="h-7 w-7 text-brand-500" />
          AI Meal Analyzer
        </h1>
        <p className="text-slate-500 text-sm sm:text-base">
          Log food by taking a photo or describing it in detail.
        </p>
      </div>

      {loading ? (
        /* Loading Stepper Visual */
        <div className="bg-white border border-slate-150 shadow-xl rounded-3xl p-8 sm:p-12 flex flex-col items-center justify-center text-center py-20 space-y-6 min-h-[400px]">
          <div className="relative w-20 h-20">
            <div className="animate-spin rounded-full h-20 w-20 border-4 border-slate-100 border-t-brand-500"></div>
            <Camera className="h-8 w-8 text-brand-500 absolute inset-0 m-auto animate-pulse" />
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-slate-800">Analyzing Your Plate</h3>
            <p className="text-brand-600 font-semibold text-sm transition-all duration-300">
              {loadingSteps[loadingStep]}
            </p>
          </div>
          
          {/* Progress bar indication */}
          <div className="w-64 bg-slate-100 h-2 rounded-full overflow-hidden">
            <div 
              className="h-full bg-brand-500 transition-all duration-1000" 
              style={{ width: `${((loadingStep + 1) / loadingSteps.length) * 100}%` }}
            />
          </div>
        </div>
      ) : (
        /* Form Visual */
        <form onSubmit={handleAnalyze} className="bg-white border border-slate-150 shadow-sm rounded-3xl p-6 sm:p-8 space-y-6">
          
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-900 rounded-xl text-sm flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />
              <span className="font-semibold">{error}</span>
            </div>
          )}

          {/* Photo upload area */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Food Photograph (Optional)</label>
            
            {imagePreview ? (
              <div className="relative rounded-2xl overflow-hidden border border-slate-200 aspect-video max-h-[300px]">
                <img 
                  src={imagePreview} 
                  alt="Meal Preview" 
                  className="w-full h-full object-cover"
                />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="absolute top-3 right-3 p-2 bg-slate-900/60 hover:bg-slate-900/80 text-white rounded-full backdrop-blur-sm transition-all"
                  title="Remove Image"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div 
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={triggerFileSelect}
                className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[200px] ${
                  dragActive 
                    ? 'border-brand-500 bg-brand-50/20' 
                    : 'border-slate-200 hover:border-brand-300 hover:bg-slate-50/50'
                }`}
              >
                <input 
                  type="file" 
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/jpeg, image/jpg, image/png, image/webp"
                  className="hidden"
                />
                <div className="p-4 bg-brand-50 text-brand-500 rounded-2xl mb-3">
                  <Upload className="h-6 w-6" />
                </div>
                <p className="text-sm font-bold text-slate-700">Drag and drop your food photo here</p>
                <p className="text-xs text-slate-400 mt-1">or click to browse from device files</p>
                <p className="text-[10px] text-slate-400 mt-3 uppercase font-bold tracking-widest bg-slate-100 px-2 py-0.5 rounded">
                  Max size: 5MB (JPG, PNG, WEBP)
                </p>
              </div>
            )}
          </div>

          {/* Description box */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
              Meal Description
              <span className="text-slate-400 text-[10px] font-normal lowercase">(Optional if photo uploaded)</span>
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Example: Grilled salmon fillet, brown rice, steamed broccoli, and half an avocado..."
              rows={4}
              className="form-input resize-none py-3"
            />
            <p className="text-xs text-slate-400 leading-relaxed">
              💡 Providing details such as oils used, preparation styles, or portion details helps the AI deliver more calibrated estimates.
            </p>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="btn-primary w-full py-3.5 justify-center shadow-lg shadow-brand-500/10 text-base"
          >
            <Sparkles className="h-5 w-5" />
            Analyze Plate
          </button>

          <div className="p-3 bg-amber-50 border border-amber-100 rounded-xl text-amber-900 text-xs flex gap-2">
            <HelpCircle className="h-4.5 w-4.5 text-amber-600 shrink-0 mt-0.5" />
            <span>
              <strong>Disclaimer:</strong> Nutritional estimates are calculated using AI vision structures. Actual values may fluctuate based on ingredients and prep. They are not medical recommendations.
            </span>
          </div>

        </form>
      )}

    </div>
  );
};

export default AnalyzePage;
