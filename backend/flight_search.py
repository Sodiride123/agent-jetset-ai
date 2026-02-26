#!/usr/bin/env python3
"""
Fixed Flight Search Script - Deterministic flight search with proper error handling.

Usage:
    python flight_search.py --origin "Beijing" --destination "Melbourne" --date "2026-03-06" --adults 1 --cabin_class "ECONOMY"

Output:
    Saves results to /tmp/jetset_flights.json and prints status message.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from booking_com_client import BookingCom


def parse_date(date_str: str) -> str:
    """Parse various date formats and return YYYY-MM-DD format."""
    date_str = date_str.strip().lower()
    today = datetime.now()

    # Handle relative dates
    if date_str in ['today', 'tonight']:
        return today.strftime('%Y-%m-%d')
    elif date_str == 'tomorrow':
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'next' in date_str:
        # Handle "next friday", "next week", etc.
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(weekdays):
            if day in date_str:
                days_ahead = i - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        # "next week" = 7 days from now
        if 'week' in date_str:
            return (today + timedelta(days=7)).strftime('%Y-%m-%d')
        # "next month" = 30 days from now
        if 'month' in date_str:
            return (today + timedelta(days=30)).strftime('%Y-%m-%d')

    # Handle weekday names (this friday, friday, etc.)
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for i, day in enumerate(weekdays):
        if day in date_str and 'next' not in date_str:
            # "this friday" or just "friday" means the coming one
            days_ahead = i - today.weekday()
            if days_ahead < 0:  # If day passed, use next week
                days_ahead += 7
            elif days_ahead == 0:
                days_ahead = 7  # If today is that day, use next week
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

    # Try to parse standard date formats
    formats = [
        '%Y-%m-%d',       # 2026-03-06
        '%Y/%m/%d',       # 2026/03/06
        '%m/%d/%Y',       # 03/06/2026
        '%d/%m/%Y',       # 06/03/2026
        '%B %d, %Y',      # March 6, 2026
        '%b %d, %Y',      # Mar 6, 2026
        '%B %d %Y',       # March 6 2026
        '%b %d %Y',       # Mar 6 2026
        '%d %B %Y',       # 6 March 2026
        '%d %b %Y',       # 6 Mar 2026
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            continue

    # Default: return as-is if already in correct format, else use a week from now
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str

    # Fallback to 7 days from now
    print(f"WARNING: Could not parse date '{date_str}', using 7 days from now")
    return (today + timedelta(days=7)).strftime('%Y-%m-%d')


def search_flights(origin: str, destination: str, date: str, adults: int = 1,
                   cabin_class: str = "ECONOMY", return_date: str = None) -> dict:
    """
    Search for flights using the booking.com API.

    Returns dict with 'success', 'flights', 'summary', and 'error' keys.
    """
    result = {
        "success": False,
        "flights": [],
        "summary": {},
        "error": None,
        "search_params": {
            "origin": origin,
            "destination": destination,
            "date": date,
            "adults": adults,
            "cabin_class": cabin_class
        }
    }

    try:
        booking = BookingCom()
    except Exception as e:
        result["error"] = f"Failed to initialize booking client: {str(e)}"
        return result

    # Step 1: Search for origin airport/city ID
    try:
        origin_response = booking.flights.search_destination(origin)
        origin_data = origin_response.get('data', [])
        if not origin_data:
            result["error"] = f"Could not find airport/city for origin: {origin}"
            return result
        origin_id = origin_data[0]['id']
        origin_name = origin_data[0].get('name', origin)
        result["search_params"]["origin_id"] = origin_id
        result["search_params"]["origin_name"] = origin_name
    except Exception as e:
        result["error"] = f"Failed to search origin '{origin}': {str(e)}"
        return result

    # Step 2: Search for destination airport/city ID
    try:
        dest_response = booking.flights.search_destination(destination)
        dest_data = dest_response.get('data', [])
        if not dest_data:
            result["error"] = f"Could not find airport/city for destination: {destination}"
            return result
        dest_id = dest_data[0]['id']
        dest_name = dest_data[0].get('name', destination)
        result["search_params"]["dest_id"] = dest_id
        result["search_params"]["dest_name"] = dest_name
    except Exception as e:
        result["error"] = f"Failed to search destination '{destination}': {str(e)}"
        return result

    # Step 3: Search for flights
    try:
        flights_response = booking.flights.search(
            from_id=origin_id,
            to_id=dest_id,
            depart_date=date,
            return_date=return_date,
            adults=adults,
            cabin_class=cabin_class.upper()
        )
    except Exception as e:
        result["error"] = f"Failed to search flights: {str(e)}"
        return result

    # Step 4: Process flight results
    data = flights_response.get('data', {})
    flight_offers = data.get('flightOffers', [])

    if not flight_offers:
        result["error"] = None  # Not an error, just no flights found
        result["success"] = True
        result["summary"] = {
            "totalResults": 0,
            "message": f"No flights found from {origin_name} to {dest_name} on {date}"
        }
        return result

    processed_flights = []
    min_price = float('inf')
    fastest_duration = None
    fastest_seconds = float('inf')

    for i, offer in enumerate(flight_offers[:8]):  # Limit to 8 flights
        try:
            token = offer.get('token', '')
            price_info = offer.get('priceBreakdown', {}).get('totalRounded', {})
            price = price_info.get('units', 0)
            currency = price_info.get('currencyCode', 'USD')

            segments = offer.get('segments', [])
            if not segments:
                continue
            segment = segments[0]
            legs = segment.get('legs', [])
            total_time_sec = segment.get('totalTime', 0)

            if not legs:
                continue
            first_leg = legs[0]
            last_leg = legs[-1]

            # Format duration
            hours = total_time_sec // 3600
            minutes = (total_time_sec % 3600) // 60
            duration = f"{hours}h {minutes}m"

            # Departure info
            dep_time_str = first_leg.get('departureTime', '')
            dep_airport = first_leg.get('departureAirport', {})

            # Arrival info
            arr_time_str = last_leg.get('arrivalTime', '')
            arr_airport = last_leg.get('arrivalAirport', {})

            # Airline info
            carriers = first_leg.get('carriersData', [])
            airline = carriers[0].get('name', 'Unknown') if carriers else 'Unknown'
            carrier_code = carriers[0].get('code', '') if carriers else ''
            flight_number = first_leg.get('flightInfo', {}).get('flightNumber', '')

            stops = len(legs) - 1

            # Extract layover cities from intermediate legs
            layover_cities = []
            if stops > 0:
                for leg in legs[:-1]:
                    arr_city = leg.get('arrivalAirport', {}).get('cityName', '')
                    if arr_city:
                        layover_cities.append(arr_city)

            flight = {
                "id": str(i + 1),
                "airline": airline,
                "flightNumber": f"{carrier_code}{flight_number}" if carrier_code and flight_number else "",
                "price": price,
                "currency": currency,
                "departure": {
                    "time": dep_time_str[11:16] if len(dep_time_str) > 16 else "",
                    "date": dep_time_str[:10] if len(dep_time_str) >= 10 else "",
                    "airport": dep_airport.get('code', ''),
                    "city": dep_airport.get('cityName', '')
                },
                "arrival": {
                    "time": arr_time_str[11:16] if len(arr_time_str) > 16 else "",
                    "date": arr_time_str[:10] if len(arr_time_str) >= 10 else "",
                    "airport": arr_airport.get('code', ''),
                    "city": arr_airport.get('cityName', '')
                },
                "duration": duration,
                "stops": stops,
                "layovers": layover_cities,
                "class": cabin_class.capitalize(),
                "tags": [],
                "token": token
            }
            processed_flights.append(flight)

            # Track cheapest and fastest
            if price < min_price:
                min_price = price
            if total_time_sec < fastest_seconds:
                fastest_seconds = total_time_sec
                fastest_duration = duration

        except Exception as e:
            # Skip this flight offer if processing fails
            print(f"WARNING: Failed to process flight offer {i}: {e}")
            continue

    # Add tags (cheapest, fastest)
    for flight in processed_flights:
        if flight['price'] == min_price:
            flight['tags'].append('cheapest')
        if flight['duration'] == fastest_duration:
            flight['tags'].append('fastest')

    # Build result
    result["success"] = True
    result["flights"] = processed_flights
    result["summary"] = {
        "totalResults": len(processed_flights),
        "cheapestPrice": min_price if min_price != float('inf') else 0,
        "fastestDuration": fastest_duration or "N/A",
        "averagePrice": round(sum(f['price'] for f in processed_flights) / len(processed_flights)) if processed_flights else 0,
        "currency": processed_flights[0]['currency'] if processed_flights else "USD",
        "origin": origin_name,
        "destination": dest_name,
        "date": date
    }

    return result


def main():
    parser = argparse.ArgumentParser(description='Search for flights')
    parser.add_argument('--origin', '-o', required=True, help='Origin city/airport')
    parser.add_argument('--destination', '-d', required=True, help='Destination city/airport')
    parser.add_argument('--date', '-t', required=True, help='Departure date (YYYY-MM-DD or natural language)')
    parser.add_argument('--adults', '-a', type=int, default=1, help='Number of adults')
    parser.add_argument('--cabin_class', '-c', default='ECONOMY',
                        choices=['ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST'],
                        help='Cabin class')
    parser.add_argument('--return_date', '-r', help='Return date for round trip')
    parser.add_argument('--output', default='/tmp/jetset_flights.json', help='Output file path')

    args = parser.parse_args()

    # Parse the date
    parsed_date = parse_date(args.date)

    # Search for flights
    result = search_flights(
        origin=args.origin,
        destination=args.destination,
        date=parsed_date,
        adults=args.adults,
        cabin_class=args.cabin_class,
        return_date=args.return_date
    )

    # Build output structure
    output = {
        "flights": result.get("flights", []),
        "summary": result.get("summary", {}),
        "search_params": result.get("search_params", {}),
        "error": result.get("error")
    }

    # Save to file
    try:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"FLIGHT_FILE_SAVED:{args.output}")
    except Exception as e:
        print(f"ERROR: Failed to save results: {e}")
        sys.exit(1)

    # Print status
    if result["success"]:
        flights = result.get("flights", [])
        if flights:
            summary = result.get("summary", {})
            print(f"SUCCESS: Found {len(flights)} flights from {summary.get('origin', args.origin)} to {summary.get('destination', args.destination)} on {parsed_date}")
            print(f"Cheapest: ${summary.get('cheapestPrice', 'N/A')} {summary.get('currency', 'USD')}")
            print(f"Fastest: {summary.get('fastestDuration', 'N/A')}")
        else:
            print(f"NO_FLIGHTS_FOUND: No flights available from {args.origin} to {args.destination} on {parsed_date}")
    else:
        print(f"ERROR: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
