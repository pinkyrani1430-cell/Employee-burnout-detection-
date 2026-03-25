import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  Keyboard, 
  Clock, 
  AlertCircle, 
  Play, 
  Square, 
  Moon, 
  Sun,
  LayoutDashboard
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

// --- Types ---
type StressLevel = 'Low' | 'Medium' | 'High';

interface Stats {
  kps: number;
  backspaces: number;
  avgPause: number;
  stressScore: number;
}

export default function App() {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [text, setText] = useState('');
  const [stats, setStats] = useState<Stats>({
    kps: 0,
    backspaces: 0,
    avgPause: 0,
    stressScore: 0
  });

  const timestampsRef = useRef<number[]>([]);
  const lastKeyTimeRef = useRef<number>(0);
  const smoothedSpeedRef = useRef<number>(0);

  // --- Theme Colors ---
  const theme = {
    bg: isDarkMode ? 'bg-[#1e1e1e]' : 'bg-slate-50',
    card: isDarkMode ? 'bg-[#2d2d2d] border-zinc-700' : 'bg-white border-slate-200',
    text: isDarkMode ? 'text-white' : 'text-slate-900',
    secondaryText: isDarkMode ? 'text-zinc-400' : 'text-slate-500',
    input: isDarkMode ? 'bg-[#252525] text-white border-zinc-700' : 'bg-slate-50 text-slate-900 border-slate-200',
  };

  // --- Monitoring Logic ---
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isMonitoring) return;

    const now = Date.now();
    timestampsRef.current.push(now);
    lastKeyTimeRef.current = now;
  };

  useEffect(() => {
    let interval: number;
    if (isMonitoring) {
      interval = window.setInterval(() => {
        const now = Date.now();
        
        // 5. Detect when the user stops typing (Idle detection > 3s)
        if (now - lastKeyTimeRef.current > 3000) {
          timestampsRef.current = [];
          smoothedSpeedRef.current = 0;
          setStats({ kps: 0, backspaces: 0, avgPause: 0, stressScore: 0 });
          return;
        }

        // 1. Sliding window: Only keep timestamps from the last 5 seconds
        timestampsRef.current = timestampsRef.current.filter(t => now - t <= 5000);
        
        // Raw speed: number_of_keys_in_last_5_seconds / 5
        const rawKps = timestampsRef.current.length / 5.0;

        // 2. Smoothing logic: smoothed = (prev * 0.7) + (curr * 0.3)
        smoothedSpeedRef.current = (smoothedSpeedRef.current * 0.7) + (rawKps * 0.3);
        const kps = smoothedSpeedRef.current;

        // New Mapping Logic: progress = min((kps / 10) * 100, 100)
        const score = Math.min((kps / 10.0) * 100, 100);

        let level = "Idle";
        let color = "bg-zinc-500";

        if (score === 0) {
          level = "Idle";
          color = "bg-zinc-500";
        } else if (score <= 30) {
          level = "Low Stress";
          color = "bg-emerald-500";
        } else if (score <= 60) {
          level = "Medium Stress";
          color = "bg-amber-500";
        } else {
          level = "High Stress";
          color = "bg-rose-500";
        }

        setStats({
          kps: Number(kps.toFixed(2)),
          backspaces: timestampsRef.current.length,
          avgPause: 0,
          stressScore: score
        });
      }, 1000); // 3. Update every 1 second
    }
    return () => clearInterval(interval);
  }, [isMonitoring]);

  const startMonitoring = () => {
    setIsMonitoring(true);
    setText('');
    timestampsRef.current = [];
    lastKeyTimeRef.current = Date.now();
    smoothedSpeedRef.current = 0;
    setStats({ kps: 0, backspaces: 0, avgPause: 0, stressScore: 0 });
  };

  const stopMonitoring = () => {
    setIsMonitoring(false);
    timestampsRef.current = [];
    smoothedSpeedRef.current = 0;
  };

  const getStressInfo = (score: number, kps: number): { level: string; color: string } => {
    if (score === 0) return { level: 'Idle', color: 'bg-zinc-500' };
    if (score <= 30) return { level: 'Low Stress', color: 'bg-emerald-500' };
    if (score <= 60) return { level: 'Medium Stress', color: 'bg-amber-500' };
    return { level: 'High Stress', color: 'bg-rose-500' };
  };

  const stressInfo = getStressInfo(stats.stressScore, stats.kps);

  return (
    <div className={`min-h-screen ${theme.bg} ${theme.text} transition-colors duration-300 font-sans p-6 md:p-12`}>
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-600/20">
              <LayoutDashboard className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Employee Burnout Detection</h1>
              <p className={theme.secondaryText}>Keyboard Behavior Analysis Dashboard</p>
            </div>
          </div>
          <button 
            onClick={() => setIsDarkMode(!isDarkMode)}
            className={`p-3 rounded-xl border ${theme.card} hover:scale-105 transition-transform`}
          >
            {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </header>

        {/* Stats Grid - Only KPS */}
        <div className="flex justify-center">
          <div className="w-full md:w-1/3">
            <StatCard 
              icon={<Activity className="text-blue-500" />} 
              title="Typing Speed" 
              value={stats.kps} 
              unit="KPS" 
              theme={theme} 
            />
          </div>
        </div>

        {/* Stress Level Card */}
        <div className={`p-6 rounded-2xl border ${theme.card} shadow-sm`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-zinc-400" />
              <span className="font-medium">Current Stress Level</span>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-bold text-white ${stressInfo.color}`}>
              {stressInfo.level}
            </span>
          </div>
          <div className="h-3 w-full bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${stats.stressScore}%` }}
              className={`h-full ${stressInfo.color}`}
            />
          </div>
        </div>

        {/* Typing Area */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Keyboard className="w-5 h-5" />
            Typing Analysis Area
          </h2>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isMonitoring ? "Start typing here..." : "Click 'Start Monitoring' to begin analysis"}
            disabled={!isMonitoring}
            className={`w-full h-64 p-6 rounded-2xl border ${theme.input} focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none font-mono text-lg`}
          />
        </div>

        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={startMonitoring}
            disabled={isMonitoring}
            className="flex-1 flex items-center justify-center gap-2 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-400 text-white font-bold rounded-xl transition-colors shadow-lg shadow-blue-600/20"
          >
            <Play className="w-5 h-5" />
            Start Monitoring
          </button>
          <button
            onClick={stopMonitoring}
            disabled={!isMonitoring}
            className="flex-1 flex items-center justify-center gap-2 py-4 bg-rose-600 hover:bg-rose-700 disabled:bg-zinc-400 text-white font-bold rounded-xl transition-colors shadow-lg shadow-rose-600/20"
          >
            <Square className="w-5 h-5" />
            Stop Monitoring
          </button>
        </div>

        <footer className={`text-center text-sm ${theme.secondaryText} pt-8`}>
          <p>Student Mini-Project: Employee Burnout Detection System</p>
          <p className="mt-1 italic">Note: This is a web preview. Use the Python files for the desktop app.</p>
        </footer>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, unit, theme }: { icon: React.ReactNode, title: string, value: number, unit: string, theme: any }) {
  return (
    <div className={`p-6 rounded-2xl border ${theme.card} shadow-sm flex flex-col items-center text-center space-y-2`}>
      <div className="p-3 bg-zinc-100 dark:bg-zinc-800 rounded-xl mb-2">
        {icon}
      </div>
      <span className={`text-sm font-semibold uppercase tracking-wider ${theme.secondaryText}`}>{title}</span>
      <div className="flex items-baseline gap-1">
        <span className="text-3xl font-bold">{value}</span>
        <span className="text-xs font-medium opacity-60">{unit}</span>
      </div>
    </div>
  );
}
