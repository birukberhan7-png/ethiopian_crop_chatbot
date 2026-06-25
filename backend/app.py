"""
AI Crop Recommendation Chatbot - Flask Backend
Ethiopian Endemic Plants Recommendation System
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

# ─── App Setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

# In-memory chat history store  {session_id: [messages]}
chat_sessions = {}

# ─── Load ML Model ────────────────────────────────────────────────────────────
import joblib
MODEL_DIR = os.path.join(BASE_DIR, "models")

try:
    clf            = joblib.load(os.path.join(MODEL_DIR, "crop_model.pkl"))
    soil_encoder   = joblib.load(os.path.join(MODEL_DIR, "soil_encoder.pkl"))
    region_encoder = joblib.load(os.path.join(MODEL_DIR, "region_encoder.pkl"))
    crop_encoder   = joblib.load(os.path.join(MODEL_DIR, "crop_encoder.pkl"))
    with open(os.path.join(MODEL_DIR, "meta.json")) as f:
        META = json.load(f)
    ML_READY = True
    print("✅ ML model loaded successfully")
except Exception as e:
    ML_READY = False
    META = {}
    print(f"⚠️  ML model not found: {e}  — run ml/train_model.py first")

# ─── Crop Knowledge Base ──────────────────────────────────────────────────────
CROP_INFO = {
    "Teff": {
        "description": "Teff is Ethiopia's most iconic grain, the backbone of injera. It thrives in highland areas.",
        "altitude": "1500–2800m",
        "rainfall": "500–900mm/year",
        "temperature": "18–25°C",
        "soil": "Well-drained loam or clay soils, pH 5.5–7.0",
        "npk": "N: 60–120 kg/ha, P: 30–60 kg/ha",
        "planting_tips": "Plant at onset of main rains (June–July). Broadcast sow at 5 kg/ha. Weed early.",
        "harvest": "85–95 days after sowing",
        "zones": ["Amhara", "Oromia", "Tigray", "SNNPR"]
    },
    "Enset": {
        "description": "Enset (False Banana) is a staple for millions in southern Ethiopia. Its fermented root is used for kocho and bulla.",
        "altitude": "1500–3000m",
        "rainfall": "1000–1500mm/year",
        "temperature": "10–25°C",
        "soil": "Deep, well-drained fertile soils, pH 5.5–6.5",
        "npk": "Responds well to organic manure + N: 40–80 kg/ha",
        "planting_tips": "Plant suckers in well-prepared pits. Perennial — takes 5–10 years to mature. Dense planting for food forests.",
        "harvest": "5–10 years (vegetative crop)",
        "zones": ["SNNPR", "Sidama", "Oromia"]
    },
    "Coffee Arabica": {
        "description": "Ethiopia is the birthplace of Arabica coffee. A premium export crop with rich biodiversity.",
        "altitude": "1500–2200m",
        "rainfall": "1200–2000mm/year",
        "temperature": "15–24°C",
        "soil": "Deep, well-drained loam with organic matter, pH 5.5–6.5",
        "npk": "N: 80–120 kg/ha, P: 40–60 kg/ha, K: 60–80 kg/ha",
        "planting_tips": "Shade-grown under forest trees is traditional. Plant seedlings in nursery first. Mulch heavily.",
        "harvest": "October–February (main harvest)",
        "zones": ["Oromia", "SNNPR", "Sidama"]
    },
    "Noug": {
        "description": "Noug (Niger seed / Guizotia abyssinica) is an ancient Ethiopian oilseed crop used for edible oil and bird feed.",
        "altitude": "1500–2500m",
        "rainfall": "700–1200mm/year",
        "temperature": "15–25°C",
        "soil": "Clay or black soils, pH 5.5–7.0",
        "npk": "N: 30–60 kg/ha, P: 20–40 kg/ha",
        "planting_tips": "Broadcast seed at 5–8 kg/ha. Tolerates waterlogged black soils where other crops fail.",
        "harvest": "90–120 days after sowing",
        "zones": ["Oromia", "Amhara", "Tigray", "SNNPR"]
    },
    "Barley": {
        "description": "Highland barley is one of Ethiopia's oldest cereals, vital for tella (local beer) and food.",
        "altitude": "2000–3500m (afro-alpine)",
        "rainfall": "400–700mm/year",
        "temperature": "5–20°C",
        "soil": "Sandy loam to clay loam, pH 5.5–7.5",
        "npk": "N: 60–100 kg/ha, P: 30–60 kg/ha",
        "planting_tips": "Plant in Meher season (June–August). Excellent cold tolerance for high altitude areas.",
        "harvest": "90–120 days after sowing",
        "zones": ["Amhara", "Oromia", "Tigray"]
    },
    "Sorghum": {
        "description": "Sorghum is a drought-tolerant staple for Ethiopia's lowland and semi-arid regions.",
        "altitude": "500–1500m",
        "rainfall": "400–700mm/year",
        "temperature": "25–35°C",
        "soil": "Deep clay or loam soils, pH 5.5–7.5",
        "npk": "N: 40–80 kg/ha, P: 20–40 kg/ha",
        "planting_tips": "Plant at start of rains. Highly drought-tolerant once established. Suited for Afar and Somali lowlands.",
        "harvest": "90–130 days after sowing",
        "zones": ["Afar", "Somali", "Oromia (lowland)"]
    },
    "Finger Millet": {
        "description": "Finger Millet (Eleusine coracana) is a nutritious grain important for food security and local beer.",
        "altitude": "1000–2200m",
        "rainfall": "500–1000mm/year",
        "temperature": "18–28°C",
        "soil": "Sandy loam, pH 5.0–7.0",
        "npk": "N: 40–80 kg/ha, P: 20–40 kg/ha",
        "planting_tips": "Excellent for inter-cropping. Tolerates poor soils. Very nutritious — high in calcium and iron.",
        "harvest": "90–120 days after sowing",
        "zones": ["SNNPR", "Oromia", "Sidama"]
    },
    "Chickpea": {
        "description": "Chickpea (shimbra in Amharic) is a key legume crop and protein source, also fixing nitrogen.",
        "altitude": "1500–2500m",
        "rainfall": "500–900mm/year",
        "temperature": "15–25°C",
        "soil": "Well-drained black or clay soils, pH 5.5–7.0",
        "npk": "P: 40–60 kg/ha (N-fixing legume — minimal N needed)",
        "planting_tips": "Excellent rotation crop after cereals. Inoculate seeds with Rhizobium. Avoid waterlogging.",
        "harvest": "75–100 days after sowing",
        "zones": ["Oromia", "Amhara", "Tigray"]
    },
    "Linseed": {
        "description": "Linseed (Linum usitatissimum) is an oilseed and fiber crop grown in Ethiopian highlands.",
        "altitude": "2000–3000m",
        "rainfall": "600–1000mm/year",
        "temperature": "15–22°C",
        "soil": "Well-drained loam or clay loam, pH 5.5–7.0",
        "npk": "N: 40–80 kg/ha, P: 30–50 kg/ha",
        "planting_tips": "Cool highland crop. Excellent for Meher season. Used for oil, food, and linen fiber.",
        "harvest": "90–120 days after sowing",
        "zones": ["Amhara", "Oromia", "Tigray"]
    },
    "Maize": {
        "description": "Maize is a major food crop across Ethiopia's mid-altitude zones.",
        "altitude": "1000–2500m",
        "rainfall": "700–1200mm/year",
        "temperature": "18–30°C",
        "soil": "Well-drained loam or sandy loam, pH 5.5–7.0",
        "npk": "N: 100–150 kg/ha, P: 40–80 kg/ha, K: 40–60 kg/ha",
        "planting_tips": "Plant at start of main rains. Responds well to fertilizer. Space 75×25 cm. Weed at 2–4 weeks.",
        "harvest": "90–120 days after sowing",
        "zones": ["Oromia", "SNNPR", "Amhara", "Benishangul-Gumuz"]
    }
}

# ─── Rule-based Altitude Logic ────────────────────────────────────────────────
def altitude_based_recommendation(altitude):
    """Fallback rule-based recommendation when ML confidence is low."""
    if altitude >= 3200:
        return "Barley", "Afro-alpine zone (>3200m). Barley is the most cold-tolerant highland cereal."
    elif altitude >= 2500:
        return "Barley", "Upper montane zone. Barley or Linseed are most suitable at this altitude."
    elif altitude >= 1800:
        return "Teff", "Mid-highland montane zone (1800–2500m). Ideal for Teff — Ethiopia's signature grain."
    elif altitude >= 1200:
        return "Maize", "Lower montane zone (1200–1800m). Maize and Coffee Arabica thrive here."
    else:
        return "Sorghum", "Lowland zone (<1200m). Drought-tolerant Sorghum or Finger Millet are best."

# ─── ML Prediction ────────────────────────────────────────────────────────────
def predict_crop(data):
    """Run ML prediction and return crop name + confidence."""
    if not ML_READY:
        return None, 0.0

    try:
        soil_enc = soil_encoder.transform([data["soil_type"]])[0] \
            if data["soil_type"] in soil_encoder.classes_ \
            else soil_encoder.transform([soil_encoder.classes_[0]])[0]

        region_enc = region_encoder.transform([data["region"]])[0] \
            if data.get("region") and data["region"] in region_encoder.classes_ \
            else 0

        features = [[
            data["temperature"],
            data["humidity"],
            data["rainfall"],
            data["ph"],
            data["altitude"],
            data["nitrogen"],
            data["phosphorus"],
            data["potassium"],
            soil_enc,
            region_enc
        ]]

        proba = clf.predict_proba(features)[0]
        pred_idx = proba.argmax()
        confidence = float(proba[pred_idx])
        crop_name = crop_encoder.inverse_transform([pred_idx])[0]
        return crop_name, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        return None, 0.0

# ─── Chatbot Engine ───────────────────────────────────────────────────────────
WELCOME_MSG = """🌿 **Selam! Welcome to the Ethiopian Crop Recommendation Chatbot!**

I can help you find the best endemic crop for your land.

**What I can do:**
- 🔍 Recommend crops based on your soil & climate
- 🌾 Tell you about Ethiopian endemic crops
- 📍 Give region-specific advice
- 💡 Provide planting & farming tips

**To get a recommendation, tell me:**
> *"Recommend a crop"* or type your conditions like:
> *"My altitude is 2200m, temperature 22°C, rainfall 800mm"*

Or ask me directly:
> *"Tell me about Teff"*
> *"What grows in Oromia?"*
> *"Best crop for altitude 1800m"*

What would you like to know? 🇪🇹"""


def extract_number(text, keyword):
    """Extract a number after a keyword in text."""
    import re
    patterns = [
        rf"{keyword}[:\s=]+([0-9.]+)",
        rf"([0-9.]+)\s*(?:m|mm|°c|%|kg)?\s+(?:{keyword})",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            grp = m.group(1)
            if grp is not None:
                return float(grp)
    return None


def chatbot_reply(session_id, user_message):
    """Main chatbot response logic."""
    msg = user_message.strip().lower()

    # ── Greetings ──────────────────────────────────────────────────────────
    greetings = ["hi", "hello", "selam", "hey", "start", "ሰላም"]
    if any(msg.startswith(g) for g in greetings):
        return WELCOME_MSG

    # ── Help ───────────────────────────────────────────────────────────────
    if any(k in msg for k in ["help", "what can you do", "menu", "commands"]):
        return WELCOME_MSG

    # ── Crop Info ──────────────────────────────────────────────────────────
    for crop_name, info in CROP_INFO.items():
        if crop_name.lower() in msg or (crop_name == "Coffee Arabica" and "coffee" in msg):
            return format_crop_info(crop_name, info)

    # ── Region-based query ─────────────────────────────────────────────────
    regions_map = {
        "oromia": ["Teff", "Coffee Arabica", "Maize", "Chickpea", "Sorghum"],
        "amhara": ["Teff", "Barley", "Wheat", "Chickpea", "Linseed"],
        "tigray": ["Teff", "Barley", "Sorghum", "Chickpea", "Noug"],
        "sidama": ["Enset", "Coffee Arabica", "Teff", "Maize"],
        "snnpr":  ["Enset", "Finger Millet", "Coffee Arabica", "Maize", "Teff"],
        "afar":   ["Sorghum", "Finger Millet"],
        "somali": ["Sorghum", "Finger Millet"],
        "benishangul": ["Maize", "Sorghum", "Teff"],
    }
    for region_key, crops in regions_map.items():
        if region_key in msg:
            region_display = region_key.replace("-", " ").title()
            crop_list = ", ".join(f"**{c}**" for c in crops)
            return (f"🌍 **Recommended crops for {region_display} region:**\n\n"
                    f"{crop_list}\n\n"
                    f"Ask me about any of these crops for detailed farming advice! "
                    f"Or say *'recommend a crop'* and provide your conditions for a personalized AI recommendation.")

    # ── Altitude quick query ────────────────────────────────────────────────
    alt_val = extract_number(msg, r"altitude|elevation|masl|meters")
    if alt_val and not any(k in msg for k in ["temperature", "humidity", "rainfall", "ph"]):
        crop, reason = altitude_based_recommendation(alt_val)
        info = CROP_INFO.get(crop, {})
        zone = get_altitude_zone(alt_val)
        return (f"📏 **Based on altitude {alt_val:.0f}m ({zone}):**\n\n"
                f"✅ Recommended: **{crop}**\n"
                f"📝 {reason}\n\n"
                f"💡 {info.get('planting_tips','')}\n\n"
                f"For a more precise AI-powered recommendation, provide:\n"
                f"> temperature, humidity, rainfall, soil pH, and soil type.")

    # ── Full ML Recommendation ─────────────────────────────────────────────
    need_recommend = any(k in msg for k in [
        "recommend", "suggest", "best crop", "what crop", "which crop",
        "crop for", "predict", "analyze", "analyse", "give me a crop"
    ])

    # Try to extract all parameters from message
    params = parse_params_from_message(msg)

    if need_recommend or (params and len(params) >= 4):
        if len(params) < 5:
            # Collect mode — ask for missing info
            session = chat_sessions.setdefault(session_id, {})
            session.update(params)
            return ask_for_missing(session)
        else:
            return run_full_recommendation(params)

    # ── Partial data continuation ──────────────────────────────────────────
    session = chat_sessions.get(session_id, {})
    if session:
        new_params = parse_params_from_message(msg)
        session.update(new_params)
        chat_sessions[session_id] = session
        if len(session) >= 5 and all(k in session for k in ["temperature", "altitude", "rainfall"]):
            result = run_full_recommendation(session)
            chat_sessions[session_id] = {}
            return result
        return ask_for_missing(session)

    # ── Numbers entered without context ────────────────────────────────────
    params = parse_params_from_message(msg)
    if params:
        session = chat_sessions.setdefault(session_id, {})
        session.update(params)
        return ask_for_missing(session)

    # ── Farming general tips ────────────────────────────────────────────────
    if any(k in msg for k in ["tip", "advice", "fertilizer", "irrigation", "plant"]):
        return ("🌱 **General Ethiopian Farming Tips:**\n\n"
                "1. **Soil preparation** — Deep plough before main rains (May–June)\n"
                "2. **Fertilizer** — Use NPSB (Nitrogen-Phosphorus-Sulfur-Boron) as base dressing\n"
                "3. **Weeding** — First weeding at 2–3 weeks after emergence is critical\n"
                "4. **Altitude zones** — Match crops to your agro-ecology: highland vs lowland\n"
                "5. **Rotation** — Alternate cereals with legumes (chickpea, faba bean) for soil health\n"
                "6. **Seed rates** — Use certified improved varieties from EIAR or regional institutes\n\n"
                "Ask about a specific crop (e.g. *'tips for Teff'*) for targeted advice!")

    # ── Default fallback ───────────────────────────────────────────────────
    return ("I'm not sure I understood that. 🤔\n\n"
            "Here are some things you can ask me:\n"
            "- *'Recommend a crop for my land'*\n"
            "- *'Tell me about Teff'*\n"
            "- *'What grows in Oromia?'*\n"
            "- *'Best crop for altitude 2000m'*\n"
            "- *'Farming tips'*\n\n"
            "Type **help** to see all options.")


def parse_params_from_message(msg):
    """Extract environmental parameters from natural language."""
    import re
    p = {}

    # Temperature
    m = re.search(r"temp(?:erature)?[:\s=]+([0-9.]+)", msg, re.I) or \
        re.search(r"([0-9.]+)\s*(?:degrees?|°c|celsius)", msg, re.I)
    if m: p["temperature"] = float(m.group(1))

    # Humidity
    m = re.search(r"humid(?:ity)?[:\s=]+([0-9.]+)", msg, re.I) or \
        re.search(r"([0-9.]+)\s*%\s+humid", msg, re.I)
    if m: p["humidity"] = float(m.group(1))

    # Rainfall
    m = re.search(r"rain(?:fall)?[:\s=]+([0-9.]+)", msg, re.I) or \
        re.search(r"([0-9.]+)\s*mm", msg, re.I)
    if m: p["rainfall"] = float(m.group(1))

    # pH
    m = re.search(r"ph[:\s=]+([0-9.]+)", msg, re.I) or \
        re.search(r"([0-9.]+)\s*ph", msg, re.I)
    if m: p["ph"] = float(m.group(1))

    # Altitude
    m = re.search(r"alt(?:itude)?[:\s=]+([0-9]+)", msg, re.I) or \
        re.search(r"([0-9]+)\s*m(?:asl|eters?)?(?:\s|$)", msg, re.I) or \
        re.search(r"([0-9]+)\s*(?:m\b|meters?\b)", msg, re.I)
    if m: p["altitude"] = float(m.group(1))

    # Nitrogen
    m = re.search(r"n(?:itrogen)?[:\s=]+([0-9.]+)", msg, re.I)
    if m: p["nitrogen"] = float(m.group(1))

    # Phosphorus
    m = re.search(r"p(?:hosphorus)?[:\s=]+([0-9.]+)", msg, re.I)
    if m: p["phosphorus"] = float(m.group(1))

    # Potassium
    m = re.search(r"k(?:potassium)?[:\s=]+([0-9.]+)", msg, re.I)
    if m: p["potassium"] = float(m.group(1))

    # Soil type
    for soil in ["clay", "loam", "sandy", "silty", "red soil", "black soil"]:
        if soil in msg.lower():
            p["soil_type"] = soil.title()
            break

    # Region
    for reg in ["oromia", "amhara", "tigray", "sidama", "snnpr", "afar", "somali", "benishangul"]:
        if reg in msg.lower():
            p["region"] = reg.title()
            break

    return p


REQUIRED_PARAMS = {
    "temperature": "🌡️ What is the average **temperature** (°C)?",
    "humidity":    "💧 What is the **humidity** (%)?",
    "rainfall":    "🌧️ What is the annual **rainfall** (mm)?",
    "ph":          "🧪 What is the **soil pH**? (typical range: 5.0–8.0)",
    "altitude":    "⛰️  What is the **altitude** of your farm (meters)?",
    "soil_type":   "🌍 What is the **soil type**?\n   Options: Clay / Loam / Sandy / Silty / Red Soil / Black Soil",
    "nitrogen":    "🌿 What is the **Nitrogen (N)** level in your soil? (kg/ha, e.g. 60–120)",
    "phosphorus":  "🌿 What is the **Phosphorus (P)** level? (kg/ha, e.g. 20–80)",
    "potassium":   "🌿 What is the **Potassium (K)** level? (kg/ha, e.g. 20–80)",
}


def ask_for_missing(session):
    """Ask for the next missing parameter."""
    for key, question in REQUIRED_PARAMS.items():
        if key not in session:
            collected = len([k for k in REQUIRED_PARAMS if k in session])
            total = len(REQUIRED_PARAMS)
            progress = "▓" * collected + "░" * (total - collected)
            return (f"[{progress}] {collected}/{total} collected\n\n"
                    f"{question}\n\n"
                    f"*(Type the value, e.g. **85** for humidity)*")
    # All collected — run prediction
    return run_full_recommendation(session)


def run_full_recommendation(params):
    """Build the full recommendation response."""
    # Fill defaults for optional params
    params.setdefault("nitrogen", 80)
    params.setdefault("phosphorus", 40)
    params.setdefault("potassium", 35)
    params.setdefault("soil_type", "Loam")
    params.setdefault("region", "Oromia")

    crop, confidence = predict_crop(params)
    altitude = params.get("altitude", 1500)

    if not crop or confidence < 0.45:
        # Use rule-based fallback
        crop, reason = altitude_based_recommendation(altitude)
        confidence_str = "rule-based"
        source = "📏 Rule-based altitude recommendation"
        advice_note = reason
    else:
        confidence_str = f"{confidence * 100:.1f}%"
        source = f"🤖 AI Model (confidence: {confidence_str})"
        advice_note = ""

    info = CROP_INFO.get(crop, {})
    zone = get_altitude_zone(altitude)

    lines = [
        f"## 🌾 Crop Recommendation Result",
        f"",
        f"**✅ Recommended Crop: {crop}**",
        f"**{source}**",
        f"",
        f"### 📊 Your Conditions",
        f"| Parameter | Value |",
        f"|-----------|-------|",
        f"| 🌡️ Temperature | {params.get('temperature', '?')}°C |",
        f"| 💧 Humidity | {params.get('humidity', '?')}% |",
        f"| 🌧️ Rainfall | {params.get('rainfall', '?')} mm/yr |",
        f"| 🧪 Soil pH | {params.get('ph', '?')} |",
        f"| ⛰️  Altitude | {altitude:.0f}m ({zone}) |",
        f"| 🌍 Soil Type | {params.get('soil_type', '?')} |",
        f"",
        f"### 🌱 About {crop}",
        f"{info.get('description', '')}",
        f"",
        f"### 📋 Optimal Conditions",
        f"- **Altitude:** {info.get('altitude', 'N/A')}",
        f"- **Rainfall:** {info.get('rainfall', 'N/A')}",
        f"- **Temperature:** {info.get('temperature', 'N/A')}",
        f"- **Soil:** {info.get('soil', 'N/A')}",
        f"",
        f"### 💡 Planting Tips",
        f"{info.get('planting_tips', '')}",
        f"",
        f"### ⏱️ Harvest",
        f"{info.get('harvest', 'N/A')}",
        f"",
    ]
    if advice_note:
        lines.append(f"*📍 {advice_note}*")
        lines.append("")

    lines.append("---")
    lines.append("Type *'recommend again'* for a new recommendation, or ask me about another crop!")

    return "\n".join(lines)


def format_crop_info(crop_name, info):
    """Format crop info as a chat message."""
    return (
        f"## 🌿 {crop_name}\n\n"
        f"{info['description']}\n\n"
        f"### 🌍 Growing Conditions\n"
        f"- **Altitude:** {info['altitude']}\n"
        f"- **Rainfall:** {info['rainfall']}\n"
        f"- **Temperature:** {info['temperature']}\n"
        f"- **Soil:** {info['soil']}\n"
        f"- **Fertilizer (NPK):** {info['npk']}\n\n"
        f"### 💡 Planting Tips\n{info['planting_tips']}\n\n"
        f"### ⏱️ Harvest Time\n{info['harvest']}\n\n"
        f"### 📍 Main Regions\n{', '.join(info['zones'])}\n\n"
        f"---\nWant a personalized recommendation? Say *'recommend a crop'*!"
    )


def get_altitude_zone(altitude):
    if altitude >= 3200: return "Afro-alpine"
    if altitude >= 2500: return "Upper Montane"
    if altitude >= 1800: return "Mid Montane"
    if altitude >= 1200: return "Lower Montane"
    return "Lowland"

# ─── API Routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the frontend."""
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chatbot endpoint."""
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    session_id = body.get("session_id", str(uuid.uuid4()))

    if not message:
        return jsonify({"error": "Empty message"}), 400

    try:
        reply = chatbot_reply(session_id, message)
        return jsonify({
            "reply": reply,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict", methods=["POST"])
def predict():
    """Direct ML prediction endpoint (for API consumers)."""
    body = request.get_json(silent=True) or {}
    required = ["temperature", "humidity", "rainfall", "ph", "altitude", "soil_type"]
    missing = [f for f in required if f not in body]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    body.setdefault("nitrogen", 80)
    body.setdefault("phosphorus", 40)
    body.setdefault("potassium", 35)
    body.setdefault("region", "Oromia")

    crop, confidence = predict_crop(body)
    if not crop:
        crop, reason = altitude_based_recommendation(body["altitude"])
        confidence = 0.0

    info = CROP_INFO.get(crop, {})
    return jsonify({
        "recommended_crop": crop,
        "confidence": f"{confidence * 100:.1f}%" if confidence else "rule-based",
        "advice": info.get("planting_tips", ""),
        "harvest": info.get("harvest", ""),
        "altitude_zone": get_altitude_zone(body["altitude"])
    })


@app.route("/api/crops", methods=["GET"])
def get_crops():
    """Return all supported crops with info."""
    return jsonify({
        "crops": [
            {"name": k, **{f: v for f, v in v.items() if f != "description"}, "description": v["description"]}
            for k, v in CROP_INFO.items()
        ]
    })


@app.route("/api/meta", methods=["GET"])
def get_meta():
    """Return model metadata."""
    return jsonify({
        "model_ready": ML_READY,
        "accuracy": META.get("accuracy"),
        "soil_types": META.get("soil_types", []),
        "regions": META.get("regions", []),
        "crops": list(CROP_INFO.keys())
    })


if __name__ == "__main__":
    print("\n🇪🇹  Ethiopian Crop Recommendation Chatbot")
    print("━" * 40)
    print(f"   ML Model: {'✅ Ready' if ML_READY else '❌ Not trained — run ml/train_model.py'}")
    print(f"   Model accuracy: {META.get('accuracy', 'N/A')}%")
    print("   Server: http://localhost:5000")
    print("━" * 40)
    app.run(debug=True, host="0.0.0.0", port=5000)
