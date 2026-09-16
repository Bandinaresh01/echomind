import { Card, CardTitle, CardDescription } from '@/components/ui/card';
import { motion } from 'framer-motion';

export default function TeamPage() {
  return (
    <motion.div 
      key="team"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-6xl flex-1 min-h-0 flex flex-col mx-auto"
    >
      <div className="flex-1 min-h-0 w-full pr-4 overflow-y-auto custom-scrollbar">
        <div className="flex flex-col items-center text-center gap-12 py-12">
          <div className="space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white">Project Authors</h1>
            <p className="text-zinc-400 text-lg">The core engineers constructing the intelligence behind EchoMind.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full px-4">
            {[
              { name: 'Rajcharan', role: 'Full Stack Engineer', desc: 'Expert in React, Vite frameworks, component systems, and UI execution.', image: '/rajcharan.jpg', linkedin: 'https://www.linkedin.com/in/raj-charan-vanga-05b249255' },
              { name: 'Bandi Naresh', role: 'AI & Systems Architect', desc: 'Specialist in Vector DB integrations, LangChain orchestration and core Python API logic.', image: '/naresh.jpg', linkedin: 'https://www.linkedin.com/in/bandi-naresh' },
              { name: 'Talah Hanuman', role: 'Lead Developer', desc: 'Overseeing global platform vision, highly-scalable backend structures, and Vercel routing.', image: '/talah.jpg', linkedin: 'https://www.linkedin.com/in/talaha-numan-4bb92a28b' }
            ].map((member, i) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="group relative h-full flex flex-col"
              >
                <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-3xl blur-xl" />
                <Card className="bg-zinc-900/80 backdrop-blur-xl border-white/5 h-full flex flex-col p-8 hover:border-indigo-500/30 transition-all duration-300 relative z-10 rounded-3xl group-hover:-translate-y-2 shadow-2xl">
                  <div className="w-20 h-20 rounded-full bg-zinc-900 border-2 border-white/10 mb-6 flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/20 overflow-hidden relative">
                    {/* Avatar Image Placeholder */}
                    <img src={member.image} alt={member.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 relative z-10" 
                        onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.nextElementSibling?.classList.remove('hidden'); }} />
                    <span className="hidden absolute inset-0 flex items-center justify-center text-xl font-bold text-white tracking-widest bg-gradient-to-br from-indigo-500 to-blue-600">{member.name.charAt(0)}</span>
                  </div>
                  <CardTitle className="text-xl font-bold text-white mb-2">{member.name}</CardTitle>
                  <CardDescription className="text-indigo-400 text-[13px] font-bold tracking-widest uppercase mb-6">{member.role}</CardDescription>
                  <p className="text-sm text-zinc-400 mt-auto leading-relaxed">{member.desc}</p>
                  
                  <div className="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mt-8 mb-4" />
                  <div className="flex justify-center gap-4">
                    <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="text-[11px] font-bold tracking-widest uppercase text-zinc-500 hover:text-indigo-400 transition-colors">LinkedIn</a>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
