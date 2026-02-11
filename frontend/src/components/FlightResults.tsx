import FlightCard from './FlightCard';

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
  token?: string;
}

interface FlightData {
  flights: Flight[];
  summary?: {
    totalResults: number;
    cheapestPrice: number;
    fastestDuration: string;
    averagePrice: number;
  };
}

interface FlightResultsProps {
  flightData: FlightData;
}

const FlightResults: React.FC<FlightResultsProps> = ({ flightData }) => {
  const { flights, summary } = flightData;

  if (!flights || flights.length === 0) {
    return null;
  }

  return (
    <div className="flight-results my-4 space-y-4">
      {/* Summary Stats */}
      {summary && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-4 mb-6">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-purple-600">{summary.totalResults}</div>
              <div className="text-xs text-gray-600">Flights Found</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">${summary.cheapestPrice}</div>
              <div className="text-xs text-gray-600">Lowest Price</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">{summary.fastestDuration}</div>
              <div className="text-xs text-gray-600">Fastest Flight</div>
            </div>
          </div>
        </div>
      )}

      {/* Flight Cards */}
      <div className="space-y-4">
        {flights.map((flight) => (
          <FlightCard key={flight.id} flight={flight} />
        ))}
      </div>
    </div>
  );
};

export default FlightResults;