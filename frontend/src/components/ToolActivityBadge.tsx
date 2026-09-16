import React from 'react';
import { CloudRain, Globe, Newspaper, Clock, Wrench, CheckCircle2, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export interface ToolActivityProps {
  toolName: string;
  status: 'running' | 'completed';
  outputPreview?: string;
}

const TOOL_CONFIG: Record<string, { label: string; icon: any; color: string; desc: string }> = {
  weather_tool: {
    label: 'Weather Tool',
    icon: CloudRain,
    color: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    desc: 'Fetching live meteorological data...',
  },
  search_tool: {
    label: 'Web Search',
    icon: Globe,
    color: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    desc: 'Searching the web for latest facts & sources...',
  },
  news_tool: {
    label: 'News Tool',
    icon: Newspaper,
    color: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    desc: 'Fetching latest news articles & headlines...',
  },
  time_tool: {
    label: 'System Clock',
    icon: Clock,
    color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    desc: 'Retrieving synchronized system timestamp...',
  },
};

export const ToolActivityBadge: React.FC<ToolActivityProps> = ({ toolName, status, outputPreview }) => {
  const config = TOOL_CONFIG[toolName] || {
    label: toolName.replace('_', ' ').toUpperCase(),
    icon: Wrench,
    color: 'text-zinc-400 bg-zinc-800/50 border-white/10',
    desc: 'Executing tool operation...',
  };

  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex flex-col gap-1.5 px-3 py-2 rounded-xl border text-xs font-medium my-1.5 ${config.color} backdrop-blur-md max-w-lg`}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Icon className="w-3.5 h-3.5 shrink-0" />
          <span className="font-semibold">{config.label}</span>
          <span className="text-[11px] opacity-70">
            {status === 'running' ? config.desc : 'Completed'}
          </span>
        </div>
        <div>
          {status === 'running' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin opacity-80" />
          ) : (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          )}
        </div>
      </div>

      {status === 'completed' && outputPreview && (
        <p className="text-[11px] text-zinc-400 bg-black/30 rounded px-2 py-1 font-mono line-clamp-2">
          {outputPreview}
        </p>
      )}
    </motion.div>
  );
};
