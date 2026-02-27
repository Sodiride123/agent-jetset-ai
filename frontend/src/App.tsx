import { useState, useRef, useEffect } from 'react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import LoadingIndicator from './components/LoadingIndicator';
import Sidebar from './components/Sidebar';
import type { Message, ChatResponse } from './types';
import './index.css';

const API_URL = '';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId] = useState('default');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: "Hi there! ✈️ I'm JetSet, your AI travel assistant! I'm here to help you find the perfect flights for your next adventure.\n\nJust tell me where you want to go, when you'd like to travel, and any preferences you have. I'll search through thousands of flights to find the best options for you!\n\nHow can I help you today?",
        timestamp: new Date(),
      },
    ]);
  }, []);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data: ChatResponse = await response.json();

      // Add assistant message with flight data if available
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        flightData: data.flight_data,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment! 😊",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      await fetch(`${API_URL}/api/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: conversationId,
        }),
      });

      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: "Hi there! ✈️ I'm JetSet, your AI travel assistant! Ready to help you find amazing flights. Where would you like to go?",
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error('Error resetting chat:', error);
    }
  };

  return (
    <div className="min-h-screen p-3 md:p-6 flex gap-3 md:gap-6">
      {/* Mobile sidebar overlay backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - hidden on mobile, shown as overlay when toggled */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-80 p-3 transition-transform duration-300 md:relative md:translate-x-0 md:p-0 md:z-auto
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <Sidebar onNewChat={() => { handleNewChat(); setSidebarOpen(false); }} />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 min-w-0 flex flex-col bg-white/60 backdrop-blur-sm rounded-3xl shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 md:p-6">
          <div className="flex items-center gap-3">
            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-1 rounded-lg hover:bg-white/20 transition-colors"
              aria-label="Open menu"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <h2 className="text-xl md:text-2xl font-bold">Chat with JetSet</h2>
              <p className="text-purple-100 text-xs md:text-sm mt-1">
                Ask me anything about flights in natural language!
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3 md:p-6 space-y-4">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isLoading && <LoadingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-3 md:p-6 bg-white/80 backdrop-blur-sm border-t border-gray-200">
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}

export default App;