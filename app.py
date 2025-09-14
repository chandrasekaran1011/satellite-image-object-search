from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uuid
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
from ultralytics import YOLO
from contextlib import asynccontextmanager
from typing import List, Dict
import logging
# Dictionary to store pre-loaded YOLO models for faster inference
MODELS: Dict[str, YOLO] = {}

# Directory to save uploaded images
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Create directory if it doesn't exist

# ------------------------
# Lifespan: Startup & Shutdown
# ------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle tasks on app startup and shutdown:
    - Load YOLO models into memory at startup for faster inference.
    - Clean up models at shutdown to free memory.
    """
    # Paths to YOLO models
    model_paths = {
        "custom": "./best.pt",
        "yolo": "yolo11x.pt"
    }

    # Load all models into the MODELS dictionary
    for name, path in model_paths.items():
        try:
            MODELS[name] = YOLO(path)
        except Exception as e:
            print(f"Error loading model '{name}' from '{path}': {e}")
            raise e

    print("Models loaded:", list(MODELS.keys()))

    yield  # Application runs here

    # Cleanup at shutdown
    print("Cleaning up models...")
    MODELS.clear()


# ------------------------
# FastAPI app initialization
# ------------------------
app = FastAPI(
    title="Satellite Image Object Detection API",
    description="""
        API to detect objects in satellite images.
        Users can choose between a custom trained YOLO model or a pre-trained YOLO model.
        The API returns detected objects with class names, confidence scores, and bounding boxes.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS (Cross-Origin Resource Sharing) for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ------------------------
# API Endpoints
# ------------------------

@app.post("/detect", summary="Detect objects in an uploaded image")
async def detect(
    image: UploadFile = File(..., description="Satellite image file to detect objects in"),
    model_name: str = Form(..., description="YOLO model to use: 'custom' or 'yolo'")
):
    """
    Detect objects in the uploaded image using the selected YOLO model.
    Returns a JSON response with a list of detected objects.
    Each object contains:
    - class_name: Detected object class
    - bounding_box: [x_min, y_min, x_max, y_max]
    - confidence: Detection confidence (0-1)
    """
    # Validate model selection
    if model_name not in MODELS:
        raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found")

    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        # Save uploaded image
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # Run detection
        detections = detect_objects(model_name, str(file_path))
        return JSONResponse(content={"detections": detections})

    except Exception as e:
        logging.exception("Error during object detection")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    finally:
        # Cleanup uploaded file
        if file_path.exists():
            file_path.unlink()

@app.get("/", summary="Serve frontend HTML page")
def index():
    """
    Serve the frontend index.html file.
    """
    return FileResponse("app/static/index.html")


# ------------------------
# Utility Functions
# ------------------------
def detect_objects(model_name: str, image_path: str) -> List[Dict]:
    """
    Perform object detection on the given image using the specified YOLO model.

    Args:
        model_name (str): Name of the YOLO model ('custom' or 'yolo')
        image_path (str): Path to the image file

    Returns:
        List[Dict]: List of detected objects with class name, bounding box, and confidence
    """
    model = MODELS[model_name]
    results = model(image_path)  # Run inference
    detections = []

    for result in results:
        boxes = result.boxes
        class_ids = boxes.cls.cpu().numpy().astype(int)
        coords = boxes.xyxy.cpu().numpy()
        confidences = boxes.conf.cpu().numpy()

        for cls_id, box, conf in zip(class_ids, coords, confidences):
            class_name = model.names.get(cls_id, "unknown")
            x_min, y_min, x_max, y_max = box

            detections.append({
                "class_name": class_name,
                "bounding_box": [int(x_min), int(y_min), int(x_max), int(y_max)],
                "confidence": round(float(conf), 2)
            })

    return detections
