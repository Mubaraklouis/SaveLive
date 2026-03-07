import json
import traceback

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.translator_utils import (
    load_model,
    translate_to_model_input,
    translate_prediction_to_response,
)

# ─── Load model once at startup ──────────────────────────────────
print("Loading displacement model...")
model_bundle = load_model()
print(
    f"Model loaded — accuracy: {model_bundle['accuracy']:.4f}, "
    f"towns: {model_bundle['num_target_towns']}"
)


async def homepage(request):
    return JSONResponse({
        "service": "SaveLife AI Displacement Prediction",
        "status": "running",
        "model_accuracy": round(float(model_bundle["accuracy"]), 4),
        "num_target_towns": model_bundle["num_target_towns"],
    })


async def predict(request):
    """
    POST /predict
    Accepts a raw ACLED conflict event JSON body and returns
    a displacement prediction with top destination towns.
    """
    # ── Parse request body ──
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(
            {"error": "Invalid JSON in request body"},
            status_code=400,
        )

    if not isinstance(body, dict):
        return JSONResponse(
            {"error": "Request body must be a JSON object"},
            status_code=400,
        )

    # ── Translate input → model features ──
    try:
        input_df = translate_to_model_input(model_bundle, body)
    except Exception as e:
        return JSONResponse(
            {"error": f"Failed to translate input: {str(e)}"},
            status_code=400,
        )

    # ── Run prediction ──
    try:
        rf_model = model_bundle["model"]
        prediction = rf_model.predict(input_df)
        prediction_proba = rf_model.predict_proba(input_df)[0]
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            {"error": f"Model prediction failed: {str(e)}"},
            status_code=500,
        )

    # ── Translate prediction → human-readable response ──
    try:
        result = translate_prediction_to_response(
            model_bundle, body, prediction, prediction_proba
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            {"error": f"Failed to translate prediction: {str(e)}"},
            status_code=500,
        )

    return JSONResponse(result)


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/predict", predict, methods=["POST"]),
    ],
)