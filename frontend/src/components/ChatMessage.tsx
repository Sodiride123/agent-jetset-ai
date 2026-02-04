import type { Message } from '../types';
import mascotImage from '../assets/jetset-mascot.png';
import FlightResults from './FlightResults';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  // Extract text without JSON blocks for display
  const getDisplayText = (content: string) => {
    // Remove JSON code blocks from display
    return content.replace(/```json\s*\{.*?\}\s*```/gs, '').trim();
  };

  return (
    <div className={`flex gap-3 mb-4 animate-fadeIn ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold">
            You
          </div>
        ) : (
          <img 
            src={mascotImage} 
            alt="JetSet AI" 
            className="w-10 h-10 rounded-full object-cover border-2 border-purple-200"
          />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
        {/* Text Message Bubble */}
        <div className={`chat-bubble ${isUser ? 'chat-bubble-user' : 'chat-bubble-assistant'}`}>
          <div className="text-sm whitespace-pre-wrap">{getDisplayText(message.content)}</div>
          <div className={`text-xs mt-2 ${isUser ? 'text-purple-100' : 'text-gray-400'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>

        {/* Flight Results Cards (if available) */}
        {!isUser && message.flightData && (
          <div className="mt-4">
            <FlightResults flightData={message.flightData} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;