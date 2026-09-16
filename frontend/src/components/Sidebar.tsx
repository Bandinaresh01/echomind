import React from 'react';
import {
  MessageSquarePlus,
  MessageSquare,
  Mic,
  Settings,
  ChevronLeft,
  ChevronRight,
  Trash2,
  Wrench,
  Sparkles,
} from 'lucide-react';

export interface ChatSession {
  id: string;
  title: string;
  timestamp: number;
}

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  onOpenVoice: () => void;
  onOpenTools: () => void;
  onOpenSettings: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggleCollapse,
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onOpenVoice,
  onOpenTools,
  onOpenSettings,
}) => {
  // Categorize sessions into Today, Yesterday, and Previous 7 Days
  const now = Date.now();
  const ONE_DAY = 24 * 60 * 60 * 1000;

  const todaySessions = sessions.filter((s) => now - s.timestamp < ONE_DAY);
  const yesterdaySessions = sessions.filter(
    (s) => now - s.timestamp >= ONE_DAY && now - s.timestamp < 2 * ONE_DAY
  );
  const previous7DaysSessions = sessions.filter(
    (s) => now - s.timestamp >= 2 * ONE_DAY && now - s.timestamp < 7 * ONE_DAY
  );
  const olderSessions = sessions.filter((s) => now - s.timestamp >= 7 * ONE_DAY);

  const renderSessionGroup = (title: string, list: ChatSession[]) => {
    if (list.length === 0) return null;
    return (
      <div className="mb-4">
        <h4 className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider px-3 mb-1.5">
          {title}
        </h4>
        <div className="space-y-1">
          {list.map((s) => (
            <div
              key={s.id}
              onClick={() => onSelectSession(s.id)}
              className={`group flex items-center justify-between px-3 py-2 rounded-xl text-xs cursor-pointer transition-all ${
                s.id === currentSessionId
                  ? 'bg-white/10 text-white font-medium border border-white/10'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/5'
              }`}
            >
              <div className="flex items-center gap-2.5 min-w-0 flex-1">
                <MessageSquare className="w-3.5 h-3.5 shrink-0 text-zinc-500 group-hover:text-zinc-300" />
                <span className="truncate">{s.title}</span>
              </div>
              <button
                onClick={(e) => onDeleteSession(s.id, e)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity"
                title="Delete chat"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <aside
      className={`relative flex flex-col bg-[#0d0d11] border-r border-white/5 transition-all duration-300 z-30 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Header & Logo */}
      <div className="flex items-center justify-between p-4 border-b border-white/5">
        {!isCollapsed ? (
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-md shadow-indigo-500/20">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-sm tracking-tight text-white">EchoMind</h1>
              <p className="text-[10px] text-zinc-500 tracking-wider uppercase font-semibold">
                Voice + Text Agent
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/20 transition-all ${
            isCollapsed ? 'px-0' : 'px-4'
          }`}
          title="New Chat"
        >
          <MessageSquarePlus className="w-4 h-4 shrink-0" />
          {!isCollapsed && <span>New Chat</span>}
        </button>
      </div>

      {/* Recent Chats Section */}
      {!isCollapsed ? (
        <div className="flex-1 overflow-y-auto px-2 py-2 custom-scrollbar">
          {sessions.length === 0 ? (
            <div className="text-center py-8 px-4 text-zinc-600 text-xs">
              <p>No recent conversations yet.</p>
              <p className="mt-1 text-[11px] opacity-75">Start chatting or use voice!</p>
            </div>
          ) : (
            <>
              {renderSessionGroup('Today', todaySessions)}
              {renderSessionGroup('Yesterday', yesterdaySessions)}
              {renderSessionGroup('Previous 7 Days', previous7DaysSessions)}
              {renderSessionGroup('Older', olderSessions)}
            </>
          )}
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center gap-2 py-4">
          {sessions.slice(0, 5).map((s) => (
            <button
              key={s.id}
              onClick={() => onSelectSession(s.id)}
              className={`w-9 h-9 rounded-xl flex items-center justify-center text-xs transition-colors ${
                s.id === currentSessionId
                  ? 'bg-white/10 text-white border border-white/10'
                  : 'text-zinc-400 hover:bg-white/5'
              }`}
              title={s.title}
            >
              <MessageSquare className="w-4 h-4" />
            </button>
          ))}
        </div>
      )}

      {/* Bottom Controls */}
      <div className="p-3 border-t border-white/5 flex flex-col gap-1">
        <button
          onClick={onOpenVoice}
          className={`w-full flex items-center gap-3 p-2.5 rounded-xl text-xs font-medium transition-colors ${
            isCollapsed ? 'justify-center' : ''
          } bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 border border-cyan-500/20`}
          title="Voice Assistant"
        >
          <Mic className="w-4 h-4 shrink-0" />
          {!isCollapsed && <span>Voice Assistant</span>}
        </button>

        <button
          onClick={onOpenTools}
          className={`w-full flex items-center gap-3 p-2.5 rounded-xl text-xs font-medium text-zinc-400 hover:text-white hover:bg-white/5 transition-colors ${
            isCollapsed ? 'justify-center' : ''
          }`}
          title="Tools Ecosystem"
        >
          <Wrench className="w-4 h-4 shrink-0" />
          {!isCollapsed && <span>Tools Ecosystem</span>}
        </button>

        <button
          onClick={onOpenSettings}
          className={`w-full flex items-center gap-3 p-2.5 rounded-xl text-xs font-medium text-zinc-400 hover:text-white hover:bg-white/5 transition-colors ${
            isCollapsed ? 'justify-center' : ''
          }`}
          title="System Settings"
        >
          <Settings className="w-4 h-4 shrink-0" />
          {!isCollapsed && <span>Settings</span>}
        </button>
      </div>
    </aside>
  );
};
