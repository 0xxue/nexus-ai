import { useRef, useEffect } from 'react';
import { useChatStore, Message } from '../../store/chat';
import { streamQuestion } from '../../api/qa';
import ChatMessage from '../../components/ChatMessage';
import ChatInput from '../../components/ChatInput';
import { MessageSquare, Plus } from 'lucide-react';

export default function ChatPage() {
  const { messages, streaming, conversationId, addMessage, updateLastMessage, setStreaming, clearMessages } = useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (query: string) => {
    // Add user message
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
    };
    addMessage(userMsg);

    // Add loading assistant message
    const assistantMsg: Message = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      loading: true,
      steps: [],
    };
    addMessage(assistantMsg);
    setStreaming(true);

    try {
      const response = await streamQuestion(query, conversationId || undefined);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      let fullContent = '';
      let sources: any[] = [];
      let chart: any = null;
      let confidence = 0;
      let steps: string[] = [];

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value);
          const lines = text.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.done) continue;

                if (data.node) {
                  steps.push(data.node);
                  const nodeData = data.data || {};

                  if (nodeData.answer) fullContent = nodeData.answer;
                  if (nodeData.sources) sources = nodeData.sources;
                  if (nodeData.chart) chart = nodeData.chart;
                  if (nodeData.confidence) confidence = nodeData.confidence;

                  updateLastMessage({
                    content: fullContent || `正在处理: ${data.node}...`,
                    sources,
                    chart,
                    confidence,
                    steps,
                    loading: !fullContent,
                  });
                }
              } catch {}
            }
          }
        }
      }

      // Final update
      updateLastMessage({
        content: fullContent || '抱歉，无法生成回答。',
        sources,
        chart,
        confidence,
        steps,
        loading: false,
      });

    } catch (err) {
      updateLastMessage({
        content: '请求失败，请检查网络或 API 配置。',
        loading: false,
      });
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="border-b px-6 py-3 flex items-center justify-between bg-white">
        <div className="flex items-center gap-2">
          <MessageSquare size={20} className="text-blue-600" />
          <h1 className="text-lg font-semibold">AI 智能问答</h1>
        </div>
        <button
          onClick={clearMessages}
          className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Plus size={16} />
          新对话
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <MessageSquare size={48} className="mb-4" />
            <h2 className="text-xl font-medium mb-2">AI 智能问答系统</h2>
            <p className="text-sm">试试问：系统整体情况怎么样？资金还能撑多久？</p>
            <div className="mt-6 grid grid-cols-2 gap-3 max-w-md">
              {[
                '系统整体数据情况',
                '最近有多少产品到期',
                '资金还能撑多久',
                '用户增长趋势如何',
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  className="px-4 py-2 text-sm text-left border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={streaming} />
    </div>
  );
}
