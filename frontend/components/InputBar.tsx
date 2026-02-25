import React, { useState } from 'react';

interface InputBarProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const InputBar: React.FC<InputBarProps> = ({
  onSendMessage,
  isLoading,
}) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 bg-white bg-opacity-80 border-t border-promtior-200"
    >
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about Promtior..."
          disabled={isLoading}
          className="flex-1 px-4 py-3 rounded-lg border border-promtior-300 focus:outline-none focus:ring-2 focus:ring-promtior-600 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-6 py-3 bg-promtior-600 text-white rounded-lg hover:bg-promtior-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {isLoading ? (
            <span className="inline-block animate-spin">⏳</span>
          ) : (
            'Send'
          )}
        </button>
      </div>
    </form>
  );
};
