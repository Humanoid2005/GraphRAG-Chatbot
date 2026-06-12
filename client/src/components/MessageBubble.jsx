import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  
  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <span className="text-[10px] uppercase tracking-widest font-bold text-text-muted bg-surface-elevated px-4 py-1.5 rounded-full border border-border-subtle shadow-sm">
          {message.content}
        </span>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[85%] rounded-[2rem] px-6 py-5 ${
          isUser 
            ? 'bg-text-primary text-surface-elevated rounded-br-md shadow-md' 
            : 'glass-panel glass-inner rounded-bl-md text-text-primary'
        } ${message.isLoading ? 'animate-pulse opacity-70' : ''}`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap leading-relaxed font-medium">{message.content}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-headings:tracking-tight prose-a:text-accent hover:prose-a:text-accent/80 prose-strong:font-semibold">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
