import os
from datetime import datetime

import joblib
import pandas as pd

RULES_FILE = "location_rules.joblib"

# ─── Default model path ──────────────────────────────────────────
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "model",
    "displacement_model.joblib",
)


def load_model(model_path=None) -> object:
    """
    Load the saved displacement model bundle from disk.
    Call this ONCE when your API starts up.
    """
    if model_path is None:
        model_path = MODEL_PATH
    return joblib.load(model_path)


def _encode_safe(le, value):
    """Encode a value using a LabelEncoder, falling back to class 0 for unseen labels."""
    if value in le.classes_:
        return int(le.transform([value])[0])
    return int(le.transform([le.classes_[0]])[0])


def translate_to_model_input(model_bundle, conflict_event):
    """
    Translate a raw ACLED conflict event dict into a DataFrame
    of encoded features that the model expects.

    Returns
    -------
    pd.DataFrame — single-row DataFrame ready for model.predict()
    """
    label_encoders = model_bundle["label_encoders"]

    # ── Parse event date ──
    event_date_str = conflict_event.get("event_date", "")
    try:
        event_date = datetime.strptime(event_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            event_date = datetime.strptime(event_date_str[:10], "%Y-%m-%d")
        except ValueError:
            event_date = datetime.now()

    # ── Extract features from ACLED data ──
    origin_country = "SSD"
    origin_admin1 = conflict_event.get("admin1", "")
    direction = "Internal"
    reason = "Conflict Displacement"
    reason_subtype = "Insecurity Generalised Violence"
    month = event_date.month
    year = conflict_event.get("year", event_date.year)
    fatalities = conflict_event.get("fatalities", 0) or 0
    group_size = max(1, fatalities * 5)
    pct_children = model_bundle["median_pct_children"]
    pct_female = model_bundle["median_pct_female"]

    # ── Encode features ──
    input_data = {
        "origin_country": _encode_safe(
            label_encoders["origin_country"], origin_country
        ),
        "origin_admin1": _encode_safe(label_encoders["origin_admin1"], origin_admin1),
        "direction": _encode_safe(label_encoders["direction"], direction),
        "reason": _encode_safe(label_encoders["reason"], reason),
        "reason_subtype": _encode_safe(
            label_encoders["reason_subtype"], reason_subtype
        ),
        "month": int(month),
        "year": int(year),
        "group_size": int(group_size),
        "pct_children": float(pct_children),
        "pct_female": float(pct_female),
    }

    return pd.DataFrame([input_data])


def translate_prediction_to_response(
    model_bundle, conflict_event, prediction, prediction_proba, top_n=10
):
    """
    Translate raw model output back into a human-readable response dict.

    Parameters
    ----------
    model_bundle      : dict — loaded via load_model()
    conflict_event    : dict — original ACLED event
    prediction        : np.ndarray — model.predict() output
    prediction_proba  : np.ndarray — model.predict_proba()[0] output
    top_n             : int — number of top destinations (default 10)

    Returns
    -------
    dict — JSON-serializable response with prediction details
    """
    target_le = model_bundle["target_le"]
    town_to_state = model_bundle["town_to_state"]

    # ── Decode prediction ──
    predicted_town = str(target_le.inverse_transform(prediction)[0])
    predicted_state = town_to_state.get(predicted_town, "Unknown")
    predicted_idx = int(prediction[0])
    confidence = float(prediction_proba[predicted_idx])

    # ── Parse event date for response ──
    event_date_str = conflict_event.get("event_date", "")
    try:
        event_date = datetime.strptime(event_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            event_date = datetime.strptime(event_date_str[:10], "%Y-%m-%d")
        except ValueError:
            event_date = datetime.now()

    fatalities = conflict_event.get("fatalities", 0) or 0

    # ── Build top N destinations ──
    town_probs = list(zip(target_le.classes_, prediction_proba))
    town_probs.sort(key=lambda x: x[1], reverse=True)

    top_destinations = []
    for rank, (town, prob) in enumerate(town_probs[:top_n], start=1):
        top_destinations.append(
            {
                "rank": rank,
                "town": str(town),
                "state": town_to_state.get(str(town), "Unknown"),
                "probability": round(float(prob), 6),
            }
        )

    # ── Assemble result ──
    return {
        "conflict_event": {
            "event_id": conflict_event.get("event_id_cnty", ""),
            "event_date": event_date.strftime("%Y-%m-%d"),
            "location": conflict_event.get("location", ""),
            "admin1": conflict_event.get("admin1", ""),
            "admin2": conflict_event.get("admin2", ""),
            "country": conflict_event.get("country", ""),
            "latitude": float(conflict_event.get("latitude", 0)),
            "longitude": float(conflict_event.get("longitude", 0)),
            "fatalities": int(fatalities),
            "event_type": conflict_event.get("event_type", ""),
            "sub_event_type": conflict_event.get("sub_event_type", ""),
        },
        "prediction": {
            "predicted_town": predicted_town,
            "predicted_state": predicted_state,
            "confidence": round(confidence, 6),
        },
        "top_destinations": top_destinations,
        "model_metadata": {
            "model_type": "RandomForestClassifier",
            "n_estimators": 200,
            "max_depth": 25,
            "accuracy": round(float(model_bundle["accuracy"]), 6),
            "num_target_towns": model_bundle["num_target_towns"],
            "training_samples": model_bundle["training_samples"],
        },
        "input_features": {
            "origin_country": "SSD",
            "origin_admin1": conflict_event.get("admin1", ""),
            "direction": "Internal",
            "reason": "Conflict Displacement",
            "reason_subtype": "Insecurity Generalised Violence",
            "month": int(event_date.month),
            "year": int(conflict_event.get("year", event_date.year)),
            "group_size": int(max(1, fatalities * 5)),
            "pct_children": float(model_bundle["median_pct_children"]),
            "pct_female": float(model_bundle["median_pct_female"]),
        },
    }


# ─── Legacy functions (kept for backward compatibility) ───────────


def prepare_training_data(raw_events):
    df = pd.DataFrame(raw_events)

    unique_data = sorted(df["location"].unique().tolist())

    mapping = {town: i for i, town in enumerate(unique_data)}
    reverse_mapping = {i: town for town, i in mapping.items()}

    joblib.dump({"forward": mapping, "backward": reverse_mapping}, RULES_FILE)

    df["location_id"] = df["location"].map(mapping)

    return df[["location_id", "fatalities"]]


def get_prediction_town(predicted_data):
    if not os.path.exists(RULES_FILE):
        return "Rules file missing"

    rules = joblib.load(RULES_FILE)

    return rules["backward"].get(predicted_data, "Unknown Location")
