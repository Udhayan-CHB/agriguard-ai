"""
Simulated market prices. In production this would fetch real data from an API or database.
"""
import random

def get_market_prices(crop: str) -> str:
    """
    Return a simulated market price range for the crop.
    """
    # Base price per kg (USD)
    base_prices = {
        "maize": 0.25,
        "rice": 0.40,
        "wheat": 0.30,
        "soybean": 0.50,
    }
    base = base_prices.get(crop.lower(), 0.35)
    # Simulate variation
    low = round(base * (0.8 + random.random() * 0.2), 2)
    high = round(base * (1.0 + random.random() * 0.2), 2)
    return f"Market price for {crop}: ${low} – ${high} per kg (simulated)."