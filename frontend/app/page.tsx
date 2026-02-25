'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { ChatBox } from '@/components/ChatBox';
import { InputBar } from '@/components/InputBar';
import { sendMessage, checkHealth } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ content: string; metadata?: Record<string, string> }>;
  timestamp: Date;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiHealthy, setApiHealthy] = useState(false);

  useEffect(() => {
    const checkApiHealth = async () => {
      const healthy = await checkHealth();
      setApiHealthy(healthy);
    };

    checkApiHealth();
    const interval = setInterval(checkApiHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (message: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(message);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response || response.error || 'No response received',
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, an error occurred. Please try again.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Header apiHealthy={apiHealthy} />
      <ChatBox messages={messages} isLoading={isLoading} />
      <InputBar onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}
