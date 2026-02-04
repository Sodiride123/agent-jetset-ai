interface Flight {
  id: string;
  airline: string;
  flightNumber?: string;
  price: number;
  currency: string;
  departure: {
    time: string;
    date: string;
    airport: string;
    city: string;
  };
  arrival: {
    time: string;
    date: string;
    airport: string;
    city: string;
  };
  duration: string;
  stops: number;
  layovers?: string[];
  class?: string;
  tags?: string[];
}

interface FlightCardProps {
  flight: Flight;
}

const FlightCard: React.FC<FlightCardProps> = ({ flight }) => {
  const isCheapest = flight.tags?.includes('cheapest');
  const isFastest = flight.tags?.includes('fastest');
  const isDirect = flight.stops === 0;

  return (
    <div className="flight-card bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden">
      {/* Best value badge */}
      {isCheapest && (
        <div className="absolute top-3 right-3 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold">
          💰 Cheapest
        </div>
      )}
      {isFastest && (
        <div className="absolute top-3 right-3 bg-purple-500 text-white px-3 py-1 rounded-full text-xs font-bold">
          ⚡ Fastest
        </div>
      )}

      {/* Header with Airline */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center text-2xl">
            ✈️
          </div>
          <div>
            <h3 className="font-bold text-lg text-gray-800">{flight.airline}</h3>
            {flight.flightNumber && (
              <span className="text-sm text-gray-500">{flight.flightNumber}</span>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            ${flight.price}
          </div>
          <div className="text-xs text-gray-500">per person</div>
        </div>
      </div>

      {/* Flight Timeline */}
      <div className="flex items-center justify-between mb-6">
        {/* Departure */}
        <div className="text-center flex-shrink-0">
          <div className="text-2xl font-bold text-gray-800">{flight.departure.time}</div>
          <div className="text-sm font-semibold text-gray-600">{flight.departure.airport}</div>
          <div className="text-xs text-gray-500">{flight.departure.city}</div>
        </div>
        
        {/* Flight Path */}
        <div className="flex-1 mx-6 relative">
          <div className="relative h-16 flex items-center">
            {/* Line */}
            <div className="absolute w-full h-0.5 bg-gradient-to-r from-purple-300 to-blue-300"></div>
            
            {/* Duration badge */}
            <div className="absolute left-1/2 transform -translate-x-1/2 -top-2">
              <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-full px-4 py-1.5 text-xs font-semibold text-purple-700 whitespace-nowrap shadow-sm">
                ✈️ {flight.duration}
              </div>
            </div>
            
            {/* Stops indicator */}
            {flight.stops > 0 && (
              <div className="absolute left-1/2 transform -translate-x-1/2 top-6">
                <div className="text-xs text-orange-600 font-medium whitespace-nowrap">
                  {flight.stops} stop{flight.stops > 1 ? 's' : ''}
                  {flight.layovers && flight.layovers.length > 0 && (
                    <span className="text-gray-500"> via {flight.layovers.join(', ')}</span>
                  )}
                </div>
              </div>
            )}
            
            {/* Plane icon */}
            <div className="absolute left-1/2 transform -translate-x-1/2 text-purple-500 text-xl">
              ✈
            </div>
          </div>
        </div>
        
        {/* Arrival */}
        <div className="text-center flex-shrink-0">
          <div className="text-2xl font-bold text-gray-800">{flight.arrival.time}</div>
          <div className="text-sm font-semibold text-gray-600">{flight.arrival.airport}</div>
          <div className="text-xs text-gray-500">{flight.arrival.city}</div>
        </div>
      </div>

      {/* Additional Info Badges */}
      <div className="flex gap-2 flex-wrap">
        {flight.class && (
          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
            {flight.class}
          </span>
        )}
        {isDirect && (
          <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
            ✈️ Direct
          </span>
        )}
        {flight.stops === 1 && (
          <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-medium">
            1 Stop
          </span>
        )}
        {flight.stops > 1 && (
          <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-medium">
            {flight.stops} Stops
          </span>
        )}
      </div>
    </div>
  );
};

export default FlightCard;