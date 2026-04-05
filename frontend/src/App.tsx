import { Shield, Eye, Smartphone, UserCheck, Video, CheckCircle2, AlertCircle, Sun, Moon, Send, XCircle } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { useRef, useState, useEffect, FormEvent } from "react";

const Navbar = ({ isDarkMode, toggleDarkMode }: { isDarkMode: boolean, toggleDarkMode: () => void }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-gray-200/50 dark:border-gray-800/50 px-4 md:px-10 py-4 mb-4 md:mb-8 max-w-7xl mx-auto w-full sticky top-0 bg-white/80 dark:bg-black/80 z-50 backdrop-blur-md transition-colors">
      <div className="flex items-center gap-4 text-black dark:text-white">
        <div className="size-14">
          <img src="/logo-light.png" className="dark:hidden w-full h-full object-contain" alt="EduSecure Logo" />
          <img src="/logo-dark.png" className="hidden dark:block w-full h-full object-contain" alt="EduSecure Logo" />
        </div>
        <h2 className="text-2xl font-bold leading-tight tracking-tight font-headline">EduSecure</h2>
      </div>
      <div className="flex flex-1 justify-end gap-2 md:gap-8 items-center">
        <nav className="hidden lg:flex items-center gap-9">
          <a className="text-gray-600 dark:text-gray-400 text-sm font-medium hover:text-black dark:hover:text-white transition-colors" href="#features">Engine</a>
          <a className="text-gray-600 dark:text-gray-400 text-sm font-medium hover:text-black dark:hover:text-white transition-colors" href="#demo">Demo</a>
          <a className="text-gray-600 dark:text-gray-400 text-sm font-medium hover:text-black dark:hover:text-white transition-colors" href="#how-it-works">Features</a>
        </nav>
        <div className="flex items-center gap-2 md:gap-4">
          <button 
            onClick={toggleDarkMode}
            className="p-2 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors flex items-center gap-2 px-2 md:px-3"
            aria-label="Toggle dark mode"
          >
            {isDarkMode ? <Sun className="size-5" /> : <Moon className="size-5" />}
            <span className="hidden sm:inline text-xs font-bold uppercase tracking-wider">{isDarkMode ? 'Light' : 'Dark'}</span>
          </button>
          <button 
            onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
            className="hidden sm:flex min-w-[100px] md:min-w-[120px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-10 md:h-12 px-4 md:px-5 bg-black dark:bg-white text-white dark:text-black text-sm font-bold leading-normal tracking-wide hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors"
          >
            Book a Demo
          </button>
          <button 
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="lg:hidden p-2 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
          >
            <div className="flex flex-col gap-1 w-5">
              <span className={`h-0.5 w-full bg-current transition-transform ${isMenuOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
              <span className={`h-0.5 w-full bg-current transition-opacity ${isMenuOpen ? 'opacity-0' : ''}`}></span>
              <span className={`h-0.5 w-full bg-current transition-transform ${isMenuOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
            </div>
          </button>
        </div>
      </div>
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-full left-0 w-full bg-white dark:bg-black border-b border-gray-200 dark:border-gray-800 p-6 flex flex-col gap-4 lg:hidden shadow-xl"
          >
            <a onClick={() => setIsMenuOpen(false)} className="text-gray-600 dark:text-gray-400 text-lg font-medium" href="#features">Engine</a>
            <a onClick={() => setIsMenuOpen(false)} className="text-gray-600 dark:text-gray-400 text-lg font-medium" href="#demo">Demo</a>
            <a onClick={() => setIsMenuOpen(false)} className="text-gray-600 dark:text-gray-400 text-lg font-medium" href="#how-it-works">Features</a>
            <button 
              onClick={() => {
                setIsMenuOpen(false);
                document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="w-full bg-black dark:bg-white text-white dark:text-black font-bold py-4 rounded-xl mt-2"
            >
              Book a Demo
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

const Hero = () => (
  <section className="flex flex-col gap-8 md:gap-12 px-4 py-8 md:py-16 lg:flex-row lg:items-center max-w-7xl mx-auto">
    <div className="flex flex-col gap-6 md:gap-8 lg:w-1/2">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex flex-col gap-4 text-left"
      >
        <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#69ff87] text-[#002108] text-[10px] md:text-xs font-bold uppercase tracking-widest w-fit">
          <CheckCircle2 className="size-3" />
          New CV Model 4.0
        </span>
        <h1 className="text-black dark:text-white text-4xl md:text-5xl lg:text-6xl font-extrabold leading-[1.1] tracking-tight font-headline">
          Integrity Powered by <span className="text-[#004ced]">AI</span>
        </h1>
        <p className="text-gray-600 dark:text-gray-400 text-base md:text-lg lg:text-xl font-normal leading-relaxed max-w-[540px]">
          EduSecure leverages proprietary Computer Vision to monitor academic honesty in real-time, delivering a seamless proctoring experience that respects student privacy.
        </p>
      </motion.div>
      <div className="flex flex-wrap gap-3 md:gap-4">
        <button 
          onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
          className="flex flex-1 sm:flex-none min-w-[140px] md:min-w-[160px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-12 md:h-14 px-6 bg-black dark:bg-white text-white dark:text-black text-sm md:text-base font-bold transition-transform hover:scale-[1.02]"
        >
          Book a Demo
        </button>
        <button 
          onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
          className="flex flex-1 sm:flex-none min-w-[140px] md:min-w-[160px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-12 md:h-14 px-6 bg-gray-100 dark:bg-gray-800 text-black dark:text-white text-sm md:text-base font-bold hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        >
          View Solutions
        </button>
      </div>
    </div>
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8, delay: 0.2 }}
      className="lg:w-1/2"
    >
      <div className="relative rounded-[1.5rem] md:rounded-[2rem] overflow-hidden editorial-shadow bg-gray-200 dark:bg-gray-800 aspect-[4/3] group">
        <img 
          alt="University student in a modern workspace" 
          className="w-full h-full object-cover grayscale opacity-90 transition-transform duration-700 group-hover:scale-105" 
          src="https://picsum.photos/seed/edusecure-student/1200/900"
          referrerPolicy="no-referrer"
        />
        <div className="absolute inset-0 bg-gradient-to-tr from-black/20 to-transparent"></div>
        <div className="absolute top-4 left-4 md:top-6 md:left-6 flex items-center gap-2 glass-panel dark:bg-black/40 px-3 py-1.5 md:px-4 md:py-2 rounded-full border border-white/20">
          <span className="relative flex h-2 w-2 md:h-3 md:w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 md:h-3 md:w-3 bg-green-500"></span>
          </span>
          <span className="text-[10px] md:text-xs font-bold text-black dark:text-white tracking-wide">AI MONITORING ACTIVE</span>
        </div>
      </div>
    </motion.div>
  </section>
);

const Features = () => (
  <section id="features" className="flex flex-col gap-8 md:gap-12 px-4 py-12 md:py-24 bg-gray-50 dark:bg-gray-900/50 rounded-[2rem] md:rounded-[3rem] my-8 md:my-12 max-w-7xl mx-auto">
    <div className="flex flex-col md:flex-row justify-between items-end gap-6">
      <div className="flex flex-col gap-4">
        <h3 className="text-black dark:text-white text-3xl md:text-4xl font-bold tracking-tight font-headline">The Forensic Engine</h3>
        <p className="text-gray-600 dark:text-gray-400 text-base md:text-lg max-w-[500px]">Our CV model doesn't just watch; it understands context, distinguishing between natural movement and academic dishonesty.</p>
      </div>
      <div className="h-[1px] flex-grow bg-gray-200 dark:bg-gray-800 hidden md:block mb-4 ml-8"></div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
      {[
        { 
          title: "Gaze Analysis", 
          desc: "Advanced saccadic movement tracking identifies when students are referencing off-screen materials or secondary devices.",
          icon: Eye
        },
        { 
          title: "Object Shield", 
          desc: "Real-time detection for prohibited items including smartphones, smartwatches, and unauthorized printed resources.",
          icon: Smartphone
        },
        { 
          title: "Identity Integrity", 
          desc: "Biometric continuous verification ensures the person who started the test is the same one finishing it, every second.",
          icon: UserCheck
        }
      ].map((feature, i) => (
        <motion.div 
          key={i}
          whileHover={{ y: -5 }}
          className="group flex flex-col gap-4 md:gap-6 p-6 md:p-8 rounded-[1.5rem] md:rounded-[2rem] bg-white dark:bg-gray-800 transition-all hover:editorial-shadow border border-transparent hover:border-gray-100 dark:hover:border-gray-700"
        >
          <div className="w-12 h-12 md:w-14 md:h-14 flex items-center justify-center rounded-xl md:rounded-2xl bg-gray-100 dark:bg-gray-700 text-black dark:text-white">
            <feature.icon className="size-6 md:size-7" />
          </div>
          <div className="flex flex-col gap-2">
            <h4 className="text-black dark:text-white text-lg md:text-xl font-bold font-headline">{feature.title}</h4>
            <p className="text-sm md:text-base text-gray-600 dark:text-gray-400 leading-relaxed">{feature.desc}</p>
          </div>
        </motion.div>
      ))}
    </div>
  </section>
);

const Demo = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [detectionResults, setDetectionResults] = useState<any>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startWebcam = async () => {
    try {
      const newStream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720 } 
      });
      setStream(newStream);
      setError(null);
    } catch (err) {
      console.error("Error accessing webcam:", err);
      setError("Could not access camera. Please ensure permissions are granted.");
    }
  };

  const stopWebcam = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsDetecting(false);
    setDetectionResults(null);
  };

  const captureFrame = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg', 0.8);
      }
    }
    return null;
  };

  const sendFrameToBackend = async () => {
    const frameData = captureFrame();
    if (!frameData) return;

    try {
      const base64Data = frameData.split(',')[1]; // Remove data URL prefix
      const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000/detect_base64' : '/detect_base64';
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: base64Data
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      // Only update results if detection hasn't been stopped
      if (intervalRef.current) {
        setDetectionResults(result);
      }
    } catch (err) {
      console.error("Error sending frame to backend:", err);
      // Don't set error state here to avoid disrupting the UI
    }
  };

  const startDetection = () => {
    setIsDetecting(true);
    // Send frames every 500ms for near real-time detection
    intervalRef.current = setInterval(sendFrameToBackend, 500);
  };

  const stopDetection = () => {
    setIsDetecting(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setDetectionResults(null);
  };

  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [stream]);

  // Draw bounding boxes on overlay canvas whenever detection results update
  useEffect(() => {
    const overlay = overlayCanvasRef.current;
    const video = videoRef.current;
    if (!overlay || !video) return;

    const ctx = overlay.getContext('2d');
    if (!ctx) return;

    // Match overlay canvas size to the video element's display size
    const rect = video.getBoundingClientRect();
    overlay.width = rect.width;
    overlay.height = rect.height;

    // Clear previous drawings
    ctx.clearRect(0, 0, overlay.width, overlay.height);

    if (detectionResults?.mobile_boxes && detectionResults.mobile_boxes.length > 0) {
      for (const box of detectionResults.mobile_boxes) {
        const x = box.x1 * overlay.width;
        const y = box.y1 * overlay.height;
        const w = (box.x2 - box.x1) * overlay.width;
        const h = (box.y2 - box.y1) * overlay.height;

        // Draw box
        ctx.strokeStyle = '#ff3b3b';
        ctx.lineWidth = 3;
        ctx.strokeRect(x, y, w, h);

        // Draw corner accents for a more premium look
        const cornerLen = Math.min(w, h) * 0.2;
        ctx.strokeStyle = '#ff3b3b';
        ctx.lineWidth = 4;
        // Top-left
        ctx.beginPath(); ctx.moveTo(x, y + cornerLen); ctx.lineTo(x, y); ctx.lineTo(x + cornerLen, y); ctx.stroke();
        // Top-right
        ctx.beginPath(); ctx.moveTo(x + w - cornerLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + cornerLen); ctx.stroke();
        // Bottom-left
        ctx.beginPath(); ctx.moveTo(x, y + h - cornerLen); ctx.lineTo(x, y + h); ctx.lineTo(x + cornerLen, y + h); ctx.stroke();
        // Bottom-right
        ctx.beginPath(); ctx.moveTo(x + w - cornerLen, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - cornerLen); ctx.stroke();

        // Draw label background
        const label = box.label || `Phone ${box.conf}`;
        ctx.font = 'bold 14px Inter, sans-serif';
        const textWidth = ctx.measureText(label).width;
        const labelH = 24;
        ctx.fillStyle = 'rgba(255, 59, 59, 0.85)';
        ctx.fillRect(x, y - labelH, textWidth + 12, labelH);

        // Draw label text
        ctx.fillStyle = '#ffffff';
        ctx.fillText(label, x + 6, y - 7);
      }
    }
  }, [detectionResults]);

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'HIGH': return 'text-red-500';
      case 'MEDIUM': return 'text-yellow-500';
      case 'LOW': return 'text-green-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <section id="demo" className="py-12 md:py-24 px-4 flex flex-col gap-8 md:gap-12 max-w-7xl mx-auto">
      <div className="text-center max-w-[700px] mx-auto flex flex-col gap-4">
        <h2 className="text-3xl md:text-4xl font-bold text-black dark:text-white font-headline">Experience Real-Time Detection</h2>
        <p className="text-gray-600 dark:text-gray-400 text-sm md:text-base">See through the eyes of the AI. Our demo showcases how non-invasive monitoring provides high-fidelity integrity reports.</p>
      </div>
      
      <div className="relative max-w-[1000px] mx-auto w-full rounded-[1.5rem] md:rounded-[2.5rem] overflow-hidden bg-black aspect-video editorial-shadow group">
        <div className="absolute inset-0 bg-neutral-900 flex items-center justify-center">
          {!stream ? (
            <div className="text-center flex flex-col items-center gap-4 md:gap-6 z-10 px-4">
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                className="w-16 h-16 md:w-20 md:h-20 rounded-full border-4 border-dashed border-gray-600 flex items-center justify-center"
              >
                <Video className="text-gray-400 size-6 md:size-8" />
              </motion.div>
              <div className="flex flex-col items-center gap-3 md:gap-4">
                <button 
                  onClick={startWebcam}
                  className="bg-[#69ff87] text-[#002108] font-bold px-6 py-3 md:px-8 md:py-4 rounded-xl hover:brightness-90 transition-all text-sm md:text-base"
                >
                  Initialize Demo Webcam
                </button>
                {error && (
                  <div className="flex items-center gap-2 text-red-400 bg-red-400/10 px-4 py-2 rounded-lg border border-red-400/20">
                    <AlertCircle className="size-4" />
                    <p className="text-xs md:text-sm font-medium">{error}</p>
                  </div>
                )}
              </div>
              <p className="text-white/40 text-[10px] md:text-sm font-medium uppercase tracking-widest">Privacy Protected • Local Processing Only</p>
            </div>
          ) : (
            <div className="relative w-full h-full">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                muted
                className="w-full h-full object-cover"
              />
              <canvas ref={canvasRef} className="hidden" />
              {/* Overlay canvas for bounding boxes */}
              <canvas 
                ref={overlayCanvasRef} 
                className="absolute inset-0 w-full h-full pointer-events-none z-10"
              />
              
              {/* Detection Controls */}
              <div className="absolute top-4 left-4 flex gap-2 z-20">
                {!isDetecting ? (
                  <button 
                    onClick={startDetection}
                    className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg transition-colors text-sm font-bold"
                  >
                    Start Detection
                  </button>
                ) : (
                  <button 
                    onClick={stopDetection}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg transition-colors text-sm font-bold"
                  >
                    Stop Detection
                  </button>
                )}
              </div>
              
              {detectionResults && isDetecting && (
                <div className="absolute top-4 right-4 bg-black/85 backdrop-blur-sm text-white p-4 rounded-xl max-w-xs z-20 border border-white/10 shadow-2xl">
                  <div className="flex items-center gap-2 mb-3">
                    <div className={`w-2 h-2 rounded-full ${
                      detectionResults.status === 'calibrating' ? 'bg-yellow-500' : 
                      (detectionResults.mobile_detected || detectionResults.head_direction !== 'Looking at Screen' || detectionResults.gaze_direction !== 'Looking at Screen') ? 'bg-red-500' : 'bg-green-500'
                    } animate-pulse`} />
                    <span className="text-xs font-bold uppercase tracking-wider">
                      {detectionResults.status === 'calibrating' ? 'Calibrating...' : 'Live Monitoring'}
                    </span>
                  </div>
                  
                  {/* YOLO Detection Results */}
                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between gap-4">
                      <span className="text-white/60">Phone:</span>
                      <span className={detectionResults.mobile_detected ? 'text-red-400 font-bold' : 'text-green-400'}>
                        {detectionResults.mobile_detected ? '⚠ Detected' : '✓ None'}
                      </span>
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-white/60">Head:</span>
                      <span className={detectionResults.head_direction !== 'Looking at Screen' ? 'text-yellow-400' : 'text-green-400'}>
                        {detectionResults.head_direction || 'None'}
                      </span>
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-white/60">Gaze:</span>
                      <span className={detectionResults.gaze_direction !== 'Looking at Screen' ? 'text-yellow-400' : 'text-green-400'}>
                        {detectionResults.gaze_direction || 'None'}
                      </span>
                    </div>
                    {detectionResults.behavior_state && (
                      <div className="flex justify-between gap-4">
                        <span className="text-white/60">Gesture:</span>
                        <span className={`font-semibold ${
                          detectionResults.behavior_state === 'Writing' ? 'text-green-400' :
                          detectionResults.behavior_state === 'Looking Around' ? 'text-yellow-400' :
                          detectionResults.behavior_state === 'Using Phone' ? 'text-red-400' :
                          detectionResults.behavior_state === 'Suspicious' ? 'text-orange-400' :
                          'text-blue-400'
                        }`}>
                          {detectionResults.behavior_state}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {/* Gemini AI Verdict */}
                  {detectionResults.gemini && detectionResults.gemini.available && (
                    <div className="mt-3 pt-3 border-t border-white/10">
                      <div className="flex items-center gap-1.5 mb-2">
                        <svg className="size-3" viewBox="0 0 24 24" fill="none">
                          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-purple-400"/>
                        </svg>
                        <span className="text-[10px] font-bold uppercase tracking-widest text-purple-400">Gemini AI Verdict</span>
                      </div>
                      <div className="space-y-1.5 text-xs">
                        <div className="flex justify-between gap-4">
                          <span className="text-white/60">Risk:</span>
                          <span className={`font-bold ${
                            detectionResults.gemini.risk === 'HIGH' ? 'text-red-400' :
                            detectionResults.gemini.risk === 'MEDIUM' ? 'text-yellow-400' :
                            detectionResults.gemini.risk === 'LOW' ? 'text-green-400' :
                            detectionResults.gemini.risk === 'LOADING' ? 'text-blue-400 animate-pulse' :
                            'text-gray-400'
                          }`}>
                            {detectionResults.gemini.risk}
                          </span>
                        </div>
                        {detectionResults.gemini.integrity_score !== undefined && (
                          <div className="flex justify-between gap-4">
                            <span className="text-white/60">Integrity:</span>
                            <span className={`font-bold ${
                              detectionResults.gemini.integrity_score >= 70 ? 'text-green-400' :
                              detectionResults.gemini.integrity_score >= 40 ? 'text-yellow-400' :
                              'text-red-400'
                            }`}>
                              {detectionResults.gemini.integrity_score}%
                            </span>
                          </div>
                        )}
                        {detectionResults.gemini.summary && (
                          <p className="text-[10px] text-white/50 leading-relaxed mt-1">
                            {detectionResults.gemini.summary}
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {detectionResults.status === 'calibrating' && (
                    <div className="mt-2 pt-2 border-t border-gray-600">
                      <div className="text-xs text-yellow-400">
                        {detectionResults.message}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              <button 
                onClick={stopWebcam}
                className="absolute bottom-4 right-4 bg-red-500 hover:bg-red-600 text-white p-2 md:p-3 rounded-full shadow-lg transition-colors z-20 group/stop"
                title="Stop Webcam"
              >
                <XCircle className="size-5 md:size-6" />
                <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-black text-white text-[10px] md:text-xs py-1 px-2 rounded opacity-0 group-hover/stop:opacity-100 transition-opacity whitespace-nowrap">Stop Feed</span>
              </button>
            </div>
          )}
          <div className="absolute inset-0 opacity-20 pointer-events-none">
            <div className="absolute top-0 left-0 w-full h-full border-[20px] md:border-[40px] border-transparent border-t-white/10 border-l-white/10"></div>
            <div className="absolute bottom-0 right-0 w-full h-full border-[20px] md:border-[40px] border-transparent border-b-white/10 border-r-white/10"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

const Workflow = () => (
  <section id="how-it-works" className="py-12 md:py-24 px-4 flex flex-col gap-12 md:gap-16 max-w-7xl mx-auto">
    <div className="flex flex-col gap-4">
      <h2 className="text-3xl md:text-4xl font-bold text-black dark:text-white font-headline">The Secure Workflow</h2>
      <p className="text-gray-600 dark:text-gray-400 text-sm md:text-base max-w-md">How we maintain the highest standards of academic integrity from start to finish.</p>
    </div>
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 md:gap-12 relative">
      <div className="absolute top-8 left-0 w-full h-[2px] bg-gray-100 dark:bg-gray-800 hidden md:block z-0"></div>
      {[
        { step: "01", title: "Environment Scan", desc: "A mandatory 360° room verification ensures a secure physical testing environment before access is granted." },
        { step: "02", title: "Identity Lock", desc: "AI analyzes facial features and ID documentation to create a biometric hash for continuous verification." },
        { step: "03", title: "Live Evaluation", desc: "Computer Vision tracks gaze, body position, and audio levels, flagging anomalies with surgical precision." },
        { step: "04", title: "Integrity Report", desc: "A detailed session audit is generated for instructors, highlighting time-stamped events and risk probabilities." }
      ].map((item, i) => (
        <div key={i} className="relative z-10 flex flex-col gap-4 md:gap-6">
          <div className={`w-12 h-12 md:w-16 md:h-16 rounded-xl md:rounded-2xl flex items-center justify-center font-bold text-lg md:text-xl ${i === 0 ? 'bg-black dark:bg-white text-white dark:text-black editorial-shadow' : 'bg-gray-100 dark:bg-gray-800 text-black dark:text-white'}`}>
            {item.step}
          </div>
          <div className="flex flex-col gap-2 md:gap-3">
            <h5 className="text-base md:text-lg font-bold text-black dark:text-white font-headline">{item.title}</h5>
            <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{item.desc}</p>
          </div>
        </div>
      ))}
    </div>
  </section>
);

const ContactForm = () => {
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent'>('idle');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setStatus('sending');
    setTimeout(() => setStatus('sent'), 1500);
  };

  return (
    <section id="contact" className="py-12 md:py-24 px-4 max-w-7xl mx-auto">
      <div className="bg-gray-50 dark:bg-gray-900/50 rounded-[2rem] md:rounded-[3rem] p-6 md:p-16 flex flex-col lg:flex-row gap-12 md:gap-16">
        <div className="lg:w-1/2 flex flex-col gap-4 md:gap-6">
          <h2 className="text-3xl md:text-4xl font-bold text-black dark:text-white font-headline">Get in touch</h2>
          <p className="text-gray-600 dark:text-gray-400 text-base md:text-lg">
            Have questions about integrating EduSecure into your institution? Our team is here to help you build a more honest academic environment.
          </p>
          <div className="flex flex-col gap-3 md:gap-4 mt-2 md:mt-4">
            <div className="flex items-center gap-3 md:gap-4 text-gray-600 dark:text-gray-400">
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <Shield className="size-4 md:size-5" />
              </div>
              <span className="text-sm md:text-base">Enterprise-grade security</span>
            </div>
            <div className="flex items-center gap-3 md:gap-4 text-gray-600 dark:text-gray-400">
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <CheckCircle2 className="size-4 md:size-5" />
              </div>
              <span className="text-sm md:text-base">24/7 Technical support</span>
            </div>
          </div>
        </div>
        <div className="lg:w-1/2">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-xs md:text-sm font-bold text-black dark:text-white">Name</label>
                <input required type="text" placeholder="John Doe" className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2.5 md:py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white transition-all text-sm md:text-base text-black dark:text-white" />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs md:text-sm font-bold text-black dark:text-white">Email</label>
                <input required type="email" placeholder="john@university.edu" className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2.5 md:py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white transition-all text-sm md:text-base text-black dark:text-white" />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs md:text-sm font-bold text-black dark:text-white">Institution</label>
              <input required type="text" placeholder="Global University" className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2.5 md:py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white transition-all text-sm md:text-base text-black dark:text-white" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs md:text-sm font-bold text-black dark:text-white">Message</label>
              <textarea required rows={4} placeholder="How can we help you?" className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2.5 md:py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white transition-all text-sm md:text-base text-black dark:text-white resize-none" />
            </div>
            <button 
              disabled={status !== 'idle'}
              className="mt-2 flex items-center justify-center gap-2 bg-black dark:bg-white text-white dark:text-black font-bold py-3.5 md:py-4 rounded-xl hover:brightness-90 transition-all disabled:opacity-50 text-sm md:text-base"
            >
              {status === 'idle' && <><Send className="size-4" /> Send Message</>}
              {status === 'sending' && "Sending..."}
              {status === 'sent' && "Message Sent!"}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
};

const CTA = () => (
  <section className="mt-12 md:mt-24 pb-12 md:pb-20 px-4 max-w-7xl mx-auto">
    <div className="bg-black dark:bg-gray-900 text-white rounded-[2rem] md:rounded-[3rem] p-8 md:p-24 flex flex-col lg:flex-row items-center justify-between gap-8 md:gap-12 overflow-hidden relative border border-gray-800">
      <div className="flex flex-col gap-4 md:gap-6 z-10 text-center lg:text-left">
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight font-headline">Ready to secure your <br className="hidden md:block"/>academic future?</h2>
        <p className="text-white/60 text-sm md:text-lg max-w-md mx-auto lg:mx-0">Join over 500+ institutions worldwide using EduSecure to uphold the value of their degrees.</p>
      </div>
      <div className="flex flex-col sm:flex-row gap-4 z-10 w-full sm:w-auto">
        <button 
          onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
          className="w-full sm:w-auto bg-[#69ff87] text-[#002108] font-bold px-8 md:px-10 py-4 md:py-5 rounded-xl md:rounded-2xl text-base md:text-lg hover:scale-105 transition-transform"
        >
          Book a Demo
        </button>
        <button 
          onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
          className="w-full sm:w-auto bg-white/10 text-white font-bold px-8 md:px-10 py-4 md:py-5 rounded-xl md:rounded-2xl text-base md:text-lg border border-white/20 hover:bg-white/20 transition-colors"
        >
          View Solutions
        </button>
      </div>
      <div className="absolute -right-20 -bottom-20 w-64 h-64 md:w-96 md:h-96 bg-[#004ced] opacity-10 rounded-full blur-3xl"></div>
    </div>
  </section>
);

const Footer = () => (
  <footer className="max-w-7xl mx-auto px-4 pb-12">
    <div className="pt-8 border-t border-gray-200 dark:border-gray-800 flex flex-col md:flex-row justify-between items-center gap-6">
      <div className="flex items-center gap-3">
        <div className="size-10">
          <img src="/logo-light.png" className="dark:hidden w-full h-full object-contain" alt="" />
          <img src="/logo-dark.png" className="hidden dark:block w-full h-full object-contain" alt="" />
        </div>
        <span className="text-black dark:text-white font-bold font-headline">EduSecure</span>
      </div>
      <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-600 dark:text-gray-400 font-medium">
        <a className="hover:text-black dark:hover:text-white" href="#">Privacy Policy</a>
        <a className="hover:text-black dark:hover:text-white" href="#">Terms of Service</a>
        <a className="hover:text-black dark:hover:text-white" href="#">Documentation</a>
        <a className="hover:text-black dark:hover:text-white" href="#">Security</a>
      </div>
      <p className="text-sm text-gray-400">© 2024 EduSecure AI Systems Inc.</p>
    </div>
  </footer>
);

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => setIsDarkMode(!isDarkMode);

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-black transition-colors duration-300">
      <Navbar isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} />
      <main className="flex-grow">
        <Hero />
        <Features />
        <Demo />
        <Workflow />
        <ContactForm />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}
