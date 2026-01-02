interface CodeLine {
  content: string;
  violation?: {
    type: 'critical' | 'high' | 'medium';
    message: string;
  };
}

interface CodeBlockProps {
  lines: CodeLine[];
  filename?: string;
}

export const CodeBlock = ({ lines, filename = 'analytics.py' }: CodeBlockProps) => {
  return (
    <div className="bg-[#1e1e1e] rounded-xl overflow-hidden font-mono text-sm shadow-2xl">
      {/* Window Controls */}
      <div className="flex items-center gap-2 px-4 py-3 bg-[#2d2d2d] border-b border-white/10">
        <div className="w-3 h-3 rounded-full bg-red-500/80" />
        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
        <div className="w-3 h-3 rounded-full bg-green-500/80" />
        <span className="ml-2 text-white/50 text-xs">{filename}</span>
      </div>

      {/* Code Content */}
      <div className="p-6 overflow-x-auto">
        {lines.map((line, i) => (
          <div key={i} className="flex items-start gap-4 leading-relaxed min-h-[24px] group">
            {/* Line Number */}
            <span className="text-white/30 select-none w-8 text-right flex-shrink-0 pt-0.5">
              {i + 1}
            </span>

            {/* Code Content */}
            <div className="flex-1 flex items-start gap-3">
              <code
                className={`text-white/90 ${
                  line.violation ? 'border-b-2 border-red-500 border-dotted' : ''
                }`}
              >
                {line.content}
              </code>

              {/* Violation Badge */}
              {line.violation && (
                <span
                  className={`text-xs px-2 py-0.5 rounded flex-shrink-0 ${
                    line.violation.type === 'critical'
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : line.violation.type === 'high'
                      ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                      : 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                  }`}
                >
                  {line.violation.type === 'critical' ? '🚨' : '⚠️'} {line.violation.message}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
