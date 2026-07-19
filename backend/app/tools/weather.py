"""
Fetches current weather and a simple forecast from Open-Meteo (free, no key).
"""
import requests
from typing import Optional

def get_weather(lat: float, lon: float) -> str:
    """
    Get current weather and a 3‑day summary for a location.
    Returns a human‑readable string.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weathercode"],
        "timezone": "auto",
        "forecast_days": 3,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current_weather", {})
        daily = data.get("daily", {})

        weather_str = f"Current weather: {current.get('temperature')}°C, wind {current.get('windspeed')} km/h.\n"
        weather_str += "3‑day forecast:\n"

        times = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        codes = daily.get("weathercode", [])

        for i in range(min(len(times), 3)):
            weather_str += (
                f"  {times[i]}: {min_temps[i]}°C – {max_temps[i]}°C, "
                f"rain {precip[i]} mm, code {codes[i]}\n"
            )
        return weather_str
    except Exception as e:
        return f"Weather data unavailable: {e}"