import asyncio
import json
import traceback
from functools import lru_cache

from sse_starlette import EventSourceResponse
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.translator_utils import (
    load_model,
    translate_prediction_to_response,
    translate_to_model_input,
)

subscribers = []


async def event_generator(queue):
    while True:
        message = await queue.get()
        yield f"data: {message}\n\n"


@lru_cache(maxsize=1)  # Cache the result of this function
def get_model():
    print("Attempting to load model (lazy)...")
    try:
        # ───----------- Load model once at startup ────────────
        print("Loading displacement model...")
        model_bundle = load_model()
        print(
            f"Model loaded — accuracy: {model_bundle['accuracy']:.4f}, "
            f"towns: {model_bundle['num_target_towns']}"
        )
        return model_bundle
    except FileNotFoundError:
        print("Error: Model file not found during lazy load.")
        return None  # Indicate failure
    except Exception as e:
        print(f"Error lazy loading model: {e}")
        return None


async def homepage(request: Request):
    model_bundle = get_model()
    return JSONResponse(
        {
            "service": "SaveLife AI Displacement Prediction",
            "status": "running",
            "model_accuracy": round(float(model_bundle["accuracy"]), 4),
            "num_target_towns": model_bundle["num_target_towns"],
        }
    )


async def predict(request: Request):
    """
    POST /predict
    Accepts a raw ACLED conflict event JSON body and returns
    a displacement prediction with top destination towns.
    """
    # ── Parse request body ──
    model_bundle = get_model()
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
    for q in subscribers:
        await q.put(f"Prediction result: {result}")

    return JSONResponse(result)


async def events(request: Request):
    queue = asyncio.Queue()
    subscribers.append(queue)
    # return StreamingResponse(event_generator(queue), media_type="text/event-stream")
    return EventSourceResponse(event_generator(queue))


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/predict", predict, methods=["POST"]),
        Route("/broadcast/events", events),
    ],
)
