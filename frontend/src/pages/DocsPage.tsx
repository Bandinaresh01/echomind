import { Database, Cpu, Wrench, Users, ArrowDown, CloudRain, Newspaper, LineChart, GraduationCap, Network, Layers, Zap } from 'lucide-react';
import { motion, type Variants } from 'framer-motion';

export default function DocsPage() {
  const containerVars: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.15 }
    }
  };

  const itemVars: Variants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  return (
    <motion.div
      key="docs"
      initial="hidden"
      animate="show"
      exit={{ opacity: 0, y: -10 }}
      variants={containerVars}
      className="w-full h-full flex flex-col"
    >
      <div className="flex-1 min-h-0 w-full overflow-y-auto custom-scrollbar relative">
        {/* Decorative background vectors */}
        <div className="absolute top-0 right-0 -mr-32 -mt-32 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-1/4 left-0 -ml-32 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[100px] pointer-events-none" />

        <div className="flex flex-col gap-16 py-12 px-2 md:px-8 relative z-10 w-full max-w-6xl mx-auto">
          
          {/* Header Section */}
          <motion.div variants={itemVars} className="space-y-6 text-center md:text-left max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-bold tracking-widest border border-indigo-500/20">
              <Layers className="w-3.5 h-3.5" />
              SYSTEM ARCHITECTURE
            </div>
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight">
              Technical <br className="md:hidden" />
              <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">Documentation</span>
            </h1>
            <p className="text-zinc-400 text-lg leading-relaxed">
              A deep dive into how EchoMind processes queries, leverages Large Language Models, and invokes real-world deterministic tools entirely within milliseconds.
            </p>
          </motion.div>

          {/* Expanded Knowledge Grid */}
          <motion.div variants={itemVars} className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="bg-zinc-900/80 backdrop-blur-xl border border-white/5 hover:border-indigo-500/30 transition-colors duration-300 p-8 rounded-3xl relative h-full flex flex-col shadow-2xl">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-indigo-500/20 flex items-center justify-center mb-6">
                  <Database className="w-6 h-6 text-indigo-300" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-3 tracking-tight">Stateful Context Memory</h3>
                <p className="text-zinc-400 leading-relaxed">
                  By intercepting the payload across the <code className="text-indigo-300 bg-indigo-500/10 px-1.5 py-0.5 rounded">/api/chat</code> route, the React frontend isolates and constructs a rolling context window of the last 3 message turns.
                  This ensures the LangChain agent running locally maintains absolute conversational permanence, allowing accurate follow-up logic.
                </p>
              </div>
            </div>

            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="bg-zinc-900/80 backdrop-blur-xl border border-white/5 hover:border-purple-500/30 transition-colors duration-300 p-8 rounded-3xl relative h-full flex flex-col shadow-2xl">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-purple-500/20 flex items-center justify-center mb-6">
                  <Wrench className="w-6 h-6 text-purple-300" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-3 tracking-tight">Deterministic Parsing</h3>
                <p className="text-zinc-400 leading-relaxed">
                  LLMs frequently hallucinate JSON objects when attempting to invoke specific code execution modules. EchoMind relies on an explicit Python validation
                  <code className="text-purple-300 bg-purple-500/10 px-1.5 py-0.5 rounded mx-1">for _ in range(3)</code> execution loop, automatically catching, parsing, and feeding any exceptions back to the model for instantaneous auto-correction.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Visual Diagram Layering */}
          <motion.div variants={itemVars} className="w-full relative mt-8">
            <div className="text-center mb-10">
               <h2 className="text-2xl font-bold text-white tracking-tight flex items-center justify-center gap-3">
                 <Network className="w-6 h-6 text-indigo-400" />
                 Execution Pipeline
               </h2>
            </div>
            
            <div className="w-full bg-[#050505] border border-white/5 rounded-[2.5rem] p-8 md:p-14 relative flex flex-col items-center gap-10 shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden">
              
              {/* Background Grid Pattern inside Diagram */}
              <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />

              {/* Connecting vertical laser line */}
              <div className="absolute top-0 bottom-0 left-1/2 w-px bg-gradient-to-b from-indigo-500/0 via-indigo-500/50 to-indigo-500/0 -translate-x-1/2 z-0 hidden md:block" />

              {/* Box 1: User / UI */}
              <motion.div 
                whileHover={{ y: -5 }}
                className="w-80 bg-zinc-900/90 backdrop-blur-xl border border-white/10 rounded-2xl p-6 flex flex-col items-center text-center shadow-xl relative z-10"
              >
                <div className="w-12 h-12 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-blue-400" />
                </div>
                <h4 className="font-bold text-white text-lg tracking-tight">Frontend Client</h4>
                <p className="text-sm text-zinc-500 mt-2 leading-relaxed opacity-80">React & Vite edge application. Safely encrypts keys and manages real-time Jotai state projection.</p>
              </motion.div>

              <motion.div animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 2 }}>
                <ArrowDown className="w-6 h-6 text-indigo-500/70" />
              </motion.div>

              {/* Box 3: LangChain core */}
              <div className="w-full max-w-4xl bg-black border border-indigo-500/40 rounded-3xl p-8 md:p-10 shadow-[0_0_80px_rgba(99,102,241,0.15)] relative z-10 flex flex-col items-center group">
                {/* Core indicator */}
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-[10px] font-bold tracking-widest uppercase px-4 py-1.5 rounded-full flex items-center gap-2 backdrop-blur-md">
                   <Zap className="w-3 h-3 text-indigo-400 fill-indigo-400" />
                   Core Inference Engine
                </div>

                <Cpu className="w-12 h-12 text-indigo-400 mb-5 relative z-10 group-hover:scale-110 transition-transform duration-500 mt-2" />
                <h4 className="text-2xl font-bold text-white tracking-tight">LangChain Recursive Agent</h4>
                <p className="text-[15px] text-zinc-400 text-center mt-3 max-w-xl mb-10 leading-relaxed">
                  The LLM dynamically reasons through the context payload to determine if it possesses native world knowledge, or if it must autonomously delegate to local Python sub-routines.
                </p>

                {/* Tools Grid inside Agent */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
                  <div className="bg-zinc-900 border border-white/5 rounded-2xl p-5 text-center flex flex-col items-center hover:bg-zinc-800 hover:border-blue-500/30 transition-all duration-300 cursor-default group/tool hover:-translate-y-1">
                    <CloudRain className="w-7 h-7 text-blue-400 mb-3 group-hover/tool:scale-110 transition-transform" />
                    <span className="text-sm font-semibold text-white tracking-tight">Weather</span>
                    <span className="text-[11px] font-medium tracking-wide text-zinc-500 mt-1 uppercase">Open-Meteo</span>
                  </div>
                  <div className="bg-zinc-900 border border-white/5 rounded-2xl p-5 text-center flex flex-col items-center hover:bg-zinc-800 hover:border-yellow-500/30 transition-all duration-300 cursor-default group/tool hover:-translate-y-1">
                    <Newspaper className="w-7 h-7 text-yellow-400 mb-3 group-hover/tool:scale-110 transition-transform" />
                    <span className="text-sm font-semibold text-white tracking-tight">Live News</span>
                    <span className="text-[11px] font-medium tracking-wide text-zinc-500 mt-1 uppercase">DuckDuckGo</span>
                  </div>
                  <div className="bg-zinc-900 border border-white/5 rounded-2xl p-5 text-center flex flex-col items-center hover:bg-zinc-800 hover:border-emerald-500/30 transition-all duration-300 cursor-default group/tool hover:-translate-y-1">
                    <LineChart className="w-7 h-7 text-emerald-400 mb-3 group-hover/tool:scale-110 transition-transform" />
                    <span className="text-sm font-semibold text-white tracking-tight">Stock Data</span>
                    <span className="text-[11px] font-medium tracking-wide text-zinc-500 mt-1 uppercase">YFinance</span>
                  </div>
                  <div className="bg-zinc-900 border border-white/5 rounded-2xl p-5 text-center flex flex-col items-center hover:bg-zinc-800 hover:border-purple-500/30 transition-all duration-300 cursor-default group/tool hover:-translate-y-1">
                    <GraduationCap className="w-7 h-7 text-purple-400 mb-3 group-hover/tool:scale-110 transition-transform" />
                    <span className="text-sm font-semibold text-white tracking-tight">ArXiv Logic</span>
                    <span className="text-[11px] font-medium tracking-wide text-zinc-500 mt-1 uppercase">Research API</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
