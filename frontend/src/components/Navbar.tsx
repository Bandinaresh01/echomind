import { useNavigate, useLocation } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { googleLogout } from '@react-oauth/google';
import { useAtom } from 'jotai';
import { userAtom, googleCredentialsAtom } from '@/store';

type Tab = 'chat' | 'docs' | 'team';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useAtom(userAtom);
  const [, setGoogleCredentials] = useAtom(googleCredentialsAtom);

  const getActiveTab = (): Tab | null => {
    if (location.pathname === '/docs') return 'docs';
    if (location.pathname === '/team') return 'team';
    if (location.pathname === '/chat') return 'chat';
    return null;
  };
  const activeTab = getActiveTab();

  const handleLogout = () => {
    googleLogout();
    setUser(null);
    setGoogleCredentials(null);
    navigate('/'); 
  };

  const handleNavigation = (tab: Tab) => {
    navigate(`/${tab}`);
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0a0a0a]/60 backdrop-blur-xl shrink-0">
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        <div 
          className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
          onClick={() => { navigate('/'); }}
        >
          <img src="/avatar.png" alt="EchoMind Avatar" className="w-8 h-8 object-cover rounded shadow-sm" />
          <span className="text-lg font-bold tracking-tight text-white">
            EchoMind
          </span>
        </div>
        
        <div className="hidden md:flex flex-1 justify-center items-center gap-8">
          {(['chat', 'docs', 'team'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => handleNavigation(tab)}
              className={`text-sm font-semibold transition-all duration-300 capitalize tracking-wide ${
                activeTab === tab 
                  ? 'text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.4)]' 
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex flex-col items-end justify-center">
            <span className="text-sm font-semibold text-zinc-200 tracking-tight leading-none mb-1">{user?.name || 'Guest User'}</span>
            <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-medium leading-none">{user?.email ? 'Authenticated' : 'Local Session'}</span>
          </div>
          {user?.picture ? (
            <img src={user.picture} alt="Profile" className="w-9 h-9 rounded-full border border-white/10 shadow-lg" />
          ) : (
            <div className="w-9 h-9 rounded-full bg-zinc-800 border border-white/10 flex items-center justify-center shadow-inner">
              <span className="text-xs text-zinc-400 font-bold">GU</span>
            </div>
          )}
          <button 
            onClick={handleLogout}
            className="p-2 ml-1 rounded-lg bg-zinc-900 md:bg-transparent hover:bg-white/10 text-zinc-400 hover:text-white transition-all duration-200 cursor-pointer shadow-sm border border-white/5 md:border-transparent md:hover:border-white/10 flex items-center gap-2"
            title="End Session"
          >
            <LogOut className="w-4 h-4" />
            <span className="sr-only">Logout</span>
          </button>
        </div>
      </div>
      
      {/* Mobile Tab Control */}
      <div className="flex md:hidden w-full border-t border-white/5 p-2 bg-black/40 justify-around">
         {(['chat', 'docs', 'team'] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => handleNavigation(tab)}
            className={`text-[11px] font-bold tracking-wider py-2 w-full text-center capitalize ${activeTab === tab ? 'text-white shadow-sm bg-white/5 rounded-md' : 'text-zinc-500'}`}
          >
            {tab}
          </button>
        ))}
      </div>
    </nav>
  );
}
