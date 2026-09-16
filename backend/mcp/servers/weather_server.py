"""
MCP Weather Server.
Provides standardized weather data retrieval using OpenWeatherMap API
with seamless fallback to Open-Meteo for high availability.
"""

import logging
import requests
from typing import Dict, Any
from config.settings import settings

logger = logging.getLogger("EchoMind.MCP.Weather")


class WeatherMCPServer:
    """MCP Server providing weather information for cities and locations."""

    name = "weather_mcp_server"
    version = "1.0.0"

    def __init__(self):
        self.timeout = 8

    def execute(self, location: str) -> str:
        """
        Retrieves weather data for the specified location.
        Tries OpenWeatherMap first using WEATHER_API_KEY, falling back to Open-Meteo.
        """
        if not location or not location.strip():
            return "Error: Location cannot be empty. Please provide a city name (e.g., 'Hyderabad', 'London')."

        loc = location.strip()
        logger.info(f"Fetching weather for: {loc}")

        # Strategy 1: OpenWeatherMap with WEATHER_API_KEY
        if settings.has_weather_key():
            try:
                owm_result = self._fetch_openweathermap(loc)
                if owm_result:
                    return owm_result
            except Exception as e:
                logger.warning(f"OpenWeatherMap attempt failed ({e}), attempting Open-Meteo fallback...")

        # Strategy 2: Open-Meteo fallback
        try:
            return self._fetch_openmeteo(loc)
        except Exception as e:
            logger.error(f"Open-Meteo fallback failed: {e}")
            return f"Weather service temporarily unavailable for '{loc}'. Error: {str(e)}"

    def _fetch_openweathermap(self, location: str) -> str:
        """Queries OpenWeatherMap 2.5 API."""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": settings.WEATHER_API_KEY,
            "units": "metric"
        }

        resp = requests.get(url, params=params, timeout=self.timeout)

        if resp.status_code == 200:
            data = resp.json()
            name = data.get("name", location)
            country = data.get("sys", {}).get("country", "")
            main = data.get("main", {})
            weather_list = data.get("weather", [{}])
            desc = weather_list[0].get("description", "clear").title() if weather_list else "Unknown"
            temp = main.get("temp")
            feels_like = main.get("feels_like")
            humidity = main.get("humidity")
            wind = data.get("wind", {}).get("speed", 0)

            loc_str = f"{name}, {country}" if country else name
            return (
                f"Current weather for {loc_str}: {desc}. "
                f"Temperature: {temp}°C (feels like {feels_like}°C). "
                f"Humidity: {humidity}%. Wind Speed: {wind} m/s."
            )
        elif resp.status_code == 404:
            return f"Location '{location}' not found. Please verify the spelling or try specifying the country/state."
        else:
            logger.warning(f"OpenWeatherMap returned status {resp.status_code}: {resp.text}")
            return ""  # Trigger fallback

    def _fetch_openmeteo(self, location: str) -> str:
        """Fallback querying Open-Meteo Geocoding + Forecast APIs (requires no API key)."""
        # Step 1: Geocode
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(location)}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=self.timeout).json()

        if "results" not in geo_resp or not geo_resp["results"]:
            return f"Could not find coordinates or weather data for '{location}'."

        result = geo_resp["results"][0]
        lat = result.get("latitude")
        lon = result.get("longitude")
        name = result.get("name", location)
        country = result.get("country", "")

        # Step 2: Forecast
        forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        fc_resp = requests.get(forecast_url, timeout=self.timeout).json()

        if "current_weather" not in fc_resp:
            return f"Could not retrieve current weather data for '{name}'."

        cw = fc_resp["current_weather"]
        temp = cw.get("temperature")
        wind = cw.get("windspeed")
        time = cw.get("time", "")

        loc_str = f"{name}, {country}" if country else name
        return (
            f"Current weather for {loc_str}: "
            f"Temperature: {temp}°C, Wind Speed: {wind} km/h (recorded at {time})."
        )
