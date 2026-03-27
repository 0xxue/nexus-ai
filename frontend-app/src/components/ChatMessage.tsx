import ReactMarkdown from 'react-markdown';
import { Message } from '../store/chat';
import ChartRenderer from './ChartRenderer';
import { Bot, User, FileText, Loader2 } from 'lucide-react';

interface Props {
  message: Message;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 py-4 px-4 ${isUser ? 'bg-transparent' : 'bg-gray-50'}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
        isUser ? 'bg-blue-600' : 'bg-gray-800'
      }`}>
        {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
      </div>

      <div className="flex-1 min-w-0">
        {message.loading ? (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 size={16} className="animate-spin" />
            <span>思考中...</span>
            {message.steps && message.steps.length > 0 && (
              <span className="text-xs text-gray-400">
                ({message.steps[message.steps.length - 1]})
              </span>
            )}
          </div>
        ) : (
          <>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>

            {message.chart && <ChartRenderer config={message.chart} />}

            {message.sources && message.sources.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {message.sources.map((src, i) => (
                  <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">
                    <FileText size={10} />
                    {src.name}
                  </span>
                ))}
              </div>
            )}

            {message.confidence !== undefined && message.confidence > 0 && (
              <div className="mt-2 text-xs text-gray-400">
                置信度: {(message.confidence * 100).toFixed(0)}%
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
