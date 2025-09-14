
# Satellite Image Object Detection

## Project Description

This project is a **Proof of Concept (PoC)** for detecting objects in satellite images using **YOLO models**.  
It allows users to upload satellite images, select a model (custom-trained YOLO or pre-trained YOLO), and visualize detected objects with bounding boxes and confidence scores.  

- **Frontend:** Vue 3 (Options API) + Bootstrap 5  
- **Backend:** FastAPI + Ultralytics YOLO  

---

## Features

- Upload and validate satellite images.
- Choose between a **custom YOLO model** or a **pre-trained YOLO model**.
- Visualize detected objects with:
  - Color-coded bounding boxes per object class.
  - Numbered circular badges.
  - Clickable object list to highlight corresponding objects in the image.
- API returns **JSON** with:
  - Object class
  - Bounding box coordinates
  - Confidence score
- Full **OpenAPI documentation** via FastAPI.

---

## Manual Setup (Local Development)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-project-directory>
```

### 2. Create a Python virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / MacOS:**
```bash
source venv/bin/activate
```

### 4. Install required Python packages

```bash
pip install -r requirements.txt
```

### 5. Run the FastAPI server

```bash
uvicorn app:app --reload
```

### 6. Access the application

Open your browser and navigate to:  
[http://localhost:8000](http://localhost:8000)  
FastAPI interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Docker Setup

You can run the Satellite Image Object Detection app using Docker. Follow the steps below:

### 1. Build the Docker image

From the project root (where the `Dockerfile` is), run:

```bash
docker build -t satellite-yolo-app .
```

### 2. Run the Docker container

```bash
docker run -d -p 8000:8000 --name satellite-yolo satellite-yolo-app
```

- `-d` → run in detached mode (background)  
- `-p 8000:8000` → map container port 8000 to host  
- `--name satellite-yolo` → optional container name

### 3. Access the application

Open your browser:

```
http://localhost:8000
```

FastAPI interactive docs:

```
http://localhost:8000/docs
```

### 4. Stop and remove the container

```bash
docker stop satellite-yolo
docker rm satellite-yolo
```

### 5. Optional: Run with GPU support

If you have an NVIDIA GPU and the NVIDIA Container Toolkit installed:

```bash
docker run -d -p 8000:8000 --gpus all --name satellite-yolo satellite-yolo-app
```

YOLO will use the GPU for faster inference.
