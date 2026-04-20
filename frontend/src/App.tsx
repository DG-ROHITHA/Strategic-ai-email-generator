import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Sparkles, 
  Mic, 
  MicOff, 
  RotateCcw, 
  ChevronRight, 
  ChevronLeft, 
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  Activity,
  User,
  Target,
  FileText,
  LifeBuoy
} from 'lucide-react';
import axios from 'axios';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const API_BASE = 'http://localhost:8000';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const App = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [coachFeedback, setCoachFeedback] = useState(null);
  const [sendTimer, setSendTimer] = useState(null);
  const [countdown, setCountdown] = useState(0);

  // Form State
  const [formData, setFormData] = useState({
    email_purpose: '',
    recipient: '',
    situation: '',
    tone_preference: 'auto detect',
    key_points: '',
    drafting_style: 'balanced',
    improve_existing_email: false,
    existing_email: '',
    num_versions: 3
  });

  // Result State
  const [result, setResult] = useState(null);
  const [selectedVersion, setSelectedVersion] = useState(null);

  // Speech Recognition Setup
  const recognitionRef = useRef(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0])
          .map(result => result.transcript)
          .join('');
        
        // Update the active text area based on step
        if (step === 1) setFormData(prev => ({ ...prev, email_purpose: transcript }));
        if (step === 2) setFormData(prev => ({ ...prev, situation: transcript }));
      };
    }
  }, [step]);

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
    } else {
      recognitionRef.current?.start();
    }
    setIsRecording(!isRecording);
  };

  const handleMagicFill = async () => {
    if (!formData.email_purpose) return alert("Please enter email purpose first");
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/suggest-points`, {
        email_purpose: formData.email_purpose,
        recipient: formData.recipient
      });
      setFormData(prev => ({
        ...prev,
        key_points: res.data.suggested_points.map(p => `- ${p}`).join('\n')
      }));
    } catch (e) {
      alert("Magic Fill failed");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (isMagic = false) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/generate`, formData);
      setResult(res.data);
      setSelectedVersion(res.data.final_email);
      setStep(4);
    } catch (e) {
      alert("Generation failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  // Real-time Coaching Logic (Debounced)
  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (formData.existing_email.length > 20) {
        try {
          const res = await axios.post(`${API_BASE}/coach`, {
            current_draft: formData.existing_email,
            recipient: formData.recipient,
            intent: formData.email_purpose
          });
          setCoachFeedback(res.data);
        } catch (e) {
          console.error("Coach failed", e);
        }
      }
    }, 1000);

    return () => clearTimeout(delayDebounceFn);
  }, [formData.existing_email, formData.recipient, formData.email_purpose]);

  const handleSend = () => {
    setCountdown(5);
    const interval = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          setSendTimer(null);
          alert("Email sent (simulation)!");
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    setSendTimer(interval);
  };

  const cancelSend = () => {
    if (sendTimer) {
      clearInterval(sendTimer);
      setSendTimer(null);
      setCountdown(0);
      alert("Send canceled.");
    }
  };

  const steps = [
    { title: "Core Strategy", icon: <Target className="w-5 h-5" /> },
    { title: "Context", icon: <Activity className="w-5 h-5" /> },
    { title: "Drafting", icon: <FileText className="w-5 h-5" /> },
    { title: "Simulator", icon: <Sparkles className="w-5 h-5" /> }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 py-12 min-h-screen flex flex-col">
      {/* Header */}
      <header className="mb-12 text-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center space-x-2 text-sky-400 mb-4"
        >
          <Sparkles className="w-6 h-6" />
          <span className="font-bold tracking-widest uppercase text-sm">Strategic AI Assistant</span>
        </motion.div>
        <h1 className="text-5xl font-black mb-4">
          <span className="gradient-text">Outcome</span> Generator
        </h1>
        <p className="text-slate-400 max-w-2xl mx-auto text-lg">
          Transform your communication with predictive AI that simulates reactions and coaches your tone in real-time.
        </p>
      </header>

      {/* Progress Stepper */}
      <div className="flex items-center justify-center space-x-4 mb-12">
        {steps.map((s, i) => (
          <React.Fragment key={i}>
            <div className={cn(
              "flex flex-col items-center space-y-2",
              step > i + 1 ? "text-sky-400" : (step === i + 1 ? "text-white" : "text-slate-600")
            )}>
              <div className={cn(
                "w-12 h-12 rounded-full flex items-center justify-center transition-all duration-500",
                step > i + 1 ? "bg-sky-500/20 border border-sky-500" : 
                (step === i+1 ? "bg-sky-500 border border-sky-400 shadow-lg shadow-sky-500/20" : "bg-slate-900 border border-slate-800")
              )}>
                {s.icon}
              </div>
              <span className="text-xs font-bold uppercase">{s.title}</span>
            </div>
            {i < steps.length - 1 && (
              <div className={cn(
                "w-16 h-px",
                step > i + 1 ? "bg-sky-500" : "bg-slate-800"
              )} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Main Container */}
      <main className="flex-1 relative">
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="premium-card grid md:grid-cols-2 gap-8"
            >
              <div>
                <label className="block text-sm font-bold text-slate-400 uppercase mb-3">Email Purpose</label>
                <div className="relative">
                  <input 
                    type="text"
                    value={formData.email_purpose}
                    onChange={(e) => setFormData({...formData, email_purpose: e.target.value})}
                    placeholder="e.g. Reject client's price request diplomatically"
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-white focus:border-sky-500 outline-none transition-all pr-12"
                  />
                  <button 
                    onClick={toggleRecording}
                    className={cn(
                      "absolute right-3 top-3 p-2 rounded-lg transition-all",
                      isRecording ? "bg-red-500 text-white animate-pulse" : "bg-slate-700 text-slate-400 hover:text-white"
                    )}
                  >
                    {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                  </button>
                </div>

                <div className="mt-8">
                  <label className="block text-sm font-bold text-slate-400 uppercase mb-3">Recipient Identity</label>
                  <div className="flex items-center space-x-4 bg-slate-800/50 border border-slate-700 rounded-xl p-4 transition-all focus-within:border-sky-500">
                    <User className="text-sky-400 w-5 h-5" />
                    <input 
                      type="text"
                      value={formData.recipient}
                      onChange={(e) => setFormData({...formData, recipient: e.target.value})}
                      placeholder="e.g. Sarah Ahmed, CEO at TechFlow"
                      className="bg-transparent border-none text-white outline-none w-full"
                    />
                  </div>
                </div>

                <div className="mt-8">
                  <label className="block text-sm font-bold text-slate-400 uppercase mb-3">Drafting Style</label>
                  <div className="grid grid-cols-3 gap-3">
                    {['concise', 'balanced', 'detailed'].map((style) => (
                      <button
                        key={style}
                        onClick={() => setFormData({...formData, drafting_style: style})}
                        className={cn(
                          "py-2 px-3 rounded-lg text-xs font-bold uppercase transition-all border",
                          formData.drafting_style === style 
                            ? "bg-sky-500 border-sky-400 text-white shadow-lg shadow-sky-500/20" 
                            : "bg-slate-800/50 border-slate-700 text-slate-400 hover:text-white"
                        )}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="flex flex-col justify-center bg-sky-500/5 rounded-2xl p-8 border border-sky-500/10">
                <Target className="w-12 h-12 text-sky-400 mb-4" />
                <h3 className="text-xl font-bold mb-2">Smart Generator</h3>
                <p className="text-slate-400 mb-6">
                  Skip the details and get a draft immediately, or continue to provide specific context.
                </p>
                <div className="flex flex-col space-y-3">
                  <button onClick={() => handleGenerate(true)} className="btn-primary flex items-center justify-center space-x-2" disabled={loading}>
                    {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Sparkles className="w-5 h-5" />}
                    <span>Magic Draft</span>
                  </button>
                  <button onClick={() => setStep(2)} className="btn-secondary flex items-center justify-center space-x-2">
                    <span>Advanced Details</span>
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="premium-card flex flex-col space-y-8"
            >
              <div>
                <label className="block text-sm font-bold text-slate-400 uppercase mb-3">Describe the Situation</label>
                <textarea 
                  rows={6}
                  value={formData.situation}
                  onChange={(e) => setFormData({...formData, situation: e.target.value})}
                  placeholder="Provide all context here. What are the constraints? Why are you sending this now?"
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-white focus:border-sky-500 outline-none transition-all resize-none"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-3">
                  <label className="block text-sm font-bold text-slate-400 uppercase">Key Points</label>
                  <button 
                    onClick={handleMagicFill} 
                    className="text-xs font-bold text-sky-400 hover:text-sky-300 flex items-center space-x-1"
                    disabled={loading}
                  >
                    <Sparkles className="w-3 h-3" />
                    <span>Magic Fill</span>
                  </button>
                </div>
                <textarea 
                  rows={4}
                  value={formData.key_points}
                  onChange={(e) => setFormData({...formData, key_points: e.target.value})}
                  placeholder="- Point 1&#10;- Point 2"
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-white focus:border-sky-500 outline-none transition-all font-mono text-sm"
                />
              </div>

              <div className="flex justify-between items-center">
                <button onClick={() => setStep(1)} className="btn-secondary flex items-center space-x-2">
                  <ChevronLeft className="w-5 h-5" />
                  <span>Back</span>
                </button>
                <button onClick={() => setStep(3)} className="btn-primary flex items-center space-x-2">
                  <span>Ready to Draft</span>
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="grid md:grid-cols-3 gap-8"
            >
              <div className="md:col-span-2 premium-card">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold flex items-center space-x-2">
                    <Sparkles className="text-sky-400 w-5 h-5" />
                    <span>Active Workspace</span>
                  </h3>
                  <div className="flex items-center space-x-2 bg-sky-500/10 px-3 py-1 rounded-full">
                    <div className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
                    <span className="text-sky-400 text-xs font-bold uppercase tracking-tighter">Real-time coaching ON</span>
                  </div>
                </div>

                <textarea 
                  rows={15}
                  value={formData.existing_email}
                  onChange={(e) => setFormData({...formData, existing_email: e.target.value})}
                  placeholder="Start typing your email draft here..."
                  className="w-full bg-slate-800/30 border border-slate-700/50 rounded-2xl p-6 text-white focus:border-sky-500/50 outline-none transition-all resize-none text-lg leading-relaxed"
                />

                <div className="mt-8 flex justify-between items-center">
                  <button onClick={() => setStep(2)} className="btn-secondary">Back</button>
                  <button onClick={handleGenerate} className="btn-primary flex items-center space-x-2" disabled={loading}>
                    {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Sparkles className="w-5 h-5" />}
                    <span>Simulate Outcomes</span>
                  </button>
                </div>
              </div>

              <div className="space-y-6">
                <div className="premium-card bg-sky-500/5 border-sky-500/20">
                  <h4 className="text-sm font-bold text-sky-400 uppercase mb-4 flex items-center space-x-2">
                    <LifeBuoy className="w-4 h-4" />
                    <span>Real-time Coach</span>
                  </h4>
                  <AnimatePresence mode="wait">
                    {coachFeedback ? (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-4"
                      >
                        <div className={cn(
                          "p-3 rounded-lg flex items-start space-x-3",
                          coachFeedback.is_too_aggressive ? "bg-red-500/10 text-red-400" : "bg-emerald-500/10 text-emerald-400"
                        )}>
                          <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                          <p className="text-sm font-medium">{coachFeedback.tone_check}</p>
                        </div>
                        <div className="space-y-2">
                          {coachFeedback.suggestions.map((s, i) => (
                            <div key={i} className="flex items-start space-x-2 text-slate-300 text-sm italic">
                              <span className="text-sky-500 font-bold">•</span>
                              <p>{s}</p>
                            </div>
                          ))}
                        </div>
                        {coachFeedback.improved_sentence && (
                          <div className="mt-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                             <p className="text-xs text-slate-500 mb-2 font-bold uppercase">Suggested Improvement</p>
                             <p className="text-sm text-sky-200">"{coachFeedback.improved_sentence}"</p>
                          </div>
                        )}
                      </motion.div>
                    ) : (
                      <div className="py-8 text-center text-slate-600 italic text-sm">
                        Waiting for draft content...
                      </div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </motion.div>
          )}

          {step === 4 && result && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid lg:grid-cols-3 gap-8"
            >
              {/* Output Content */}
              <div className="lg:col-span-2 space-y-6">
                <div className="premium-card">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold">Optimized Version</h3>
                    <div className="flex space-x-2">
                      <button className="p-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"><RotateCcw className="w-4 h-4" /></button>
                      <button className="p-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"><ThumbsUp className="w-4 h-4 text-emerald-400" /></button>
                      <button className="p-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"><ThumbsDown className="w-4 h-4 text-red-400" /></button>
                    </div>
                  </div>
                  
                  <div className="bg-slate-950/50 border border-slate-800 rounded-2xl p-8 mb-6 font-serif text-lg leading-relaxed whitespace-pre-wrap">
                    {selectedVersion}
                  </div>

                  <div className="flex md:flex-row flex-col items-center justify-between gap-4 py-4 border-t border-slate-800">
                    <div className="flex flex-wrap gap-4">
                      {result.versions?.map((v, i) => (
                        <button 
                          key={i}
                          onClick={() => setSelectedVersion(v)}
                          className={cn(
                            "px-4 py-2 rounded-lg text-sm font-bold transition-all",
                            selectedVersion === v ? "bg-sky-500 text-white shadow-lg" : "bg-slate-800 text-slate-400 hover:text-white"
                          )}
                        >
                          Version {i + 1}
                        </button>
                      ))}
                    </div>
                    {countdown > 0 ? (
                      <button onClick={cancelSend} className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-xl font-bold transition-all flex items-center space-x-2 shadow-lg animate-pulse">
                        <RotateCcw className="w-5 h-5" />
                        <span>Undo Send ({countdown}s)</span>
                      </button>
                    ) : (
                      <button onClick={handleSend} className="btn-primary flex items-center space-x-2 px-10">
                        <Send className="w-5 h-5" />
                        <span>Final Send</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Sidebar: Simulation Results */}
              <div className="space-y-6">
                <div className="premium-card border-emerald-500/20 bg-emerald-500/5">
                   <h4 className="text-sm font-bold text-emerald-400 uppercase mb-6 flex items-center space-x-2">
                    <Sparkles className="w-4 h-4" />
                    <span>Outcome Prediction</span>
                   </h4>
                   
                   <div className="space-y-6">
                      <div className="space-y-4">
                        <div className="flex justify-between items-end">
                            <span className="text-sm text-slate-400 font-bold uppercase tracking-widest">Reaction Distribution</span>
                            <span className="text-emerald-400 font-black text-xl">{result.simulation?.predicted_reaction?.positive}% +</span>
                        </div>
                        <div className="h-4 bg-slate-800 rounded-full flex overflow-hidden border border-slate-700">
                            <div style={{width: `${result.simulation?.predicted_reaction?.positive}%`}} className="h-full bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.5)]" />
                            <div style={{width: `${result.simulation?.predicted_reaction?.neutral}%`}} className="h-full bg-sky-500" />
                            <div style={{width: `${result.simulation?.predicted_reaction?.negative}%`}} className="h-full bg-red-500" />
                        </div>
                        <div className="flex justify-between text-[10px] font-black uppercase text-slate-500">
                            <div className="flex items-center space-x-1"><div className="w-2 h-2 rounded-full bg-emerald-500" /><span>Positive</span></div>
                            <div className="flex items-center space-x-1"><div className="w-2 h-2 rounded-full bg-sky-500" /><span>Neutral</span></div>
                            <div className="flex items-center space-x-1"><div className="w-2 h-2 rounded-full bg-red-500" /><span>Negative</span></div>
                        </div>
                      </div>

                      <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-700">
                        <div className="flex items-center space-x-2 mb-2">
                           <AlertCircle className={cn(
                             "w-4 h-4",
                             result.simulation?.risk_level === 'high' ? "text-red-500" : (result.simulation?.risk_level === 'medium' ? "text-amber-500" : "text-emerald-500")
                           )} />
                           <span className="text-sm font-bold uppercase text-slate-300">Risk Assessment: {result.simulation?.risk_level}</span>
                        </div>
                        <p className="text-slate-400 text-xs leading-relaxed italic">
                          "{result.simulation?.risk_reasoning}"
                        </p>
                      </div>

                      <div className="space-y-3">
                         <h5 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Potential Objections</h5>
                         {result.simulation?.potential_objections?.map((obj, i) => (
                           <div key={i} className="flex items-center space-x-2 text-sm text-slate-300 bg-slate-800/50 p-2 rounded-lg border border-slate-700/50">
                              <span className="text-red-500 font-bold">!</span>
                              <span>{obj}</span>
                           </div>
                         ))}
                      </div>
                   </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer / Context */}
      <footer className="mt-12 py-8 border-t border-slate-800 flex justify-between items-center text-slate-500 text-sm">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Professional Model Active</span>
        </div>
        <div className="flex space-x-6">
          <a href="#" className="hover:text-white transition-colors">Privacy</a>
          <a href="#" className="hover:text-white transition-colors">Strategy Guide</a>
          <a href="#" className="hover:text-white transition-colors">Feedback</a>
        </div>
      </footer>
    </div>
  );
};

export default App;
