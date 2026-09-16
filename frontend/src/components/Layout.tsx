import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

export default function Layout() {
  return (
    <div className="h-[100dvh] bg-[#0a0a0a] text-zinc-50 font-sans selection:bg-white/20 flex flex-col relative overflow-hidden">
      {/* Background Ambient Glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 blur-[140px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[140px] rounded-full pointer-events-none" />
      
      <Navbar />

      {/* Main Content Area */}
      <main className="flex-1 min-h-0 container mx-auto p-4 md:px-8 md:py-6 flex flex-col items-center justify-center">
        <Outlet />
      </main>
    </div>
  );
}
