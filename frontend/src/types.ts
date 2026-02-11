export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  flightData?: FlightData;
}

export interface Flight {
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

export interface FlightData {
  flights: Flight[];
  summary?: {
    totalResults: number;
    cheapestPrice: number;
    fastestDuration: string;
    averagePrice: number;
  };
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  flight_data?: FlightData;
  tool_uses?: Array<{
    tool: string;
    input: any;
  }>;
  needs_continuation?: boolean;
}