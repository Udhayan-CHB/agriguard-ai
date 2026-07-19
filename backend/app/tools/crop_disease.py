"""
Simulated crop disease knowledge base.
In a real system this would be replaced by RAG over agricultural documents.
"""
KNOWLEDGE = {
    "maize": {
        "yellow leaves": "Nitrogen deficiency or Maize Streak Virus. Apply nitrogen‑rich fertilizer and remove infected plants.",
        "spots on leaves": "Northern Corn Leaf Blight. Use fungicides (mancozeb) and rotate crops.",
        "stunted growth": "Phosphorus deficiency. Apply phosphate fertilizer.",
    },
    "rice": {
        "yellowing": "Iron deficiency or Bacterial Leaf Blight. Improve drainage and apply iron chelates.",
        "brown spots": "Brown spot disease (Helminthosporium). Use fungicide and avoid overhead irrigation.",
    },
    "wheat": {
        "yellowing": "Nitrogen deficiency. Top dress with urea.",
        "rust": "Wheat rust. Apply propiconazole.",
    },
}

def diagnose(crop: str, problem: str) -> str:
    """
    Looks up common problems and gives advice.
    """
    crop_kb = KNOWLEDGE.get(crop.lower())
    if not crop_kb:
        return f"No knowledge available for crop '{crop}'. Please consult a local extension officer."

    # Simple keyword matching
    for key, advice in crop_kb.items():
        if key in problem.lower():
            return f"For {crop}, problem '{problem}': {advice}"

    return f"For {crop}, problem '{problem}': I don't have exact data. Consult a local agronomist."