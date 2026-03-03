import React, { useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ content: string; metadata?: Record<string, string> }>;
  timestamp: Date;
}

interface ChatBoxProps {
  messages: Message[];
  isLoading: boolean;
}

export const ChatBox: React.FC<ChatBoxProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white bg-opacity-50">
      {messages.length === 0 && !isLoading && (
        <div className="flex h-full items-center justify-center text-center">
          <div>
            <h2 className="text-2xl font-bold text-promtior-900 mb-2">
              Welcome to Promtior Chatbot
            </h2>
            <p className="text-promtior-600">
              Ask me about Promtior's services and company information.
            </p>
            <p className="text-sm text-promtior-500 mt-4">
              Example questions:
              <br />
              • What services does Promtior offer?
              <br />
              • When was Promtior founded?
            </p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          <div
            className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
              message.role === 'user'
                ? 'bg-promtior-600 text-white rounded-br-none'
                : 'bg-gray-200 text-gray-900 rounded-bl-none'
            }`}
          >
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            {message.sources && message.sources.length > 0 && (
              <div className="mt-2 pt-2 border-t border-opacity-20 border-gray-900">
                <p className="text-xs font-semibold opacity-70 mb-1">
                  Sources:
                </p>
                <ul className="text-xs opacity-70 space-y-1">
                  {message.sources.slice(0, 2).map((source, idx) => (
                    <li key={idx} className="truncate">
                      {source.metadata?.source || `Source ${idx + 1}`}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <p className="text-xs opacity-50 mt-1">
              {message.timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-200 text-gray-900 px-4 py-3 rounded-lg rounded-bl-none">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-gray-900 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-900 rounded-full animate-bounce delay-100"></div>
              <div className="w-2 h-2 bg-gray-900 rounded-full animate-bounce delay-200"></div>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};
