"""
Provides sustainable farming tips.
"""
TIPS = [
    "Rotate crops to reduce pest buildup and improve soil health.",
    "Use organic compost instead of synthetic fertilizers to lower carbon footprint.",
    "Plant cover crops (e.g., clover) to fix nitrogen and prevent erosion.",
    "Implement drip irrigation to save water.",
    "Integrate agroforestry by planting trees along field boundaries.",
    "Use natural predators (e.g., ladybugs) for pest control instead of pesticides.",
]

def get_sustainability_advice(crop: str) -> str:
    """
    Return general sustainable agriculture tips tailored to the crop.
    """
    # In a real system, we'd filter tips based on crop.
    return "Sustainable farming advice: " + "; ".join(TIPS)