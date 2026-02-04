import { useState, useEffect } from 'react';
import mascotImage from '../assets/jetset-mascot.png';

const LoadingIndicator: React.FC = () => {
  const [currentMessage, setCurrentMessage] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  const messages = [
    "Searching for the best flights...",
    "Comparing prices across airlines...",
    "Analyzing flight options...",
    "Finding the perfect deals for you...",
    "Almost there, finalizing results..."
  ];

  const travelTips = [
    "💡 Tip: Booking on Tuesdays can save you up to 15%",
    "✈️ Did you know? The cheapest time to fly is usually early morning",
    "🌍 Fun fact: The longest commercial flight is 19 hours",
    "💰 Pro tip: Clear your cookies before booking for better prices",
    "📅 Best time to book: 6-8 weeks before domestic flights"
  ];

  useEffect(() => {
    // Rotate through messages every 3 seconds
    const messageInterval = setInterval(() => {
      setCurrentMessage((prev) => (prev + 1) % messages.length);
    }, 3000);

    // Update elapsed time every second
    const timeInterval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(messageInterval);
      clearInterval(timeInterval);
    };
  }, []);

  const tipIndex = Math.floor(elapsedTime / 5) % travelTips.length;

  return (
    <div className="flex gap-3 mb-4 animate-fadeIn">
      <div className="flex-shrink-0">
        <img 
          src={mascotImage} 
          alt="JetSet AI" 
          className="w-10 h-10 rounded-full object-cover border-2 border-purple-200 animate-pulse-slow"
        />
      </div>
      <div className="chat-bubble chat-bubble-assistant max-w-md">
        <div className="space-y-3">
          {/* Status Message */}
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-sm font-medium text-gray-700 animate-pulse">
              {messages[currentMessage]}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-purple-500 to-blue-500 h-1.5 rounded-full transition-all duration-1000 ease-out"
              style={{ 
                width: `${Math.min((elapsedTime / 60) * 100, 95)}%` 
              }}
            ></div>
          </div>

          {/* Time Estimate */}
          <div className="text-xs text-gray-500">
            {elapsedTime < 30 ? (
              <span>⏱️ Usually takes 30-60 seconds...</span>
            ) : elapsedTime < 60 ? (
              <span>⏱️ Almost done, just a few more seconds...</span>
            ) : (
              <span>⏱️ Taking a bit longer than usual, thanks for your patience...</span>
            )}
          </div>

          {/* Travel Tip (shows after 5 seconds) */}
          {elapsedTime >= 5 && (
            <div className="text-xs text-purple-600 bg-purple-50 rounded-lg p-2 animate-fadeIn">
              {travelTips[tipIndex]}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;