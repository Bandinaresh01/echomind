import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Volume2, X, AlertCircle, Radio, Sparkles } from 'lucide-react';

export type VoiceState = 'IDLE' | 'CONNECTING' | 'LISTENING' | 'PROCESSING' | 'SPEAKING';

interface VoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSendMessage: (text: string) => Promise<string>;
}

export const VoiceModal: React.FC<VoiceModalProps> = ({ isOpen, onClose, onSendMessage }) => {
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [transcript, setTranscript] = useState('');
  const [aiSpeech, setAiSpeech] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [connectionMode, setConnectionMode] = useState<'LiveKit' | 'Browser WebSpeech'>('Browser WebSpeech');

  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const activeUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Initialize Speech APIs & LiveKit Token Check
  useEffect(() => {
    if (!isOpen) {
      cleanupAudio();
      return;
    }

    setErrorMessage(null);
    setVoiceState('CONNECTING');

    // 1. Check LiveKit Voice Token Endpoint from Flask Backend
    fetch('/api/voice/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room_name: 'echomind-main', participant_name: 'guest-user' }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success && data.token) {
          setConnectionMode('LiveKit');
          console.log('[EchoMind Voice] LiveKit token verified for room:', data.room);
        } else {
          setConnectionMode('Browser WebSpeech');
        }
      })
      .catch((err) => {
        console.warn('[EchoMind Voice] LiveKit server unreachable, using WebSpeech fallback:', err);
        setConnectionMode('Browser WebSpeech');
      })
      .finally(() => {
        setVoiceState('LISTENING');
        startSpeechRecognition();
      });

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }

    return () => {
      cleanupAudio();
    };
  }, [isOpen]);

  const cleanupAudio = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
    }
    if (synthRef.current) {
      synthRef.current.cancel();
    }
    setVoiceState('IDLE');
    setTranscript('');
    setAiSpeech('');
  };

  const startSpeechRecognition = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setErrorMessage('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      setVoiceState('IDLE');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setVoiceState('LISTENING');
      };

      recognition.onresult = (event: any) => {
        const current = event.resultIndex;
        const text = event.results[current][0].transcript;
        setTranscript(text);

        if (event.results[current].isFinal) {
          handleUserQuery(text);
        }
      };

      recognition.onerror = (event: any) => {
        if (event.error !== 'no-speech') {
          console.error('Speech recognition error:', event.error);
          setErrorMessage(`Speech error: ${event.error}`);
        }
        setVoiceState('IDLE');
      };

      recognition.onend = () => {
        // If not processing or speaking, keep listening
        setVoiceState((prev) => (prev === 'LISTENING' ? 'IDLE' : prev));
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e: any) {
      console.error('Failed to initialize speech recognition:', e);
      setErrorMessage(e.message || 'Microphone access failed.');
      setVoiceState('IDLE');
    }
  };

  const handleUserQuery = async (queryText: string) => {
    if (!queryText.trim()) return;

    setVoiceState('PROCESSING');
    try {
      const answer = await onSendMessage(queryText);
      const cleanAnswer = answer.replace(/[#*_~`\[\]()]/g, '').slice(0, 350);
      setAiSpeech(cleanAnswer);
      speakResponse(cleanAnswer);
    } catch (err: any) {
      setErrorMessage('Failed to receive response from EchoMind.');
      setVoiceState('IDLE');
    }
  };

  const speakResponse = (text: string) => {
    if (!synthRef.current || isMuted) {
      setVoiceState('LISTENING');
      startSpeechRecognition();
      return;
    }

    synthRef.current.cancel();
    setVoiceState('SPEAKING');

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1.05;

    utterance.onend = () => {
      setVoiceState('LISTENING');
      setTimeout(() => {
        startSpeechRecognition();
      }, 300);
    };

    utterance.onerror = () => {
      setVoiceState('LISTENING');
      startSpeechRecognition();
    };

    activeUtteranceRef.current = utterance;
    synthRef.current.speak(utterance);
  };

  const toggleMic = () => {
    if (voiceState === 'LISTENING') {
      if (recognitionRef.current) recognitionRef.current.stop();
      setVoiceState('IDLE');
    } else {
      setErrorMessage(null);
      startSpeechRecognition();
    }
  };

  if (!isOpen) return null;

  // Orb animation variants depending on VoiceState
  const getOrbColor = () => {
    switch (voiceState) {
      case 'CONNECTING':
        return 'from-amber-500 via-orange-500 to-yellow-400 shadow-amber-500/40';
      case 'LISTENING':
        return 'from-cyan-400 via-blue-500 to-indigo-600 shadow-cyan-500/50';
      case 'PROCESSING':
        return 'from-purple-500 via-fuchsia-600 to-pink-500 shadow-purple-500/50';
      case 'SPEAKING':
        return 'from-emerald-400 via-teal-500 to-cyan-600 shadow-emerald-500/50';
      case 'IDLE':
      default:
        return 'from-zinc-600 via-zinc-700 to-zinc-800 shadow-zinc-700/30';
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-xl">
        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.92 }}
          className="relative w-full max-w-xl bg-gradient-to-b from-[#121216] to-[#0a0a0c] border border-white/10 rounded-3xl p-8 shadow-[0_0_80px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col items-center text-center"
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-5 right-5 p-2 rounded-full bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Connection status tag */}
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-zinc-400 mb-6">
            <Radio className={`w-3 h-3 ${voiceState !== 'IDLE' ? 'text-emerald-400 animate-pulse' : 'text-zinc-500'}`} />
            <span>Mode: {connectionMode}</span>
            <span className="text-zinc-600">•</span>
            <span className="font-semibold text-zinc-300">{voiceState}</span>
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold tracking-tight text-white mb-1 flex items-center gap-2">
            EchoMind Voice
            <Sparkles className="w-5 h-5 text-indigo-400" />
          </h2>
          <p className="text-sm text-zinc-400 mb-8 max-w-sm">
            Speak naturally. EchoMind dynamically determines tools and answers with real-time speech.
          </p>

          {/* Animated Voice Orb */}
          <div className="relative w-44 h-44 flex items-center justify-center my-4">
            {/* Outer pulsating rings */}
            <motion.div
              animate={{
                scale: voiceState === 'LISTENING' ? [1, 1.35, 1] : voiceState === 'SPEAKING' ? [1, 1.25, 1] : 1,
                opacity: voiceState === 'LISTENING' || voiceState === 'SPEAKING' ? [0.4, 0.8, 0.4] : 0.2,
              }}
              transition={{ repeat: Infinity, duration: voiceState === 'LISTENING' ? 1.8 : 2.2, ease: 'easeInOut' }}
              className={`absolute inset-0 rounded-full bg-gradient-to-tr ${getOrbColor()} blur-2xl`}
            />

            {/* Middle Orb */}
            <motion.div
              animate={{
                rotate: voiceState === 'PROCESSING' ? 360 : 0,
                scale: voiceState === 'LISTENING' ? [1, 1.08, 1] : voiceState === 'SPEAKING' ? [1, 1.05, 1] : 1,
              }}
              transition={{
                rotate: { repeat: Infinity, duration: 3, ease: 'linear' },
                scale: { repeat: Infinity, duration: 1.5, ease: 'easeInOut' },
              }}
              className={`relative w-32 h-32 rounded-full bg-gradient-to-br ${getOrbColor()} shadow-2xl flex items-center justify-center border border-white/20`}
            >
              {voiceState === 'SPEAKING' ? (
                <Volume2 className="w-10 h-10 text-white" />
              ) : voiceState === 'LISTENING' ? (
                <Mic className="w-10 h-10 text-white animate-pulse" />
              ) : (
                <MicOff className="w-10 h-10 text-white/70" />
              )}
            </motion.div>
          </div>

          {/* Waveform Visualization */}
          <div className="flex items-end justify-center gap-1.5 h-10 my-4">
            {[40, 70, 95, 60, 85, 45, 90, 65, 80, 50, 75, 35].map((h, i) => (
              <motion.span
                key={i}
                animate={{
                  height:
                    voiceState === 'LISTENING' || voiceState === 'SPEAKING'
                      ? [`${Math.max(15, h * 0.3)}%`, `${h}%`, `${Math.max(15, h * 0.4)}%`]
                      : '20%',
                }}
                transition={{
                  repeat: Infinity,
                  duration: 0.8 + (i % 4) * 0.15,
                  ease: 'easeInOut',
                }}
                className={`w-1 rounded-full ${
                  voiceState === 'SPEAKING'
                    ? 'bg-emerald-400'
                    : voiceState === 'LISTENING'
                    ? 'bg-cyan-400'
                    : 'bg-zinc-700'
                }`}
              />
            ))}
          </div>

          {/* Live Transcript Display */}
          <div className="w-full bg-black/40 border border-white/5 rounded-2xl p-4 min-h-[70px] flex items-center justify-center text-sm my-2">
            {voiceState === 'LISTENING' && transcript && (
              <p className="text-cyan-300 font-medium italic">"{transcript}"</p>
            )}
            {voiceState === 'LISTENING' && !transcript && (
              <p className="text-zinc-500">Listening... Speak now</p>
            )}
            {voiceState === 'PROCESSING' && (
              <p className="text-purple-300 animate-pulse">EchoMind is reasoning & selecting tools...</p>
            )}
            {voiceState === 'SPEAKING' && (
              <p className="text-emerald-300 font-medium">{aiSpeech}</p>
            )}
            {voiceState === 'IDLE' && (
              <p className="text-zinc-500">Mic paused. Click microphone to start speaking.</p>
            )}
          </div>

          {/* Error notice */}
          {errorMessage && (
            <div className="flex items-center gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-2 rounded-xl mt-2 w-full">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Controls Bar */}
          <div className="flex items-center gap-4 mt-6">
            <button
              onClick={toggleMic}
              className={`h-12 px-6 rounded-full flex items-center gap-2 font-medium text-sm transition-all ${
                voiceState === 'LISTENING'
                  ? 'bg-red-500/20 border border-red-500/40 text-red-400 hover:bg-red-500/30'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20'
              }`}
            >
              {voiceState === 'LISTENING' ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              <span>{voiceState === 'LISTENING' ? 'Pause Listening' : 'Start Listening'}</span>
            </button>

            <button
              onClick={() => setIsMuted((prev) => !prev)}
              className={`h-12 w-12 rounded-full flex items-center justify-center border transition-colors ${
                isMuted
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : 'bg-white/5 border-white/10 text-zinc-400 hover:text-white'
              }`}
              title={isMuted ? 'Voice reply muted' : 'Voice reply active'}
            >
              <Volume2 className="w-4 h-4" />
            </button>

            <button
              onClick={onClose}
              className="h-12 px-5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-zinc-300 font-medium transition-colors"
            >
              Done
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
