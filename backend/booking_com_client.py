#!/usr/bin/env python3
"""
Booking.com MCP Client - Python wrapper for all booking.com MCP tools.
Uses Streamable HTTP MCP transport (session-based).

Usage:
    from booking_com_client import BookingCom, BookingConfig

    config = BookingConfig(api_key="your-key")
    booking = BookingCom(config)

    # Search flights
    airports = booking.flights.search_destination("London")
    flights = booking.flights.search("JFK.AIRPORT", "LHR.AIRPORT", "2026-03-15")

    # Search hotels
    destinations = booking.hotels.search_destination("Paris")
    hotels = booking.hotels.search("-1456928", "2026-03-15", "2026-03-18")

    # Search cars, attractions, taxis
    booking.cars.search_location("San Francisco")
    booking.attractions.search_location("Tokyo")
    booking.taxi.search_location("Dubai")

    # Meta info
    booking.meta.test_api()
    booking.meta.get_currencies()
"""

import requests, json, os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env from the same directory as this file
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)


@dataclass
class BookingConfig:
    base_url: str = ""
    api_key: str = ""
    server_id: str = ""
    tool_prefix: str = ""
    language_code: str = "en-us"
    currency_code: str = "USD"

    def __post_init__(self):
        if not self.base_url:
            self.base_url = os.environ.get("ANTHROPIC_BASE_URL", "").rstrip("/")
            if not self.base_url:
                raise ValueError("Base URL required via ANTHROPIC_BASE_URL env var or BookingConfig(base_url=...)")
        self.base_url = self.base_url.rstrip("/")
        if not self.api_key:
            self.api_key = os.environ.get("BOOKING_MCP_API_KEY", "") or os.environ.get("ANTHROPIC_API_KEY", "")
            if not self.api_key:
                raise ValueError("API key required via BOOKING_MCP_API_KEY or ANTHROPIC_API_KEY env var or BookingConfig(api_key=...)")
        if not self.server_id:
            self.server_id = os.environ.get("BOOKING_MCP_SERVER_ID", "")
            if not self.server_id:
                self._discover_server_id()

    def _discover_server_id(self):
        """Auto-discover server_id and tool_prefix from the gateway"""
        try:
            r = requests.get(f"{self.base_url}/v1/mcp/server",
                             headers={"Authorization": f"Bearer {self.api_key}"})
            if r.status_code == 200:
                servers = r.json()
                for s in servers:
                    if "booking" in s.get("server_name", "").lower():
                        self.server_id = s["server_id"]
                        self.tool_prefix = s.get("alias", "") + "-" if s.get("alias") else ""
                        return
            raise ValueError("Could not auto-discover server_id")
        except requests.RequestException as e:
            raise ValueError(f"Failed to connect to {self.base_url}: {e}")
        except ValueError:
            raise
        except Exception:
            raise ValueError("server_id required via BOOKING_MCP_SERVER_ID env var or BookingConfig(server_id=...)")


class _MCPSession:
    """MCP REST client using /mcp-rest/tools/call endpoint"""

    def __init__(self, cfg: BookingConfig):
        self.cfg = cfg
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg.api_key}",
        }

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        # Prefix tool name with server alias (e.g. "flights-")
        prefixed_name = f"{self.cfg.tool_prefix}{name}"
        r = requests.post(f"{self.cfg.base_url}/mcp-rest/tools/call",
                          headers=self._headers,
                          json={"name": prefixed_name, "arguments": arguments,
                                "server_id": self.cfg.server_id})

        if r.status_code != 200:
            raise Exception(f"HTTP {r.status_code}: {r.text[:500]}")

        data = r.json()

        # Handle both response formats:
        # Format 1 (direct list): [{"type":"text","text":"..."}]
        # Format 2 (wrapped):     {"content": [{"type":"text","text":"..."}], "isError": false}
        if isinstance(data, list):
            content = data
        else:
            if data.get("isError"):
                content = data.get("content", [])
                err_msg = content[0].get("text", "Unknown error") if content else "Unknown error"
                raise Exception(f"Tool error: {err_msg}")
            content = data.get("content", [])

        for item in content:
            if item.get("type") == "text":
                text = item["text"]
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text
        return data

    def list_tools(self) -> List[Dict]:
        r = requests.get(f"{self.cfg.base_url}/v1/mcp/tools",
                         headers=self._headers)
        if r.status_code != 200:
            return []
        return r.json().get("tools", [])


class _Base:
    def __init__(self, mcp: _MCPSession, cfg: BookingConfig):
        self._mcp = mcp
        self.cfg = cfg

    def _call(self, tool: str, args: Dict[str, Any]) -> Any:
        return self._mcp.call_tool(tool, args)


# ============================================================================
# FLIGHTS
# ============================================================================

class Flights(_Base):
    """Booking.com Flights API"""

    def search_destination(self, query: str, lang: str = None) -> Any:
        """Search airports/cities. Returns IDs for use in search()."""
        return self._call("Search_Flight_Location", {
            "_endpoint": "/api/v1/flights/searchDestination", "_method": "GET",
            "query": query, "languagecode": lang or self.cfg.language_code})

    def search(self, from_id: str, to_id: str, depart_date: str, return_date: str = None,
               adults: int = 1, children: int = 0, infants: int = 0,
               cabin_class: str = "ECONOMY", currency: str = None) -> Any:
        """Search flights. cabin_class: ECONOMY/PREMIUM_ECONOMY/BUSINESS/FIRST"""
        a = {"_endpoint": "/api/v1/flights/searchFlights", "_method": "GET",
             "fromId": from_id, "toId": to_id, "departDate": depart_date,
             "adults": str(adults), "cabinClass": cabin_class,
             "currency_code": currency or self.cfg.currency_code}
        if return_date: a["returnDate"] = return_date
        if children: a["children"] = str(children)
        if infants: a["infants"] = str(infants)
        return self._call("Search_Flights", a)

    def search_multi_stop(self, legs: List[Dict], adults: int = 1,
                          cabin_class: str = "ECONOMY", currency: str = None) -> Any:
        """Multi-stop flights. legs: [{"fromId":"..","toId":"..","departDate":"YYYY-MM-DD"}]"""
        return self._call("Search_Flights_Multi_Stops", {
            "_endpoint": "/api/v1/flights/searchFlightsMultiStops", "_method": "GET",
            "legs": json.dumps(legs), "adults": str(adults), "cabinClass": cabin_class,
            "currency_code": currency or self.cfg.currency_code})

    def get_details(self, token: str) -> Any:
        """Get flight details by token from search results."""
        return self._call("Get_Flight_Details", {
            "_endpoint": "/api/v1/flights/getFlightDetails", "_method": "GET", "token": token})

    def get_seat_map(self, token: str, currency: str = None) -> Any:
        """Get seat map for a flight."""
        return self._call("Get_Seat_Map", {
            "_endpoint": "/api/v1/flights/getSeatMap", "_method": "GET",
            "token": token, "currency_code": currency or self.cfg.currency_code})

    def get_min_price(self, from_id: str, to_id: str, depart_date: str, currency: str = None) -> Any:
        """Get minimum price calendar."""
        return self._call("Get_Min_Price", {
            "_endpoint": "/api/v1/flights/getMinPrice", "_method": "GET",
            "fromId": from_id, "toId": to_id, "departDate": depart_date,
            "currency_code": currency or self.cfg.currency_code})


# ============================================================================
# HOTELS
# ============================================================================

class Hotels(_Base):
    """Booking.com Hotels API"""

    def search_destination(self, query: str) -> Any:
        """Search hotel destinations. Returns dest_id for use in search()."""
        return self._call("Search_Hotel_Destination", {
            "_endpoint": "/api/v1/hotels/searchDestination", "_method": "GET", "query": query})

    def search(self, dest_id: str, checkin: str, checkout: str, adults: int = 1,
               rooms: int = 1, search_type: str = "city", currency: str = None,
               lang: str = None, page: int = 1) -> Any:
        """Search hotels at a destination. search_type: city, district, region, landmark, etc."""
        return self._call("Search_Hotels", {
            "_endpoint": "/api/v1/hotels/searchHotels", "_method": "GET",
            "dest_id": dest_id, "search_type": search_type,
            "arrival_date": checkin, "departure_date": checkout,
            "adults": str(adults), "room_qty": str(rooms), "page_number": str(page),
            "currency_code": currency or self.cfg.currency_code,
            "languagecode": lang or self.cfg.language_code})

    def search_by_coords(self, lat: float, lon: float, checkin: str, checkout: str,
                         adults: int = 1, rooms: int = 1) -> Any:
        """Search hotels by coordinates."""
        return self._call("Search_Hotels_By_Coordinates", {
            "_endpoint": "/api/v1/hotels/searchHotelsByCoordinates", "_method": "GET",
            "latitude": str(lat), "longitude": str(lon),
            "arrival_date": checkin, "departure_date": checkout,
            "adults": str(adults), "room_qty": str(rooms),
            "currency_code": self.cfg.currency_code, "languagecode": self.cfg.language_code})

    def get_details(self, hotel_id: str, checkin: str, checkout: str) -> Any:
        """Get hotel details."""
        return self._call("Get_Hotel_Details", {
            "_endpoint": "/api/v1/hotels/getHotelDetails", "_method": "GET",
            "hotel_id": hotel_id, "arrival_date": checkin, "departure_date": checkout,
            "currency_code": self.cfg.currency_code, "languagecode": self.cfg.language_code})

    def get_photos(self, hotel_id: str) -> Any:
        return self._call("Get_Hotel_Photos", {
            "_endpoint": "/api/v1/hotels/getHotelPhotos", "_method": "GET", "hotel_id": hotel_id})

    def get_reviews(self, hotel_id: str, page: int = 1, sort: str = "sort_most_relevant") -> Any:
        return self._call("Get_Hotel_ReviewsTips", {
            "_endpoint": "/api/v1/hotels/getHotelReviews", "_method": "GET",
            "hotel_id": hotel_id, "languagecode": self.cfg.language_code,
            "page_number": str(page), "sort_option_id": sort})

    def get_rooms(self, hotel_id: str, checkin: str, checkout: str, adults: int = 1) -> Any:
        return self._call("Get_Room_List", {
            "_endpoint": "/api/v1/hotels/getRoomList", "_method": "GET",
            "hotel_id": hotel_id, "arrival_date": checkin, "departure_date": checkout,
            "adults": str(adults), "currency_code": self.cfg.currency_code,
            "languagecode": self.cfg.language_code})

    def get_facilities(self, hotel_id: str) -> Any:
        return self._call("Get_Hotel_Facilities", {
            "_endpoint": "/api/v1/hotels/getHotelFacilities", "_method": "GET",
            "hotel_id": hotel_id, "languagecode": self.cfg.language_code})

    def get_policies(self, hotel_id: str) -> Any:
        return self._call("Get_Hotel_Policies", {
            "_endpoint": "/api/v1/hotels/getHotelPolicies", "_method": "GET",
            "hotel_id": hotel_id, "languagecode": self.cfg.language_code})

    def get_description(self, hotel_id: str) -> Any:
        return self._call("Get_Description_And_Info", {
            "_endpoint": "/api/v1/hotels/getDescriptionAndInfo", "_method": "GET",
            "hotel_id": hotel_id, "languagecode": self.cfg.language_code})


# ============================================================================
# CAR RENTALS
# ============================================================================

class Cars(_Base):
    """Booking.com Car Rentals API"""

    def search_location(self, query: str, lang: str = None) -> Any:
        return self._call("Search_Car_Location", {
            "_endpoint": "/api/v1/cars/searchDestination", "_method": "GET",
            "query": query, "languagecode": lang or self.cfg.language_code})

    def search(self, pickup_id: str, dropoff_id: str, pickup_date: str, pickup_time: str,
               dropoff_date: str, dropoff_time: str, driver_age: int = 30) -> Any:
        return self._call("Search_Car_Rentals", {
            "_endpoint": "/api/v1/cars/searchCarRentals", "_method": "GET",
            "pick_up_location_id": pickup_id, "drop_off_location_id": dropoff_id,
            "pick_up_date": pickup_date, "pick_up_time": pickup_time,
            "drop_off_date": dropoff_date, "drop_off_time": dropoff_time,
            "driver_age": str(driver_age), "currency_code": self.cfg.currency_code,
            "languagecode": self.cfg.language_code})

    def get_vehicle_details(self, vehicle_id: str, pickup_date: str, pickup_time: str,
                            dropoff_date: str, dropoff_time: str) -> Any:
        return self._call("Vehicle_Details", {
            "_endpoint": "/api/v1/cars/getVehicleDetails", "_method": "GET",
            "vehicle_id": vehicle_id, "pick_up_date": pickup_date, "pick_up_time": pickup_time,
            "drop_off_date": dropoff_date, "drop_off_time": dropoff_time,
            "currency_code": self.cfg.currency_code})


# ============================================================================
# ATTRACTIONS
# ============================================================================

class Attractions(_Base):
    """Booking.com Attractions API"""

    def search_location(self, query: str, lang: str = None) -> Any:
        return self._call("Search_Attraction_Location", {
            "_endpoint": "/api/v1/attraction/searchLocation", "_method": "GET",
            "query": query, "languagecode": lang or self.cfg.language_code})

    def search(self, location_id: str) -> Any:
        return self._call("Search_Attractions", {
            "_endpoint": "/api/v1/attraction/searchAttractions", "_method": "GET",
            "id": location_id, "currency_code": self.cfg.currency_code,
            "languagecode": self.cfg.language_code})

    def get_details(self, slug: str) -> Any:
        return self._call("Get_Attraction_Details", {
            "_endpoint": "/api/v1/attraction/getAttractionDetails", "_method": "GET",
            "slug": slug, "currency_code": self.cfg.currency_code,
            "languagecode": self.cfg.language_code})

    def get_reviews(self, slug: str) -> Any:
        return self._call("Get_Attraction_Reviews", {
            "_endpoint": "/api/v1/attraction/getAttractionReviews", "_method": "GET",
            "slug": slug, "languagecode": self.cfg.language_code})

    def get_nearby(self, lat: float, lon: float) -> Any:
        return self._call("Get_Popular_Attraction_Near_By", {
            "_endpoint": "/api/v1/attraction/getPopularAttractionNearBy", "_method": "GET",
            "latitude": str(lat), "longitude": str(lon), "languagecode": self.cfg.language_code})


# ============================================================================
# TAXI
# ============================================================================

class Taxi(_Base):
    """Booking.com Taxi API"""

    def search_location(self, query: str, lang: str = None) -> Any:
        return self._call("Taxi_Search_Location", {
            "_endpoint": "/api/v1/taxi/searchLocation", "_method": "GET",
            "query": query, "languagecode": lang or self.cfg.language_code})

    def search(self, pickup_id: str, dropoff_id: str, pickup_date: str, pickup_time: str) -> Any:
        return self._call("Search_Taxi", {
            "_endpoint": "/api/v1/taxi/searchTaxi", "_method": "GET",
            "pick_up_place_id": pickup_id, "drop_off_place_id": dropoff_id,
            "pick_up_date": pickup_date, "pick_up_time": pickup_time,
            "currency_code": self.cfg.currency_code})


# ============================================================================
# META / UTILITY
# ============================================================================

class Meta(_Base):
    """Booking.com Meta/Utility API"""

    def test_api(self) -> Any:
        return self._call("Test_API", {
            "_endpoint": "/api/v1/meta/testApi", "_method": "GET"})

    def get_currencies(self) -> Any:
        return self._call("Get_Currency", {
            "_endpoint": "/api/v1/meta/getCurrency", "_method": "GET"})

    def get_exchange_rates(self, base_currency: str = "USD") -> Any:
        return self._call("Get_Exchange_Rates", {
            "_endpoint": "/api/v1/meta/getExchangeRates", "_method": "GET",
            "base_currency": base_currency})

    def get_languages(self) -> Any:
        return self._call("Get_Languages", {
            "_endpoint": "/api/v1/meta/getLanguages", "_method": "GET"})

    def location_to_latlong(self, query: str) -> Any:
        return self._call("Location_to_Lat_Long", {
            "_endpoint": "/api/v1/meta/locationToLatLong", "_method": "GET", "query": query})

    def get_nearby_cities(self, lat: float, lon: float, lang: str = None) -> Any:
        return self._call("Get_Nearby_Cities", {
            "_endpoint": "/api/v1/meta/getNearbyCities", "_method": "GET",
            "latitude": str(lat), "longitude": str(lon),
            "languagecode": lang or self.cfg.language_code})


# ============================================================================
# MAIN FACADE
# ============================================================================

class BookingCom:
    """Unified interface to all Booking.com MCP tools."""

    def __init__(self, config: BookingConfig = None):
        self.config = config or BookingConfig()
        self._mcp = _MCPSession(self.config)
        self.flights = Flights(self._mcp, self.config)
        self.hotels = Hotels(self._mcp, self.config)
        self.cars = Cars(self._mcp, self.config)
        self.attractions = Attractions(self._mcp, self.config)
        self.taxi = Taxi(self._mcp, self.config)
        self.meta = Meta(self._mcp, self.config)

    def list_tools(self) -> List[Dict]:
        """List all available MCP tools."""
        return self._mcp.list_tools()


if __name__ == "__main__":
    import sys

    # No need to pass api_key explicitly — BookingConfig will auto-load
    # from BOOKING_MCP_API_KEY or ANTHROPIC_API_KEY (loaded from .env)
    try:
        booking = BookingCom()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    pp = lambda x: print(json.dumps(x, indent=2)[:500] if isinstance(x, (dict, list)) else str(x)[:500])

    print("=== Booking.com MCP Client Tests ===\n")

    print("1. List tools...")
    tools = booking.list_tools()
    print(f"   {len(tools)} tools available\n")

    print("2. Test API...")
    try:
        pp(booking.meta.test_api())
    except Exception as e:
        print(f"   Error: {e}\n")

    print("\n3. Search flight destinations: 'London'...")
    try:
        pp(booking.flights.search_destination("London"))
    except Exception as e:
        print(f"   Error: {e}\n")

    print("\n4. Search hotel destinations: 'Paris'...")
    try:
        pp(booking.hotels.search_destination("Paris"))
    except Exception as e:
        print(f"   Error: {e}\n")

    print("\n5. Search car locations: 'San Francisco'...")
    try:
        pp(booking.cars.search_location("San Francisco"))
    except Exception as e:
        print(f"   Error: {e}\n")

    print("\n6. Search attraction locations: 'Tokyo'...")
    try:
        pp(booking.attractions.search_location("Tokyo"))
    except Exception as e:
        print(f"   Error: {e}\n")

    print("\n7. Search taxi locations: 'Dubai'...")
    try:
        pp(booking.taxi.search_location("Dubai"))
    except Exception as e:
        print(f"   Error: {e}\n")

    print("\n8. Get nearby cities (NYC 40.71, -74.00)...")
    try:
        pp(booking.meta.get_nearby_cities(40.7128, -74.0060))
    except Exception as e:
        print(f"   Error: {e}\n")

    print("\n=== Tests complete ===")
