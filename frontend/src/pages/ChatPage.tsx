import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Mic,
  Volume2,
  VolumeX,
  Copy,
  Check,
  Sparkles,
  CloudRain,
  Globe,
  Newspaper,
  Compass,
  ArrowRight,
  Wrench,
  Layers,
  Cpu,
  X,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion } from 'framer-motion';

import { Sidebar, type ChatSession } from '@/components/Sidebar';
import { VoiceModal } from '@/components/VoiceModal';
import { ToolActivityBadge } from '@/components/ToolActivityBadge';
import { useSpeechSynthesis } from '@/lib/useSpeechSynthesis';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tools_used?: string[];
  active_tools?: { name: string; status: 'running' | 'completed'; preview?: string }[];
}

export const SUGGESTED_PROMPTS = [
  {
    title: 'What is RAG?',
    subtitle: 'Learn about Retrieval-Augmented Generation',
    icon: Compass,
    query: 'Explain what RAG is and how it works in generative AI systems.',
  },
  {
    title: "What's the weather in Hyderabad?",
    subtitle: 'Live meteorological forecast via Weather MCP',
    icon: CloudRain,
    query: "What's the current weather in Hyderabad?",
  },
  {
    title: "Give me today's AI news",
    subtitle: 'Latest artificial intelligence headlines via News MCP',
    icon: Newspaper,
    query: "What are today's top AI news headlines?",
  },
  {
    title: 'Search the latest LangGraph updates',
    subtitle: 'Deep web search via DuckDuckGo MCP',
    icon: Globe,
    query: 'Search for the latest features and updates in LangGraph 2026.',
  },
];

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false);
  const [isToolsDialogOpen, setIsToolsDialogOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { isVoiceEnabled, toggleVoice, speak, isSpeaking, cancel } = useSpeechSynthesis();

  // Load chat sessions from localStorage
  useEffect(() => {
    try {
      const savedSessions = localStorage.getItem('echomind_sessions');
      if (savedSessions) {
        const parsed = JSON.parse(savedSessions);
        setSessions(parsed);
        if (parsed.length > 0) {
          loadSession(parsed[0].id);
        }
      }
    } catch (e) {
      console.error('Failed to load sessions from storage:', e);
    }
  }, []);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages, isLoading]);

  const loadSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    try {
      const savedMessages = localStorage.getItem(`echomind_chat_${sessionId}`);
      if (savedMessages) {
        setMessages(JSON.parse(savedMessages));
      } else {
        setMessages([]);
      }
    } catch (e) {
      setMessages([]);
    }
  };

  const handleNewChat = () => {
    const newId = `chat_${Date.now()}`;
    const newSession: ChatSession = {
      id: newId,
      title: 'New Conversation',
      timestamp: Date.now(),
    };
    const updated = [newSession, ...sessions];
    setSessions(updated);
    setCurrentSessionId(newId);
    setMessages([]);
    localStorage.setItem('echomind_sessions', JSON.stringify(updated));
    localStorage.setItem(`echomind_chat_${newId}`, JSON.stringify([]));
  };

  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = sessions.filter((s) => s.id !== sessionId);
    setSessions(updated);
    localStorage.setItem('echomind_sessions', JSON.stringify(updated));
    localStorage.removeItem(`echomind_chat_${sessionId}`);

    if (currentSessionId === sessionId) {
      if (updated.length > 0) {
        loadSession(updated[0].id);
      } else {
        setCurrentSessionId(null);
        setMessages([]);
      }
    }
  };

  const saveCurrentMessages = (msgs: Message[]) => {
    let sId = currentSessionId;
    let currentList = [...sessions];

    if (!sId) {
      sId = `chat_${Date.now()}`;
      setCurrentSessionId(sId);
      const firstUserMsg = msgs.find((m) => m.role === 'user');
      const title = firstUserMsg ? firstUserMsg.content.slice(0, 32) : 'Conversation';
      const newSession = { id: sId, title, timestamp: Date.now() };
      currentList = [newSession, ...sessions];
      setSessions(currentList);
      localStorage.setItem('echomind_sessions', JSON.stringify(currentList));
    } else {
      // Update title if it was "New Conversation"
      const sessionIndex = currentList.findIndex((s) => s.id === sId);
      if (sessionIndex !== -1 && currentList[sessionIndex].title === 'New Conversation') {
        const firstUserMsg = msgs.find((m) => m.role === 'user');
        if (firstUserMsg) {
          currentList[sessionIndex].title = firstUserMsg.content.slice(0, 32);
          setSessions(currentList);
          localStorage.setItem('echomind_sessions', JSON.stringify(currentList));
        }
      }
    }

    localStorage.setItem(`echomind_chat_${sId}`, JSON.stringify(msgs));
  };

  const handleSubmit = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const queryToSend = (customQuery || input).trim();
    if (!queryToSend || isLoading) return;

    if (isSpeaking) cancel();

    const userMessage: Message = {
      id: `usr_${Date.now()}`,
      role: 'user',
      content: queryToSend,
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    const assistantId = `ast_${Date.now()}`;
    const initialAssistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      tools_used: [],
      active_tools: [],
    };

    setMessages((prev) => [...prev, initialAssistantMessage]);

    // Build history to send (last 6 turns for context)
    const historyToSend = messages.slice(-6).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      // Use relative endpoint /api/chat so Vite proxy forwards to http://localhost:5000
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage.content,
          history: historyToSend,
          stream: true,
        }),
      });

      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      if (!response.body) throw new Error('No response stream returned');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let done = false;
      let buffer = '';
      let accumulatedText = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim();
              if (!dataStr) continue;

              try {
                const parsed = JSON.parse(dataStr);

                if (parsed.type === 'token') {
                  accumulatedText += parsed.content;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantId ? { ...msg, content: accumulatedText } : msg
                    )
                  );
                } else if (parsed.type === 'tool_start') {
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantId
                        ? {
                            ...msg,
                            active_tools: [
                              ...(msg.active_tools || []),
                              { name: parsed.name, status: 'running' },
                            ],
                            tools_used: Array.from(
                              new Set([...(msg.tools_used || []), parsed.name])
                            ),
                          }
                        : msg
                    )
                  );
                } else if (parsed.type === 'tool_end') {
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantId
                        ? {
                            ...msg,
                            active_tools: (msg.active_tools || []).map((t) =>
                              t.name === parsed.name
                                ? { ...t, status: 'completed', preview: parsed.output_preview }
                                : t
                            ),
                          }
                        : msg
                    )
                  );
                } else if (parsed.type === 'error') {
                  accumulatedText += `\n\n> ⚠ **Error**: ${parsed.content}`;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantId ? { ...msg, content: accumulatedText } : msg
                    )
                  );
                }
              } catch (e) {
                console.error('SSE JSON parse error:', dataStr, e);
              }
            }
          }
        }
      }

      // Final save and voice reply
      setMessages((prev) => {
        saveCurrentMessages(prev);
        if (isVoiceEnabled && accumulatedText) {
          const plain = accumulatedText.replace(/[#*_~`\[\]()]/g, '');
          speak(plain);
        }
        return prev;
      });
    } catch (err: any) {
      console.error('Chat error:', err);
      const errorContent = `EchoMind couldn't complete this request. (${err.message}). Please verify the backend is running on port 5000.`;
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId ? { ...msg, content: errorContent } : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceQuery = async (queryText: string): Promise<string> => {
    return new Promise(async (resolve, reject) => {
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: queryText, stream: false }),
        });
        const data = await response.json();
        if (data.success && data.response) {
          const assistantMsg: Message = {
            id: `ast_${Date.now()}`,
            role: 'assistant',
            content: data.response,
            tools_used: data.tools_used || [],
          };
          setMessages((prev) => {
            const updated = [...prev, { id: `usr_${Date.now()}`, role: 'user' as const, content: queryText }, assistantMsg];
            saveCurrentMessages(updated);
            return updated;
          });
          resolve(data.response);
        } else {
          reject(new Error(data.error || 'Failed response'));
        }
      } catch (e) {
        reject(e);
      }
    });
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMessageId(id);
    setTimeout(() => setCopiedMessageId(null), 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#08080a] text-zinc-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed((prev) => !prev)}
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={loadSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onOpenVoice={() => setIsVoiceModalOpen(true)}
        onOpenTools={() => setIsToolsDialogOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Chat Workspace */}
      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        {/* Top Navbar */}
        <header className="h-14 border-b border-white/5 bg-[#0a0a0d]/80 backdrop-blur-md px-6 flex items-center justify-between shrink-0 z-20">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-semibold text-zinc-300">EchoMind 3.0</span>
            </div>
            <span className="text-zinc-600">|</span>
            <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[11px] font-medium text-indigo-300">
              <Cpu className="w-3 h-3" />
              <span>Groq Llama 3.3 / OSS 120B</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleVoice}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                isVoiceEnabled
                  ? 'bg-blue-500/10 border-blue-500/30 text-blue-400'
                  : 'bg-white/5 border-white/10 text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {isVoiceEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
              <span>Voice Reply {isVoiceEnabled ? 'ON' : 'OFF'}</span>
            </button>

            <button
              onClick={() => setIsVoiceModalOpen(true)}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-md shadow-indigo-600/20 transition-all"
            >
              <Mic className="w-3.5 h-3.5" />
              <span>Talk Live</span>
            </button>
          </div>
        </header>

        {/* Scrollable Messages Container */}
        <div
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto px-4 md:px-8 py-6 custom-scrollbar relative flex flex-col"
        >
          {messages.length === 0 ? (
            /* Empty / Landing State (Section 16) */
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="my-auto max-w-2xl mx-auto w-full flex flex-col items-center text-center py-10"
            >
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-2xl shadow-indigo-500/30 mb-6">
                <div className="w-full h-full bg-[#0d0d12] rounded-2xl flex items-center justify-center">
                  <Sparkles className="w-7 h-7 text-indigo-400" />
                </div>
              </div>

              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-3">
                EchoMind
              </h1>
              <p className="text-zinc-400 text-base md:text-lg max-w-lg mb-8 leading-relaxed">
                Your intelligent AI companion. Ask questions. Search the web. Check weather. Get latest news. Or talk naturally using your voice.
              </p>

              <div className="flex items-center gap-3 mb-10">
                <button
                  onClick={() => setIsVoiceModalOpen(true)}
                  className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm shadow-lg shadow-indigo-600/25 flex items-center gap-2 transition-all"
                >
                  <Mic className="w-4 h-4" />
                  <span>Start Voice Session</span>
                </button>
                <button
                  onClick={() => {
                    inputRef.current?.focus();
                  }}
                  className="h-11 px-6 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-zinc-300 font-medium text-sm transition-all"
                >
                  Start a Conversation
                </button>
              </div>

              {/* Clickable Suggested Prompt Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full text-left">
                {SUGGESTED_PROMPTS.map((prompt, idx) => {
                  const Icon = prompt.icon;
                  return (
                    <motion.div
                      key={idx}
                      whileHover={{ y: -2 }}
                      onClick={() => handleSubmit(undefined, prompt.query)}
                      className="p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.07] border border-white/5 hover:border-white/10 cursor-pointer transition-all flex items-start gap-3.5 group"
                    >
                      <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0 mt-0.5">
                        <Icon className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">
                          {prompt.title}
                        </h4>
                        <p className="text-xs text-zinc-500 line-clamp-1 mt-0.5">
                          {prompt.subtitle}
                        </p>
                      </div>
                      <ArrowRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-300 self-center opacity-0 group-hover:opacity-100 transition-opacity" />
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          ) : (
            /* Chat Stream List */
            <div className="max-w-3xl mx-auto w-full space-y-6 pb-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex items-start gap-4 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 mt-1 shadow-md shadow-indigo-500/20">
                      <Sparkles className="w-4 h-4 text-white" />
                    </div>
                  )}

                  <div
                    className={`flex flex-col gap-1.5 max-w-[85%] md:max-w-[78%] ${
                      message.role === 'user' ? 'items-end' : 'items-start'
                    }`}
                  >
                    {/* Active Tool Execution Badges (Section 19) */}
                    {message.role === 'assistant' &&
                      message.active_tools &&
                      message.active_tools.length > 0 && (
                        <div className="w-full flex flex-col gap-1 mb-2">
                          {message.active_tools.map((tool, tIdx) => (
                            <ToolActivityBadge
                              key={tIdx}
                              toolName={tool.name}
                              status={tool.status}
                              outputPreview={tool.preview}
                            />
                          ))}
                        </div>
                      )}

                    {/* Message Bubble */}
                    <div
                      className={`px-5 py-4 rounded-2xl text-[14.5px] leading-relaxed shadow-sm ${
                        message.role === 'user'
                          ? 'bg-indigo-600 text-white rounded-br-sm'
                          : 'bg-[#121217] text-zinc-200 border border-white/5 rounded-bl-sm prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-black/60 prose-pre:border prose-pre:border-white/10'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <p className="whitespace-pre-wrap break-words font-medium">
                          {message.content}
                        </p>
                      ) : (
                        <div>
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content || '...'}
                          </ReactMarkdown>
                        </div>
                      )}
                    </div>

                    {/* Message Action Footer (Copy, Speak) */}
                    {message.role === 'assistant' && message.content && (
                      <div className="flex items-center gap-2 px-1 mt-0.5 text-zinc-500 text-xs">
                        <button
                          onClick={() => copyToClipboard(message.content, message.id)}
                          className="flex items-center gap-1 hover:text-zinc-300 transition-colors p-1 rounded"
                          title="Copy response"
                        >
                          {copiedMessageId === message.id ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                          <span className="text-[11px]">Copy</span>
                        </button>

                        <button
                          onClick={() => {
                            const plain = message.content.replace(/[#*_~`\[\]()]/g, '');
                            speak(plain);
                          }}
                          className="flex items-center gap-1 hover:text-zinc-300 transition-colors p-1 rounded"
                          title="Speak aloud"
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                          <span className="text-[11px]">Speak</span>
                        </button>
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-zinc-800 border border-white/10 flex items-center justify-center shrink-0 mt-1">
                      <span className="text-xs font-semibold text-zinc-300">You</span>
                    </div>
                  )}
                </motion.div>
              ))}

              {isLoading && (
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 mt-1 animate-pulse">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  <div className="px-5 py-3.5 rounded-2xl bg-[#121217] border border-white/5 rounded-bl-sm flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Floating Chat Input (Section 20) */}
        <div className="p-4 bg-gradient-to-t from-[#08080a] via-[#08080a]/90 to-transparent shrink-0">
          <div className="max-w-3xl mx-auto w-full relative">
            <form
              onSubmit={handleSubmit}
              className="relative flex items-end gap-2 bg-[#121217] border border-white/10 rounded-2xl px-4 py-2.5 shadow-2xl focus-within:border-indigo-500/50 transition-colors"
            >
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask EchoMind anything... (e.g. Hyderabad weather, AI news)"
                rows={1}
                className="flex-1 bg-transparent text-sm text-white placeholder:text-zinc-500 resize-none outline-none max-h-32 py-1.5 custom-scrollbar"
                disabled={isLoading}
              />

              <div className="flex items-center gap-1.5 shrink-0 pb-0.5">
                <button
                  type="button"
                  onClick={() => setIsVoiceModalOpen(true)}
                  className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                  title="Voice Mode"
                >
                  <Mic className="w-4 h-4" />
                </button>

                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="h-9 w-9 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white flex items-center justify-center transition-all shadow-md shadow-indigo-600/20"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </form>

            <p className="text-center text-[11px] text-zinc-600 mt-2">
              EchoMind agentically executes tools (Weather, Search, News) based on your intent.
            </p>
          </div>
        </div>
      </div>

      {/* Voice Assistant Modal */}
      <VoiceModal
        isOpen={isVoiceModalOpen}
        onClose={() => setIsVoiceModalOpen(false)}
        onSendMessage={handleVoiceQuery}
      />

      {/* Tools Ecosystem Dialog */}
      {isToolsDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-[#121217] border border-white/10 rounded-3xl p-6 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Wrench className="w-5 h-5 text-indigo-400" />
                Tools Ecosystem (MCP)
              </h3>
              <button
                onClick={() => setIsToolsDialogOpen(false)}
                className="p-1 rounded-lg text-zinc-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="font-semibold text-blue-400">Weather Tool (OpenWeatherMap)</span>
                <p className="text-zinc-400 mt-0.5">Fetches current temperature, weather conditions, wind speed, and humidity.</p>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="font-semibold text-amber-400">Search Tool (DuckDuckGo)</span>
                <p className="text-zinc-400 mt-0.5">Live real-time search engine for current facts, updates, and research.</p>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="font-semibold text-purple-400">News Tool (NewsAPI.org)</span>
                <p className="text-zinc-400 mt-0.5">Latest curated news headlines with dates and sources.</p>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="font-semibold text-emerald-400">System Time Clock</span>
                <p className="text-zinc-400 mt-0.5">Synchronized current date, time, and day of the week.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Settings Dialog */}
      {isSettingsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-[#121217] border border-white/10 rounded-3xl p-6 max-w-md w-full shadow-2xl text-xs">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-400" />
                System Settings
              </h3>
              <button
                onClick={() => setIsSettingsOpen(false)}
                className="p-1 rounded-lg text-zinc-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-2.5 text-zinc-300">
              <div className="flex justify-between py-2 border-b border-white/5">
                <span className="text-zinc-500">Groq Model</span>
                <span className="font-mono text-indigo-300">openai/gpt-oss-120b</span>
              </div>
              <div className="flex justify-between py-2 border-b border-white/5">
                <span className="text-zinc-500">Agent Framework</span>
                <span className="font-mono text-indigo-300">LangGraph StateGraph</span>
              </div>
              <div className="flex justify-between py-2 border-b border-white/5">
                <span className="text-zinc-500">Tool Protocol</span>
                <span className="font-mono text-indigo-300">Model Context Protocol (MCP)</span>
              </div>
              <div className="flex justify-between py-2 border-b border-white/5">
                <span className="text-zinc-500">LiveKit WebRTC</span>
                <span className="font-mono text-emerald-400">ws://localhost:7880 (Active)</span>
              </div>
              <div className="flex justify-between py-2 border-b border-white/5">
                <span className="text-zinc-500">REST Backend</span>
                <span className="font-mono text-zinc-300">Flask (port 5000)</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
