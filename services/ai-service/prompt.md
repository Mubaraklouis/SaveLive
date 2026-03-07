
this was the script i used to load the displacement_model.joblib but now i want to be able to use the translator_utils.py to able able to translate i want to accept a post request with data example 

{
  "id": 2,
  "event_id_cnty": "SSD-2026-02-22-0001",
  "event_date": "2026-02-22T00:00:00.000Z",
  "year": 2026,
  "time_precision": 1,
  "disorder_type": "Political violence",
  "event_type": "Violence against civilians",
  "sub_event_type": "Attack",
  "actor1": "Unidentified armed group",
  "assoc_actor_1": null,
  "inter1": null,
  "actor2": "Civilians (South Sudan)",
  "assoc_actor_2": null,
  "inter2": null,
  "interaction": "Other vs Civilians",
  "civilian_targeting": "Civilian targeting",
  "iso": 728,
  "region": "Eastern Africa",
  "country": "South Sudan",
  "admin1": "Western Equatoria",
  "admin2": "Yambio",
  "admin3": null,
  "location": "Yambio",
  "latitude": "4.570000",
  "longitude": "28.390000",
  "geo_precision": 1,
  "source": "ACLED",
  "source_scale": "National",
  "notes": "Isolated attack on civilians in Yambio; 1 fatality reported.",
  "fatalities": 1,
  "tags": null,
  "timestamp": "1740182400",
  "created_at": "2026-03-06T10:57:24.596Z",
  "updated_at": "2026-03-06T10:57:24.596Z"
}

and pass the body to a function build that already exist in main the function accepts the body translate it using the tranlator and the translattor accepts that data and load the train model and pass the data for prediction use the other translator to translate the predicted data back to human readable format and return the result as the api 

"""
Displacement Prediction Loader
===============================
Loads the joblib-saved model bundle and exposes a predict function
that accepts raw ACLED conflict event data and returns numerical data
as a Python dict — ready for json.dumps().

Usage in your API:
    from predict import load_model, predict_displacement

    model_bundle = load_model()  # call once at startup

    # Per request — pass the raw ACLED event dict:
    result = predict_displacement(model_bundle, acled_event_dict)
    return jsonify(result)  # or json.dumps(result)
"""

import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import os


def load_model(model_path=None):
    """
    Load the saved model bundle from disk.
    Call this ONCE when your API starts up.
    """
    if model_path is None:
        model_path = os.path.join(
            os.path.dirname(os.path.abspath(_file_)),
            "model", "displacement_model.joblib"
        )
    return joblib.load(model_path)


def _encode_safe(le, value):
    """Encode a value, falling back to class 0 for unseen labels."""
    if value in le.classes_:
        return int(le.transform([value])[0])
    return int(le.transform([le.classes_[0]])[0])


def predict_displacement(model_bundle, conflict_event, top_n=10):
    """
    Given the loaded model bundle and a raw ACLED conflict event dict,
    return a plain Python dict with numerical prediction data.

    Parameters
    ----------
    model_bundle   : dict — loaded via load_model()
    conflict_event : dict — raw ACLED conflict event JSON
    top_n          : int  — number of top destinations to return (default 10)

    Returns
    -------
    dict — all values are JSON-serializable (int, float, str, list, dict)
    """
    rf_model = model_bundle["model"]
    label_encoders = model_bundle["label_encoders"]
    target_le = model_bundle["target_le"]
    town_to_state = model_bundle["town_to_state"]

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
        "origin_country": _encode_safe(label_encoders["origin_country"], origin_country),
        "origin_admin1": _encode_safe(label_encoders["origin_admin1"], origin_admin1),
        "direction": _encode_safe(label_encoders["direction"], direction),
        "reason": _encode_safe(label_encoders["reason"], reason),
        "reason_subtype": _encode_safe(label_encoders["reason_subtype"], reason_subtype),
        "month": int(month),
        "year": int(year),
        "group_size": int(group_size),
        "pct_children": float(pct_children),
        "pct_female": float(pct_female),
    }

    input_df = pd.DataFrame([input_data])

    # ── Predict ──
    prediction = rf_model.predict(input_df)
    prediction_proba = rf_model.predict_proba(input_df)[0]

    predicted_town = str(target_le.inverse_transform(prediction)[0])
    predicted_state = town_to_state.get(predicted_town, "Unknown")
    predicted_idx = int(prediction[0])
    confidence = float(prediction_proba[predicted_idx])

    # ── Build top N destinations ──
    town_probs = list(zip(target_le.classes_, prediction_proba))
    town_probs.sort(key=lambda x: x[1], reverse=True)

    top_destinations = []
    for rank, (town, prob) in enumerate(town_probs[:top_n], start=1):
        top_destinations.append({
            "rank": rank,
            "town": str(town),
            "state": town_to_state.get(str(town), "Unknown"),
            "probability": round(float(prob), 6),
        })

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
            "origin_country": origin_country,
            "origin_admin1": origin_admin1,
            "direction": direction,
            "reason": reason,
            "reason_subtype": reason_subtype,
            "month": int(month),
            "year": int(year),
            "group_size": int(group_size),
            "pct_children": float(pct_children),
            "pct_female": float(pct_female),
        },
    }


# ─── Standalone: accept raw ACLED JSON ────────────────────────────

if _name_ == "_main_":
    import json
    import sys

    print("Loading model from joblib...")
    bundle = load_model()
    print(f"Model loaded — accuracy: {bundle['accuracy']:.4f}, towns: {bundle['num_target_towns']}")

    # Accept ACLED JSON from:
    #   1) Command line argument:  python predict.py '{"admin1":"Jonglei", ...}'
    #   2) Stdin (pipe):           echo '{"admin1":"Jonglei", ...}' | python predict.py
    #   3) No input:               uses a built-in sample event

    acled_json = None

    if len(sys.argv) > 1:
        # From command line argument
        acled_json = sys.argv[1]
    elif not sys.stdin.isatty():
        # From stdin (piped input)
        acled_json = sys.stdin.read()

    if acled_json:
        event = json.loads(acled_json)
        print(f"\nUsing provided ACLED event data")
    else:
        # Default sample event
        event = {
            "event_id_cnty": "SSD-2026-02-25-0001",
            "event_date": "2026-02-25T00:00:00.000Z",
            "year": 2026,
            "event_type": "Battles",
            "sub_event_type": "Armed clash",
            "country": "South Sudan",
            "admin1": "Jonglei",
            "admin2": "Bor South",
            "location": "Bor",
            "latitude": "6.210000",
            "longitude": "31.560000",
            "fatalities": 25,
        }
        print(f"\nNo input provided — using sample event")

    print("Running prediction...\n")
    result = predict_displacement(bundle, event, top_n=10)
    print(json.dumps(result, indent=2))