import { motion, type Variants } from 'framer-motion';
import { ScanLine, BrainCircuit, LineChart, GraduationCap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useGoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { useSetAtom } from 'jotai';
import { userAtom, googleCredentialsAtom, type UserProfile, type GoogleCredentials } from '@/store';

export default function LandingPage() {
  const navigate = useNavigate();
  const setUser = useSetAtom(userAtom);
  const setGoogleCredentials = useSetAtom(googleCredentialsAtom);
  // Animation Variants
  const containerVars: Variants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.15, delayChildren: 0.2 } }
  };

  const itemVars: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  const loginToGoogle = useGoogleLogin({
    flow: 'auth-code',
    scope: 'openid email profile https://www.googleapis.com/auth/gmail.modify',
    onSuccess: async (codeResponse) => {
      try {
        const res = await fetch('https://my-backend1-6q8j.onrender.com/api/auth/google', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: codeResponse.code })
        });

        if (!res.ok) throw new Error('Auth exchange failed. Missing Client Secret?');
        const credentials: GoogleCredentials = await res.json();

        // Fetch User Identity securely from Google via the new Access Token
        const profileRes = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
          headers: { Authorization: `Bearer ${credentials.access_token}` }
        });
        const profile = await profileRes.json();

        const userData: UserProfile = {
          name: profile.name,
          email: profile.email,
          picture: profile.picture
        };

        setUser(userData);
        setGoogleCredentials(credentials);
        navigate('/chat');
      } catch (err: any) {
        console.error('Google Auth Failed', err);
        alert('Google Authentication Failed! Ensure your backend .env file has the GOOGLE_CLIENT_SECRET, and check the server logs. Falling back to Guest mode.');
        navigate('/chat');
      }
    },
    onError: () => {
      console.error('Google Login Dialog Failed');
      navigate('/chat');
    }
  });

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-50 font-sans flex flex-col relative overflow-hidden selection:bg-zinc-800">

      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-zinc-800/20 rounded-full blur-[120px] pointer-events-none" />

      {/* Modern minimal navbar */}
      <nav className="w-full px-8 py-6 flex items-center justify-between z-10 relative">
        <div className="flex items-center gap-3">
          <img src="/avatar.png" alt="EchoMind" className="w-8 h-8 rounded shadow-sm opacity-90" />
          <span className="text-xl font-bold tracking-tighter text-white">EchoMind</span>
        </div>
        <div className="hidden md:flex gap-6 text-sm font-medium text-zinc-400">
          <span className="hover:text-white transition-colors cursor-pointer">Architecture</span>
          <span className="hover:text-white transition-colors cursor-pointer">Integrations</span>
          <span className="hover:text-white transition-colors cursor-pointer">Security</span>
        </div>
        <Button
          onClick={() => navigate('/chat')}
          variant="outline"
          className="bg-black/50 border-white/10 text-white hover:bg-white hover:text-black transition-all rounded-full px-6 h-10 text-sm"
        >
          Guest Access
        </Button>
      </nav>

      <main className="flex-1 flex flex-col items-center justify-center px-4 z-10 relative pb-20">
        <motion.div
          variants={containerVars}
          initial="hidden"
          animate="visible"
          className="max-w-5xl mx-auto w-full flex flex-col items-center mt-12 md:mt-24"
        >

          <motion.div variants={itemVars} className="flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 bg-white/5 mb-8 backdrop-blur-sm">
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs font-medium text-zinc-300 tracking-wide uppercase">EchoMind V3.0 is Live</span>
          </motion.div>

          <motion.h1 variants={itemVars} className="text-5xl md:text-8xl font-bold tracking-tighter text-center leading-[1.1] mb-6">
            The Agentic <br className="hidden md:block" />
            <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-600">
              Intelligence Platform.
            </span>
          </motion.h1>

          <motion.p variants={itemVars} className="text-lg md:text-xl text-zinc-400 text-center max-w-2xl mb-12 leading-relaxed">
            Unleash the power of Llama 3 equipped with deep internet scraping, real-time market tracking, and autonomous multi-tool execution capabilities.
          </motion.p>

          <motion.div variants={itemVars} className="flex flex-col sm:flex-row items-center gap-4">
            <button
              onClick={() => loginToGoogle()}
              className="h-[44px] px-8 rounded-full bg-white text-black hover:bg-zinc-200 transition-all font-semibold shadow-lg shadow-white/10 flex items-center justify-center gap-3 text-[15px]"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" /><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" /><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" /><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" /></svg>
              <span>Connect Google Workspace</span>
            </button>
            <Button
              onClick={() => navigate('/chat')}
              variant="outline"
              className="h-[44px] px-8 rounded-full bg-transparent border-white/10 text-white hover:bg-white/5 transition-all font-medium text-[15px]"
            >
              Guest Access
            </Button>
          </motion.div>

          {/* Feature Grid */}
          <motion.div variants={containerVars} className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-24 max-w-5xl">
            {[
              { title: "Autonomous Web Scraper", icon: ScanLine, desc: "Bypasses search limits by physically fetching and reading the raw HTML of massive websites to answer your queries." },
              { title: "Live Market Oracle", icon: LineChart, desc: "Securely wired into global stock and cryptocurrency tickers. Instantly evaluates asset volatility and day performance." },
              { title: "ArXiv Research Extraction", icon: GraduationCap, desc: "Capable of locating, indexing, and summarizing highly technical quantum physics and medical academic papers." }
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                variants={itemVars}
                className="bg-zinc-900/40 border border-white/5 rounded-2xl p-6 hover:bg-zinc-900/60 transition-colors backdrop-blur-md"
              >
                <div className="w-12 h-12 rounded-full bg-black border border-white/10 flex items-center justify-center mb-5 shadow-inner">
                  <feature.icon className="w-5 h-5 text-zinc-300" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2 tracking-tight">{feature.title}</h3>
                <p className="text-sm text-zinc-500 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Deep Dive Architecture Section */}
          <motion.div variants={containerVars} className="w-full max-w-5xl mt-32 mb-10 flex flex-col md:flex-row gap-16 items-center">
            <motion.div variants={itemVars} className="flex-1 space-y-6 text-left w-full">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 text-indigo-400 text-[11px] font-bold tracking-widest border border-indigo-500/20">
                <BrainCircuit className="w-3.5 h-3.5" />
                SYSTEM ARCHITECTURE
              </div>
              <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white leading-[1.15]">
                Not just generating text. <br /><span className="text-zinc-600">Executing actions.</span>
              </h2>
              <p className="text-zinc-400 leading-relaxed text-lg">
                EchoMind acts as a terminal wrapper around Llama 3.1. Instead of hallucinating answers, it constructs a JSON-based execution plan, halting its generation to invoke live APIs and scrape text, verifying facts instantly.
              </p>
              <ul className="space-y-4 pt-4">
                {[
                  "Self-Correcting Execution Loops",
                  "Short-Term Memory Context Injection",
                  "Fault-Tolerant Type Parsing"
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-4 text-sm text-zinc-300 font-medium">
                    <div className="w-6 h-6 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shadow-sm">
                      <ScanLine className="w-3 h-3 text-zinc-400" />
                    </div>
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
            <motion.div variants={itemVars} className="flex-1 w-full bg-[#050505] shadow-2xl backdrop-blur-xl border border-white/10 rounded-2xl p-6 relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-transparent to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
              <div className="flex items-center gap-2 absolute top-4 right-4">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500/80"></span>
                <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></span>
                <span className="w-2.5 h-2.5 rounded-full bg-green-500/80"></span>
              </div>
              <pre className="text-[13px] text-zinc-400 font-mono leading-relaxed overflow-x-auto pt-6">
                <code>
                  {`{
  "thought": "I need live weather data.",
  "action": "weather_tool",
  "action_input": {
    "location": "Tokyo, Japan"
  }
}

>> OBSERVATION: 
{ "temp": 18, "condition": "Rain" }

>> SYNTHESIS:
"It is currently 18°C and raining in Tokyo."`}
                </code>
              </pre>
            </motion.div>
          </motion.div>

        </motion.div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-white/5 py-8 mt-auto relative z-10 flex flex-col items-center justify-center">
        <div className="flex items-center gap-2 opacity-30 mix-blend-screen">
          <BrainCircuit className="w-5 h-5 text-white" />
        </div>
        <p className="text-xs text-zinc-600 mt-4 font-medium uppercase tracking-widest">Designed for Power Users.</p>
      </footer>
    </div>
  );
}
