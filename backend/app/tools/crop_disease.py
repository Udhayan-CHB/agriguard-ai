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
        "yellow leaves": "Check for nitrogen deficiency, poor drainage, or early bacterial leaf blight. Keep shallow water (not standing deep water), split nitrogen applications, and remove badly affected leaves.",
        "brown spots": "Brown spot disease (Helminthosporium). Use fungicide and avoid overhead irrigation.",
        "poor yield": "Review plant spacing, split nitrogen application, irrigation timing, and pest pressure. Avoid applying excess nitrogen late in the season and inspect for stem borers and leaf blast.",
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
    crop_kb = KNOWLEDGE.get(crop.lower().strip())
    if not crop_kb:
        return f"No knowledge available for crop '{crop}'. Please consult a local extension officer."

    normalized_problem = problem.lower().replace("yeild", "yield")
    # Simple keyword matching, including common phrasing such as "leaves
    # turning yellow" versus the knowledge key "yellowing".
    problem_words = set(normalized_problem.replace("-", " ").split())
    for key, advice in crop_kb.items():
        key_words = set(key.split())
        if key in normalized_problem or key_words.issubset(problem_words):
            return f"For {crop}, problem '{problem}': {advice}"

    if "yellow" in normalized_problem and "yellowing" in crop_kb:
        return f"For {crop}, problem '{problem}': {crop_kb['yellowing']}"

    return f"For {crop}, problem '{problem}': I don't have exact data. Consult a local agronomist."
