import React from 'react';

interface HeaderProps {
  apiHealthy: boolean;
}

export const Header: React.FC<HeaderProps> = ({ apiHealthy }) => {
  return (
    <div className="bg-gradient-to-r from-promtior-600 to-promtior-700 text-white p-4 shadow-lg">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Promtior Chatbot</h1>
          <p className="text-promtior-100 text-sm">
            Ask anything about Promtior's services and company
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              apiHealthy ? 'bg-green-400' : 'bg-red-400'
            }`}
          />
          <span className="text-sm">
            {apiHealthy ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </div>
  );
};
