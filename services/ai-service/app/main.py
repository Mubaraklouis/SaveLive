from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from starlette.applications import Starlette
from functools import lru_cache
import contextlib




@lru_cache(maxsize=1) # Cache the result of this function
def get_model():
    print("Attempting to load model (lazy)...")
    try:
        # model = joblib.load("models/sentiment_model.pkl")
        model = {"model": "test"}
        print("Model loaded successfully.")
        return model
    except FileNotFoundError:
        print("Error: Model file not found during lazy load.")
        return None # Indicate failure
    except Exception as e:
        print(f"Error lazy loading model: {e}")
        return None


async def homepage(request: Request):
    return JSONResponse({"hello": "world"})


async def predict_event(request: Request):
    data = await request.body()
    print(data)
    result = get_model()
    print(result.get("model"))
    return JSONResponse({"result": "data received"})


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/api/predict", predict_event, methods=["POST"]),
    ],
)
