import mascotImage from '../assets/jetset-mascot.png';

interface SidebarProps {
  onNewChat: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onNewChat }) => {
  return (
    <div className="w-80 bg-white/80 backdrop-blur-sm shadow-xl rounded-3xl p-6 flex flex-col">
      {/* Logo and Mascot */}
      <div className="text-center mb-8">
        <img 
          src={mascotImage} 
          alt="JetSet AI" 
          className="w-32 h-32 mx-auto mb-4 object-contain"
        />
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
          JetSet AI
        </h1>
        <p className="text-gray-600 text-sm mt-2">
          Your AI-Powered Travel Assistant ✈️
        </p>
      </div>

      {/* New Chat Button */}
      <button
        onClick={onNewChat}
        className="btn-primary w-full mb-6"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-5 w-5 inline mr-2" 
          viewBox="0 0 20 20" 
          fill="currentColor"
        >
          <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
        </svg>
        New Chat
      </button>

      {/* Features */}
      <div className="flex-1 space-y-4">
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          What I Can Do
        </h3>
        
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-xl">
            <span className="text-2xl">🔍</span>
            <div>
              <h4 className="font-semibold text-sm text-gray-800">Smart Search</h4>
              <p className="text-xs text-gray-600">Natural language flight queries</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-xl">
            <span className="text-2xl">💰</span>
            <div>
              <h4 className="font-semibold text-sm text-gray-800">Best Prices</h4>
              <p className="text-xs text-gray-600">Real-time flight comparisons</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-pink-50 rounded-xl">
            <span className="text-2xl">🎯</span>
            <div>
              <h4 className="font-semibold text-sm text-gray-800">Personalized</h4>
              <p className="text-xs text-gray-600">Tailored recommendations</p>
            </div>
          </div>
        </div>
      </div>

      {/* Example Queries */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
          Try Asking
        </h3>
        <div className="space-y-2 text-xs text-gray-600">
          <p className="bg-gray-50 p-2 rounded-lg">
            "Find flights from NYC to London next Friday"
          </p>
          <p className="bg-gray-50 p-2 rounded-lg">
            "Show me weekend trips to Paris under $500"
          </p>
          <p className="bg-gray-50 p-2 rounded-lg">
            "Direct flights to Tokyo in March"
          </p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;