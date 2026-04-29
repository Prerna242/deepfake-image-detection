# DEEPFAKE IMAGE DETECTION SYSTEM — COMPLETE PROJECT BLUEPRINT
### The Holy Grail Document — Everything from Zero to Deployment

---

## TABLE OF CONTENTS

1. [Project Philosophy & What We're Actually Building](#1-project-philosophy)
2. [Do We Need an Orchestrator? (LangChain / LangGraph)](#2-orchestrator-decision)
3. [Final Tech Stack — Locked In](#3-final-tech-stack)
4. [Complete Directory Structure](#4-directory-structure)
5. [Phase 0 — Environment Setup](#5-environment-setup)
6. [Phase 1 — The ML Model (Start Here, Always)](#6-ml-model)
7. [Phase 2 — The FastAPI Backend](#7-fastapi-backend)
8. [Phase 3 — MongoDB Schema & Motor Integration](#8-mongodb)
9. [Phase 4 — JWT Authentication](#9-jwt-auth)
10. [Phase 5 — React Frontend](#10-react-frontend)
11. [End-to-End Data Flow Diagrams](#11-data-flow)
12. [Library Reference — Every Package Used](#12-library-reference)
13. [Running the Full Project](#13-running-the-project)
14. [Common Pitfalls & How to Avoid Them](#14-pitfalls)

---

## 1. PROJECT PHILOSOPHY

### What Are We Actually Building?

At its absolute core, this is a **binary image classification system with a web interface**. The entire system does one thing: it takes an image as input and outputs a verdict — "REAL" or "FAKE" — along with a confidence score (e.g., 92.4% fake).

Every other piece — the React frontend, the FastAPI routes, the MongoDB database, the JWT auth — exists purely to wrap that core in a usable product. Never lose sight of this. If the model doesn't work, nothing else matters.

### The Mental Model (Read This Carefully)

Think of the project in three layers that talk to each other in a specific sequence:

```
User uploads image on React UI
        ↓ (Axios HTTP POST with JWT)
FastAPI receives the image
        ↓ (OpenCV preprocesses it)
TensorFlow model runs inference
        ↓ (returns probability: 0.0 to 1.0)
FastAPI saves result to MongoDB
        ↓ (returns JSON response)
React displays REAL/FAKE + confidence score
```

That's the entire system. Everything you build must serve this pipeline.

### Scope — What We Are NOT Building

To keep this project focused and working:
- No real-time video deepfake detection (only static image uploads)
- No admin panel
- No email verification
- No OAuth (plain JWT only)
- No cloud image storage (local filesystem for uploads)
- No Docker for now (just run locally)
- No WebSockets or streaming results

---

## 2. ORCHESTRATOR DECISION

### Do We Need LangChain, LangGraph, or Any Orchestrator?

**No. Absolutely not. Do not add any of these.**

Here is why: LangChain and LangGraph are tools designed for orchestrating **Large Language Model (LLM) pipelines** — chains of prompts, agents that decide what tool to call next, retrieval-augmented generation, etc. None of that applies here.

What we are doing is straightforward **ML inference**: preprocess an image → run it through a neural network → get a number back. This is a direct function call. There is no chain of LLM decisions, no tool-use, no retrieval step. Adding LangChain here would be like using a freight train to cross the street — it introduces massive unnecessary complexity for zero benefit.

Your inference pipeline in Python is literally this:

```python
# This is your entire "orchestration"
image = preprocess(raw_image)        # OpenCV
prediction = model.predict(image)    # TensorFlow
result = "FAKE" if prediction > 0.5 else "REAL"
```

That's it. No orchestrator needed.

---

## 3. FINAL TECH STACK — LOCKED IN

### Frontend
- **React 18** (via Create React App or Vite — use Vite, it's faster)
- **Tailwind CSS 3** for all styling
- **Axios** for HTTP requests to the backend
- **React Router v6** for page navigation (Login, Dashboard, History)
- **React Hook Form** for form handling (login/register forms)

### Backend
- **Python 3.10+**
- **FastAPI** — web framework
- **Uvicorn** — ASGI server to run FastAPI
- **Motor** — async MongoDB driver (works natively with FastAPI's async model)
- **python-jose[cryptography]** — for creating and verifying JWT tokens
- **passlib[bcrypt]** — for hashing and verifying passwords
- **python-multipart** — required by FastAPI to accept file uploads
- **python-dotenv** — to load `.env` environment variables
- **Pillow (PIL)** — for basic image reading/format validation before OpenCV

### ML / AI Layer
- **TensorFlow 2.x** (includes Keras built-in as `tf.keras`)
- **OpenCV (cv2)** — image preprocessing (resize, normalize, face crop)
- **NumPy** — array manipulation between OpenCV and TensorFlow
- **EfficientNetB0** — pretrained base model (built into `tf.keras.applications`)

### Database
- **MongoDB Atlas** (Free M0 tier — 512MB, completely free forever)
- **Motor 3.x** — async Python driver for MongoDB

### Dataset (Free)
- **FaceForensics++ subset** from Kaggle — or use the Kaggle DFDC (DeepFake Detection Challenge) dataset. Both are free with a Kaggle account.
- Alternatively: search Kaggle for "deepfake detection dataset" — there are several good ones with pre-split real/fake folders.

---

## 4. COMPLETE DIRECTORY STRUCTURE

Below is the **exact** directory structure you will create. Every file is intentional. Read the comment next to each one so you understand its purpose before creating it.

```
deepfake-detector/                      ← Root project folder
│
├── backend/                            ← Everything Python/FastAPI lives here
│   ├── app/                            ← The actual FastAPI application package
│   │   ├── __init__.py                 ← Makes 'app' a Python package (can be empty)
│   │   ├── main.py                     ← FastAPI app creation, CORS, startup events, router mounting
│   │   ├── config.py                   ← Reads .env values, exposes Settings object
│   │   │
│   │   ├── routes/                     ← All API route handlers grouped by feature
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 ← /api/auth/register, /api/auth/login
│   │   │   └── detection.py            ← /api/detect (POST), /api/history (GET)
│   │   │
│   │   ├── models/                     ← Pydantic models (request/response schemas)
│   │   │   ├── __init__.py
│   │   │   ├── user.py                 ← UserCreate, UserLogin, UserResponse schemas
│   │   │   └── scan.py                 ← ScanResult, ScanHistory schemas
│   │   │
│   │   ├── services/                   ← Business logic, separated from routes
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py         ← Register user, verify login, hash password
│   │   │   ├── detection_service.py    ← Preprocess image, run model, return result
│   │   │   └── history_service.py      ← Save scan to DB, fetch user history
│   │   │
│   │   ├── db/                         ← Database connection and collection accessors
│   │   │   ├── __init__.py
│   │   │   └── mongo.py                ← Motor client setup, get_database() function
│   │   │
│   │   ├── middleware/                 ← Custom middleware (JWT verification)
│   │   │   ├── __init__.py
│   │   │   └── auth_middleware.py      ← get_current_user() dependency for protected routes
│   │   │
│   │   └── ml/                         ← Everything ML related
│   │       ├── __init__.py
│   │       ├── model_loader.py         ← Load .h5 model once at startup, expose predict()
│   │       └── preprocessor.py         ← OpenCV face crop, resize, normalize
│   │
│   ├── ml_training/                    ← Standalone scripts — NOT part of the FastAPI app
│   │   ├── train.py                    ← Full training script: load data, build model, train, save
│   │   ├── evaluate.py                 ← Load saved model, run on test set, print accuracy
│   │   └── dataset_prep.py             ← Script to organize downloaded dataset into correct folders
│   │
│   ├── uploads/                        ← Uploaded images saved here temporarily
│   │   └── .gitkeep                    ← Empty file so Git tracks this folder
│   │
│   ├── saved_model/                    ← Your trained .h5 model file goes here
│   │   └── .gitkeep
│   │
│   ├── requirements.txt                ← All Python dependencies with pinned versions
│   └── .env                            ← Secret keys, MongoDB URI — NEVER commit this
│
├── frontend/                           ← Everything React lives here
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.jsx                    ← Vite entry point, renders <App />
│   │   ├── App.jsx                     ← React Router setup, route definitions
│   │   │
│   │   ├── api/
│   │   │   └── axiosInstance.js        ← Axios with base URL + JWT interceptor
│   │   │
│   │   ├── pages/                      ← Top-level page components (one per route)
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardPage.jsx       ← Upload image, show result
│   │   │   └── HistoryPage.jsx         ← User's past scans
│   │   │
│   │   ├── components/                 ← Reusable UI pieces used across pages
│   │   │   ├── Navbar.jsx
│   │   │   ├── ImageUploader.jsx       ← Drag-and-drop + file picker component
│   │   │   ├── ResultCard.jsx          ← Shows REAL/FAKE with confidence bar
│   │   │   ├── ScanHistoryTable.jsx    ← Table for history page
│   │   │   ├── ProtectedRoute.jsx      ← Wrapper that redirects if not logged in
│   │   │   └── LoadingSpinner.jsx
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.jsx         ← Global auth state (token, user, login/logout)
│   │   │
│   │   └── hooks/
│   │       └── useAuth.js              ← useContext(AuthContext) shorthand hook
│   │
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
│
├── dataset/                            ← Raw downloaded dataset lives here
│   ├── real/                           ← Real face images
│   └── fake/                           ← Deepfake images
│
└── README.md
```

---

## 5. ENVIRONMENT SETUP

### Step 5.1 — Python Virtual Environment

Always use a virtual environment. This isolates your project's dependencies from your system Python.

```bash
# Go to the backend folder
cd deepfake-detector/backend

# Create virtual environment named 'venv'
python -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# You'll see (venv) in your terminal prompt — this means it's active
```

### Step 5.2 — requirements.txt (Backend)

Create this file in the `backend/` folder with exactly these contents. These versions are stable and compatible with each other.

```txt
fastapi==0.111.0
uvicorn[standard]==0.29.0
motor==3.4.0
pymongo==4.7.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
python-dotenv==1.0.1
Pillow==10.3.0
opencv-python-headless==4.9.0.80
numpy==1.26.4
tensorflow==2.16.1
```

**Important note on `opencv-python-headless`:** Use the "headless" version on a server/backend. The regular `opencv-python` requires a display (GUI libraries) which causes errors in server environments. Headless works fine for all image processing tasks.

Install everything:

```bash
pip install -r requirements.txt
```

### Step 5.3 — .env File

Create `backend/.env`. This file must **never** be committed to Git. Add it to `.gitignore` immediately.

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=deepfake_db
JWT_SECRET_KEY=your_very_long_random_secret_key_here_make_it_at_least_32_chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
MODEL_PATH=saved_model/efficientnet_deepfake.h5
UPLOAD_DIR=uploads
```

To generate a strong JWT secret key, run this in Python:
```python
import secrets
print(secrets.token_hex(32))
# Outputs something like: a3f8b2c9d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2
```

### Step 5.4 — MongoDB Atlas Setup (Free)

1. Go to https://www.mongodb.com/cloud/atlas/register and create a free account.
2. Click "Build a Database" → Select "M0 Free" tier → choose any cloud region.
3. Create a username and password — save these, they go into your `MONGO_URI`.
4. In "Network Access", click "Add IP Address" → "Allow Access from Anywhere" (0.0.0.0/0) during development. This is fine for a minor project.
5. Click "Connect" on your cluster → "Connect your application" → Copy the connection string. Replace `<password>` with your actual password. This is your `MONGO_URI`.

### Step 5.5 — Frontend Setup (Vite + React + Tailwind)

```bash
# From the root project folder
npm create vite@latest frontend -- --template react

cd frontend

# Install all dependencies
npm install

# Install Tailwind CSS and its peer dependencies
npm install -D tailwindcss postcss autoprefixer

# Initialize Tailwind
npx tailwindcss init -p

# Install Axios and React Router
npm install axios react-router-dom

# Install React Hook Form
npm install react-hook-form
```

After `npx tailwindcss init -p`, edit `tailwind.config.js` to tell Tailwind which files to scan:

```js
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",  // Scan all React files for class names
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Then edit `src/index.css` to include Tailwind's base styles (replace all existing content):

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## 6. ML MODEL — BUILD THIS FIRST

**Do not touch FastAPI or React until this works.** This is the soul of your project.

### Step 6.1 — Understanding Transfer Learning (Conceptually)

EfficientNetB0 is a convolutional neural network trained by Google on ImageNet — a dataset of 1.2 million images across 1000 categories. In doing so, it learned incredibly rich feature representations: edges, textures, shapes, patterns, anomalies in pixel patterns. These learned features happen to be extremely useful for detecting deepfakes, which often have subtle texture inconsistencies, unnatural blending at face boundaries, and frequency-domain artifacts.

What you are doing is: take the EfficientNetB0 "body" (all the layers that extract features), freeze its weights (don't retrain them — they're already good), and attach a new "head" (two or three Dense layers + a final Sigmoid output) that learns to classify those features as REAL or FAKE. You only train the new head on your deepfake dataset. This requires far less data and compute than training from scratch.

### Step 6.2 — Getting the Dataset

Go to Kaggle (https://www.kaggle.com) and download one of these:
- **"Deepfake and Real Images"** by `manjilkarki` — small, clean, already split into real/fake folders. Perfect for a minor project.
- **"140k Real and Fake Faces"** — larger, more robust.

Once downloaded, organize your dataset folder like this:

```
dataset/
├── train/
│   ├── real/       ← ~2000-3000 real face images
│   └── fake/       ← ~2000-3000 deepfake images
├── validation/
│   ├── real/       ← ~400-600 real images
│   └── fake/       ← ~400-600 fake images
└── test/
    ├── real/       ← ~200-300 real images
    └── fake/       ← ~200-300 fake images
```

The `dataset_prep.py` script in `ml_training/` can help you automate this split from a raw folder.

### Step 6.3 — dataset_prep.py

This script takes your raw downloaded dataset (which might just be a flat folder of images) and splits it into train/validation/test. Write this first.

```python
# backend/ml_training/dataset_prep.py

import os
import shutil
import random

# CONFIGURATION — edit these paths to match where your downloaded data is
RAW_REAL_DIR = "../../dataset/raw/real"       # Your real images here
RAW_FAKE_DIR = "../../dataset/raw/fake"       # Your fake images here
OUTPUT_DIR   = "../../dataset"

TRAIN_RATIO  = 0.75   # 75% of data goes to training
VAL_RATIO    = 0.15   # 15% for validation
TEST_RATIO   = 0.10   # 10% for final testing

def split_and_copy(source_dir, label, output_dir):
    """
    Takes all images from source_dir, shuffles them randomly,
    and copies them into train/val/test subfolders under output_dir.
    label is either 'real' or 'fake'.
    """
    all_images = [f for f in os.listdir(source_dir)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    random.shuffle(all_images)

    n = len(all_images)
    train_end = int(n * TRAIN_RATIO)
    val_end   = train_end + int(n * VAL_RATIO)

    splits = {
        "train":      all_images[:train_end],
        "validation": all_images[train_end:val_end],
        "test":       all_images[val_end:]
    }

    for split_name, files in splits.items():
        dest = os.path.join(output_dir, split_name, label)
        os.makedirs(dest, exist_ok=True)
        for filename in files:
            shutil.copy(os.path.join(source_dir, filename),
                        os.path.join(dest, filename))
        print(f"Copied {len(files)} images to {dest}")

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    split_and_copy(RAW_REAL_DIR, "real", OUTPUT_DIR)
    split_and_copy(RAW_FAKE_DIR, "fake", OUTPUT_DIR)
    print("Dataset preparation complete.")
```

Run it once: `python backend/ml_training/dataset_prep.py`

### Step 6.4 — train.py (The Training Script)

This is the most important file in the project. Read every comment carefully.

```python
# backend/ml_training/train.py

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

IMG_SIZE    = 224      # EfficientNetB0 expects 224x224 input
BATCH_SIZE  = 32       # How many images per training step; lower if you run out of RAM
EPOCHS      = 20       # Maximum training epochs; EarlyStopping will stop earlier if needed
DATASET_DIR = "../../dataset"
OUTPUT_PATH = "../saved_model/efficientnet_deepfake.h5"

# ─── DATA GENERATORS ──────────────────────────────────────────────────────────
# ImageDataGenerator handles loading images from folders AND augmentation.
# Augmentation = randomly flip, rotate, zoom images during training.
# This artificially multiplies your training data and prevents overfitting.

train_datagen = ImageDataGenerator(
    rescale=1.0/255.0,            # Normalize pixel values from [0,255] to [0,1]
    horizontal_flip=True,          # Randomly mirror images left-right
    rotation_range=10,             # Randomly rotate up to 10 degrees
    zoom_range=0.1,                # Randomly zoom in/out by 10%
    width_shift_range=0.1,         # Randomly shift horizontally
    height_shift_range=0.1,        # Randomly shift vertically
)

# Validation and test sets: ONLY rescale, no augmentation.
# We want to evaluate on unmodified images to get accurate metrics.
val_test_datagen = ImageDataGenerator(rescale=1.0/255.0)

# flow_from_directory scans the folder structure and automatically assigns labels.
# class_mode='binary' means it will output 0 or 1 per image (perfect for real vs fake).
# It alphabetically assigns class indices: 'fake'=0, 'real'=1
train_gen = train_datagen.flow_from_directory(
    os.path.join(DATASET_DIR, "train"),
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary"
)

val_gen = val_test_datagen.flow_from_directory(
    os.path.join(DATASET_DIR, "validation"),
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary"
)

# ─── BUILD THE MODEL ──────────────────────────────────────────────────────────

# Load EfficientNetB0 with ImageNet weights, but WITHOUT the top classification layers.
# include_top=False means we keep only the feature extraction part.
# input_shape must match (IMG_SIZE, IMG_SIZE, 3) — height, width, RGB channels
base_model = EfficientNetB0(
    weights="imagenet",
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# FREEZE the base model weights. We don't want to change what ImageNet already taught it.
# If you don't freeze, gradient updates would corrupt those carefully trained weights.
base_model.trainable = False

# Build the full model by stacking layers on top of the base model
inputs  = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x       = base_model(inputs, training=False)  # training=False keeps BatchNorm in inference mode
x       = layers.GlobalAveragePooling2D()(x)  # Reduces spatial dimensions to a flat vector
x       = layers.Dense(256, activation="relu")(x)  # Fully connected layer for classification
x       = layers.Dropout(0.4)(x)                   # Dropout: randomly zeroes 40% of neurons during training to prevent overfitting
outputs = layers.Dense(1, activation="sigmoid")(x) # Final output: single value 0-1 (probability of being fake)

model = models.Model(inputs, outputs)

# ─── COMPILE ──────────────────────────────────────────────────────────────────
# Binary crossentropy is the correct loss for binary classification.
# Adam optimizer with a small learning rate is standard for fine-tuning.
# metrics=['accuracy'] tracks accuracy during training.
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

print(model.summary())

# ─── CALLBACKS ────────────────────────────────────────────────────────────────
# Callbacks are functions that run at specific points during training.

# EarlyStopping: stop training if val_loss doesn't improve for 5 consecutive epochs.
# restore_best_weights=True means it keeps the weights from the best epoch, not the last.
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True,
    verbose=1
)

# ModelCheckpoint: save the model whenever val_accuracy improves.
# This ensures you never lose your best model even if training continues.
checkpoint = ModelCheckpoint(
    filepath=OUTPUT_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)

# ReduceLROnPlateau: if val_loss stops improving, reduce learning rate by 50%.
# This helps the model escape plateaus and fine-tune more carefully.
reduce_lr = ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.5,
    patience=3,
    verbose=1
)

# ─── TRAIN ────────────────────────────────────────────────────────────────────
print("\n=== PHASE 1: Training the classification head (base frozen) ===\n")

history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=[early_stop, checkpoint, reduce_lr]
)

# ─── FINE-TUNING PHASE (Optional but improves accuracy) ──────────────────────
# After the classification head has learned, unfreeze the TOP layers of the base model
# and train the whole thing at a very low learning rate. This allows the model
# to fine-tune its feature extraction specifically for deepfake detection.

print("\n=== PHASE 2: Fine-tuning top layers of base model ===\n")

# Unfreeze the entire base model
base_model.trainable = True

# But freeze everything EXCEPT the last 20 layers
for layer in base_model.layers[:-20]:
    layer.trainable = False

# Recompile at a much lower learning rate to avoid destroying existing weights
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

fine_tune_history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=10,  # Fewer epochs for fine-tuning
    callbacks=[early_stop, checkpoint, reduce_lr]
)

print(f"\nModel saved to: {OUTPUT_PATH}")
print("Training complete.")
```

Run training: `python backend/ml_training/train.py`

**What to expect:** On a decent CPU, Phase 1 might take 20-40 minutes depending on dataset size. If you have a GPU, it will be much faster. On a 5000-image dataset, expect 80-88% validation accuracy from Phase 1 alone. Fine-tuning may push it to 88-93%.

### Step 6.5 — evaluate.py

After training, always evaluate on the held-out test set to see real-world performance.

```python
# backend/ml_training/evaluate.py

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

MODEL_PATH  = "../saved_model/efficientnet_deepfake.h5"
TEST_DIR    = "../../dataset/test"
IMG_SIZE    = 224
BATCH_SIZE  = 32

model = tf.keras.models.load_model(MODEL_PATH)

test_datagen = ImageDataGenerator(rescale=1.0/255.0)
test_gen = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False  # Don't shuffle so predictions align with filenames
)

loss, accuracy = model.evaluate(test_gen)
print(f"\nTest Loss:     {loss:.4f}")
print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

# Class mapping (so you know which index = real, which = fake)
print("\nClass indices:", test_gen.class_indices)
# Expected output: {'fake': 0, 'real': 1}
# This means: model output close to 0 = fake, close to 1 = real
# BUT WAIT — you need to decide your convention. See note in detection_service.py.
```

### Step 6.6 — preprocessor.py (Inside the App)

This file lives inside `backend/app/ml/` and is used at inference time (when a user uploads an image). It must match exactly how you preprocessed images during training.

```python
# backend/app/ml/preprocessor.py

import cv2
import numpy as np
from PIL import Image
import io

IMG_SIZE = 224  # Must match training size

def load_and_validate_image(file_bytes: bytes) -> np.ndarray:
    """
    Takes raw bytes from the uploaded file, decodes it into a NumPy array.
    Raises ValueError if the bytes don't represent a valid image.
    This is your first line of defense against bad uploads.
    """
    try:
        # Convert raw bytes to a PIL Image first for format validation
        pil_image = Image.open(io.BytesIO(file_bytes))

        # Convert to RGB — important because PNG images can be RGBA (4 channels)
        # and some images might be grayscale. We always need 3 channels (RGB) for EfficientNet.
        pil_image = pil_image.convert("RGB")

        # Convert PIL → NumPy → OpenCV format
        # PIL uses RGB, but OpenCV uses BGR. Convert for OpenCV processing.
        img_array = np.array(pil_image)
        img_bgr   = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        return img_bgr

    except Exception:
        raise ValueError("Invalid image file. Please upload a JPG, PNG, or WEBP image.")


def detect_and_crop_face(img_bgr: np.ndarray) -> np.ndarray:
    """
    Tries to detect a face in the image and crop to it.
    If no face is found, returns the original image (we still classify it).
    
    Why crop to face? Deepfakes are facial manipulations. By focusing on the face,
    the model isn't distracted by background content. This significantly improves accuracy.
    """
    # Load OpenCV's pre-trained Haar Cascade face detector
    # This file is bundled with OpenCV — no separate download needed
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # detectMultiScale returns a list of (x, y, width, height) for each face found
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,     # How much to scale down the image each pass (1.1 = 10% reduction)
        minNeighbors=5,       # How many overlapping detections are needed to confirm a face
        minSize=(60, 60)      # Minimum face size in pixels (ignores tiny detections)
    )

    if len(faces) > 0:
        # Take the largest face (most likely the main subject)
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])  # Maximize width*height

        # Add a small margin around the face (15% of face size on each side)
        margin = int(0.15 * max(w, h))
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(img_bgr.shape[1], x + w + margin)
        y2 = min(img_bgr.shape[0], y + h + margin)

        face_crop = img_bgr[y1:y2, x1:x2]
        return face_crop

    # No face detected — return full image, model will still attempt classification
    return img_bgr


def preprocess_for_model(img_bgr: np.ndarray) -> np.ndarray:
    """
    Final preprocessing step: resize to model input size and normalize pixel values.
    This MUST match what was done during training exactly.
    """
    # Resize to 224x224 (EfficientNetB0 input size)
    img_resized = cv2.resize(img_bgr, (IMG_SIZE, IMG_SIZE))

    # Convert BGR back to RGB (TensorFlow/Keras expects RGB)
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)

    # Normalize: scale pixel values from [0, 255] to [0.0, 1.0]
    # This matches the rescale=1.0/255.0 used in training
    img_normalized = img_rgb.astype(np.float32) / 255.0

    # Add batch dimension: model expects (batch_size, height, width, channels)
    # Our single image needs to be (1, 224, 224, 3)
    img_batch = np.expand_dims(img_normalized, axis=0)

    return img_batch


def full_preprocess_pipeline(file_bytes: bytes) -> np.ndarray:
    """
    Master function — runs the full preprocessing pipeline end-to-end.
    Call this from detection_service.py.
    Returns: NumPy array of shape (1, 224, 224, 3) ready for model.predict()
    """
    img_bgr  = load_and_validate_image(file_bytes)
    img_face = detect_and_crop_face(img_bgr)
    img_ready = preprocess_for_model(img_face)
    return img_ready
```

### Step 6.7 — model_loader.py

This is critical for performance. The model must be loaded **once** when FastAPI starts, not on every API request. Loading a TensorFlow model takes 2-5 seconds — doing that on every upload request would make your API terribly slow.

```python
# backend/app/ml/model_loader.py

import tensorflow as tf
import numpy as np
import os

# This is the model instance — it's a module-level variable so it persists in memory
_model = None

def load_model(model_path: str) -> None:
    """
    Load the trained model from disk and store it in the module-level _model variable.
    Called once during FastAPI application startup via lifespan event.
    """
    global _model

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at: {model_path}\n"
            "Please run backend/ml_training/train.py first to generate the model."
        )

    print(f"[ML] Loading model from: {model_path}")
    _model = tf.keras.models.load_model(model_path)
    print(f"[ML] Model loaded successfully. Input shape: {_model.input_shape}")


def get_model() -> tf.keras.Model:
    """
    Returns the loaded model. Raises an error if load_model() was never called.
    """
    if _model is None:
        raise RuntimeError("Model has not been loaded. Call load_model() during app startup.")
    return _model


def predict(preprocessed_image: np.ndarray) -> dict:
    """
    Runs inference on a preprocessed image batch.
    
    Input:  NumPy array of shape (1, 224, 224, 3)
    Output: dict with keys 'label' (str), 'confidence' (float), 'raw_score' (float)
    
    IMPORTANT — Understanding the output score:
    Our training used flow_from_directory which assigns class indices alphabetically.
    'fake' → index 0, 'real' → index 1.
    With binary crossentropy and sigmoid:
      - Score close to 0.0 → model thinks it's 'fake' (class 0)
      - Score close to 1.0 → model thinks it's 'real' (class 1)
    
    So: score > 0.5 = REAL, score <= 0.5 = FAKE
    Confidence for FAKE = (1.0 - score) * 100
    Confidence for REAL = score * 100
    """
    model = get_model()

    # model.predict() returns a 2D array: [[score]]
    # We extract the single float value with [0][0]
    raw_score = float(model.predict(preprocessed_image, verbose=0)[0][0])

    if raw_score > 0.5:
        label      = "REAL"
        confidence = round(raw_score * 100, 2)
    else:
        label      = "FAKE"
        confidence = round((1.0 - raw_score) * 100, 2)

    return {
        "label":      label,
        "confidence": confidence,    # e.g., 87.34 (means 87.34% sure of this label)
        "raw_score":  raw_score      # Raw sigmoid output, useful for debugging
    }
```

---

## 7. FASTAPI BACKEND

### Step 7.1 — config.py

This module reads your `.env` file and exposes a `Settings` object. Every other file imports from here — no file reads `.env` directly.

```python
# backend/app/config.py

from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # These names must EXACTLY match the keys in your .env file
    MONGO_URI:                       str
    DATABASE_NAME:                   str
    JWT_SECRET_KEY:                  str
    JWT_ALGORITHM:                   str  = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int  = 60
    MODEL_PATH:                      str
    UPLOAD_DIR:                      str  = "uploads"

    class Config:
        # Tell pydantic where to find the .env file
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a single settings instance — import this everywhere
settings = Settings()
```

Note: Install `pydantic-settings` (separate from `pydantic`): `pip install pydantic-settings`
Add it to `requirements.txt` as well: `pydantic-settings==2.2.1`

### Step 7.2 — db/mongo.py

```python
# backend/app/db/mongo.py

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

# Module-level client — initialized once, reused across all requests
_client: AsyncIOMotorClient = None

def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client

def get_database() -> AsyncIOMotorDatabase:
    """
    Returns the database object. All collection operations happen through this.
    Usage in service files:  db = get_database()
                              await db["users"].find_one(...)
    """
    return get_client()[settings.DATABASE_NAME]

async def close_mongo_connection():
    """Called on app shutdown to cleanly close the MongoDB connection."""
    global _client
    if _client:
        _client.close()
        _client = None
```

### Step 7.3 — Pydantic Models (Request/Response Schemas)

Pydantic models serve two purposes: they **validate incoming data** (FastAPI auto-validates request bodies against them) and **shape outgoing data** (they define what your API responses look like).

```python
# backend/app/models/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Used for registration — what the client must send."""
    username: str = Field(..., min_length=3, max_length=30)
    email:    EmailStr                                        # pydantic validates email format
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """Used for login."""
    email:    EmailStr
    password: str

class UserResponse(BaseModel):
    """What we send BACK to the client — never include password_hash here."""
    id:         str
    username:   str
    email:      str
    created_at: datetime

class TokenResponse(BaseModel):
    """Response after successful login."""
    access_token: str
    token_type:   str = "bearer"
    username:     str
```

```python
# backend/app/models/scan.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScanResult(BaseModel):
    """Response after a successful detection API call."""
    scan_id:    str
    label:      str            # "REAL" or "FAKE"
    confidence: float          # e.g., 87.34
    raw_score:  float          # Raw model output
    filename:   str
    scanned_at: datetime

class ScanHistoryItem(BaseModel):
    """A single item in the user's history list."""
    scan_id:    str
    label:      str
    confidence: float
    filename:   str
    scanned_at: datetime

class ScanHistoryResponse(BaseModel):
    """Full history response."""
    scans: list[ScanHistoryItem]
    total: int
```

### Step 7.4 — auth_service.py

```python
# backend/app/services/auth_service.py

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from app.db.mongo import get_database
from app.config import settings
from app.models.user import UserCreate

# CryptContext handles password hashing.
# "bcrypt" is the algorithm — it's slow by design, making brute-force attacks expensive.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a plain text password. bcrypt automatically adds a salt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a plain password matches a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Creates a JWT token.
    'data' should contain {'sub': user_id_string} at minimum.
    The token encodes: subject (user id), expiry time, and any extra data.
    """
    to_encode  = data.copy()
    expire     = datetime.now(timezone.utc) + timedelta(
                     minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
                 )
    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return token


def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    Raises JWTError if the token is invalid, expired, or tampered with.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")


async def register_user(user_data: UserCreate) -> dict:
    """
    Creates a new user in MongoDB.
    Returns the created user document (without password_hash).
    Raises ValueError if email already exists.
    """
    db = get_database()
    users_collection = db["users"]

    # Check for duplicate email
    existing = await users_collection.find_one({"email": user_data.email})
    if existing:
        raise ValueError("An account with this email already exists.")

    new_user = {
        "username":      user_data.username,
        "email":         user_data.email,
        "password_hash": hash_password(user_data.password),
        "created_at":    datetime.now(timezone.utc)
    }

    result = await users_collection.insert_one(new_user)

    return {
        "id":         str(result.inserted_id),
        "username":   new_user["username"],
        "email":      new_user["email"],
        "created_at": new_user["created_at"]
    }


async def login_user(email: str, password: str) -> dict:
    """
    Validates credentials and returns a JWT token + user info.
    Raises ValueError if credentials are invalid.
    """
    db = get_database()
    user = await db["users"].find_one({"email": email})

    if not user or not verify_password(password, user["password_hash"]):
        # Use a generic error message — never tell the user which part was wrong
        # (that would help attackers know if an email exists)
        raise ValueError("Invalid email or password.")

    token = create_access_token({"sub": str(user["_id"])})

    return {
        "access_token": token,
        "token_type":   "bearer",
        "username":     user["username"]
    }
```

### Step 7.5 — detection_service.py

```python
# backend/app/services/detection_service.py

import os
import uuid
import aiofiles  # For async file writing — install: pip install aiofiles
from datetime import datetime, timezone
from app.db.mongo import get_database
from app.ml.preprocessor import full_preprocess_pipeline
from app.ml.model_loader import predict
from app.config import settings


async def run_detection(file_bytes: bytes, original_filename: str, user_id: str) -> dict:
    """
    Master detection function. Orchestrates:
    1. Save uploaded file
    2. Preprocess the image
    3. Run model inference
    4. Save result to MongoDB
    5. Return result to route handler
    """

    # ── STEP 1: Save the uploaded file ──────────────────────────────────────
    # Generate a unique filename to avoid collisions between users
    file_ext  = os.path.splitext(original_filename)[1].lower()  # e.g., '.jpg'
    unique_id = str(uuid.uuid4())
    save_name = f"{unique_id}{file_ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, save_name)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # aiofiles allows async file writing — doesn't block the event loop
    async with aiofiles.open(save_path, "wb") as f:
        await f.write(file_bytes)

    # ── STEP 2: Preprocess ───────────────────────────────────────────────────
    # This will raise ValueError if the image is invalid
    processed_image = full_preprocess_pipeline(file_bytes)

    # ── STEP 3: Run model inference ──────────────────────────────────────────
    prediction = predict(processed_image)
    # prediction = {"label": "FAKE", "confidence": 87.34, "raw_score": 0.1266}

    # ── STEP 4: Save to MongoDB ──────────────────────────────────────────────
    scan_id  = str(uuid.uuid4())
    scan_doc = {
        "scan_id":   scan_id,
        "user_id":   user_id,
        "filename":  original_filename,
        "saved_as":  save_name,
        "label":     prediction["label"],
        "confidence":prediction["confidence"],
        "raw_score": prediction["raw_score"],
        "scanned_at":datetime.now(timezone.utc)
    }

    db = get_database()
    await db["scans"].insert_one(scan_doc)

    # ── STEP 5: Return result ────────────────────────────────────────────────
    return {
        "scan_id":    scan_id,
        "label":      prediction["label"],
        "confidence": prediction["confidence"],
        "raw_score":  prediction["raw_score"],
        "filename":   original_filename,
        "scanned_at": scan_doc["scanned_at"]
    }
```

Don't forget to add `aiofiles` to `requirements.txt`: `aiofiles==23.2.1`

### Step 7.6 — history_service.py

```python
# backend/app/services/history_service.py

from app.db.mongo import get_database


async def get_user_history(user_id: str, limit: int = 20) -> dict:
    """
    Fetches the most recent scans for a user, newest first.
    limit: how many records to return (default 20)
    """
    db = get_database()

    cursor = db["scans"].find(
        {"user_id": user_id},          # Filter by this user's ID
        {"_id": 0}                     # Exclude MongoDB's internal _id field from results
    ).sort("scanned_at", -1).limit(limit)  # Sort descending (newest first), cap at limit

    scans = await cursor.to_list(length=limit)
    total = await db["scans"].count_documents({"user_id": user_id})

    return {"scans": scans, "total": total}
```

### Step 7.7 — middleware/auth_middleware.py

```python
# backend/app/middleware/auth_middleware.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import decode_token
from app.db.mongo import get_database

# HTTPBearer automatically extracts the token from the "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    """
    FastAPI dependency function. Inject this into any route that requires authentication.
    
    Usage in a route:
        @router.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            return {"message": f"Hello, {current_user['username']}"}
    
    It will:
    1. Extract the token from the Authorization header
    2. Decode and validate it
    3. Look up the user in MongoDB
    4. Return the user document, or raise 401 if anything fails
    """
    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Token payload missing 'sub'")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Look up the user in the database to make sure they still exist
    db = get_database()
    from bson import ObjectId
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Return a clean user dict (never return password_hash)
    return {
        "id":       str(user["_id"]),
        "username": user["username"],
        "email":    user["email"]
    }
```

### Step 7.8 — routes/auth.py

```python
# backend/app/routes/auth.py

from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    """
    Registers a new user.
    Request body: { "username": "...", "email": "...", "password": "..." }
    Response:     { "id": "...", "username": "...", "email": "...", "created_at": "..." }
    """
    try:
        user = await register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Authenticates a user and returns a JWT token.
    Request body: { "email": "...", "password": "..." }
    Response:     { "access_token": "...", "token_type": "bearer", "username": "..." }
    """
    try:
        result = await login_user(credentials.email, credentials.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
```

### Step 7.9 — routes/detection.py

```python
# backend/app/routes/detection.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.models.scan import ScanResult, ScanHistoryResponse
from app.services.detection_service import run_detection
from app.services.history_service import get_user_history
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api", tags=["Detection"])

# Maximum allowed upload size: 5MB in bytes
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/detect", response_model=ScanResult)
async def detect_image(
    file: UploadFile = File(...),                      # UploadFile = FastAPI's file upload type
    current_user: dict = Depends(get_current_user)     # JWT auth dependency injected here
):
    """
    Main detection endpoint.
    Accepts a multipart form upload with the image file.
    Returns the detection result.
    """

    # ── Validate file type ───────────────────────────────────────────────────
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Only JPG, PNG, and WEBP are allowed."
        )

    # ── Read file bytes and validate size ────────────────────────────────────
    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 5MB."
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file received."
        )

    # ── Run detection ────────────────────────────────────────────────────────
    try:
        result = await run_detection(
            file_bytes        = file_bytes,
            original_filename = file.filename,
            user_id           = current_user["id"]
        )
        return result
    except ValueError as e:
        # ValueError from preprocessor means the file wasn't a valid image
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Unexpected errors — log in production, return generic message to user
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during detection. Please try again."
        )


@router.get("/history", response_model=ScanHistoryResponse)
async def get_history(current_user: dict = Depends(get_current_user)):
    """
    Returns the authenticated user's scan history (most recent 20 scans).
    """
    history = await get_user_history(user_id=current_user["id"])
    return history
```

### Step 7.10 — main.py (The Entry Point)

```python
# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.db.mongo import close_mongo_connection
from app.ml.model_loader import load_model
from app.routes import auth, detection


# ── Lifespan: runs on startup and shutdown ───────────────────────────────────
# This is the modern FastAPI way to handle startup/shutdown events.
# Everything in the 'try' block runs when the app starts.
# Everything after 'yield' runs when the app shuts down.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──────────────────────────────────────────────────────────────
    print("[Startup] Loading ML model...")
    load_model(settings.MODEL_PATH)
    print("[Startup] ML model ready.")
    print("[Startup] Application is ready to accept requests.")

    yield  # App runs here — handling requests

    # ── SHUTDOWN ─────────────────────────────────────────────────────────────
    print("[Shutdown] Closing MongoDB connection...")
    await close_mongo_connection()
    print("[Shutdown] Goodbye.")


# ── Create the FastAPI app ────────────────────────────────────────────────────
app = FastAPI(
    title="Deepfake Detection API",
    description="Upload an image and find out if it's AI-generated.",
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS Configuration ────────────────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing.
# Your React app (port 5173) is a different "origin" than your API (port 8000).
# Without this, browsers will BLOCK all API requests from React.
# This is one of the most common gotchas for beginners — configure it early.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],      # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],      # Allow Authorization, Content-Type, etc.
)

# ── Register Routes ───────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(detection.router)

@app.get("/")
async def root():
    return {"message": "Deepfake Detection API is running.", "status": "ok"}
```

---

## 8. MONGODB SCHEMA & DATABASE DESIGN

### Collections Overview

You have exactly two collections in `deepfake_db`: `users` and `scans`. That's it.

### Users Collection Schema

Each document in the `users` collection looks like this:

```json
{
    "_id":           ObjectId("664f3a..."),   // MongoDB auto-generated unique ID
    "username":      "johndoe",
    "email":         "john@example.com",
    "password_hash": "$2b$12$...",            // bcrypt hash — never the plain password
    "created_at":    ISODate("2024-05-01T10:30:00Z")
}
```

### Scans Collection Schema

Each document in the `scans` collection looks like this:

```json
{
    "_id":        ObjectId("664f3b..."),      // MongoDB auto-generated
    "scan_id":    "550e8400-e29b-...",        // UUID we generate — used in API responses
    "user_id":    "664f3a...",                // String form of user's _id (for lookup)
    "filename":   "profile_photo.jpg",        // Original filename from upload
    "saved_as":   "550e8400-e29b...jpg",      // What we saved it as (UUID-named)
    "label":      "FAKE",                     // "REAL" or "FAKE"
    "confidence": 87.34,                      // Confidence percentage
    "raw_score":  0.1266,                     // Raw sigmoid output
    "scanned_at": ISODate("2024-05-01T10:35:00Z")
}
```

### MongoDB Indexes

Create these indexes on MongoDB Atlas (under "Database" → your cluster → "Collections" → "Indexes") OR run this Python snippet once after your app is running. Indexes dramatically speed up queries.

```python
# Run this once as a setup script: backend/setup_indexes.py

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

async def create_indexes():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DATABASE_NAME")]

    # Unique index on email — prevents duplicate accounts
    await db["users"].create_index("email", unique=True)

    # Index on scans.user_id — makes history queries fast
    await db["scans"].create_index("user_id")

    # Compound index on (user_id, scanned_at) — makes sorted history queries very fast
    await db["scans"].create_index([("user_id", 1), ("scanned_at", -1)])

    print("Indexes created successfully.")
    client.close()

asyncio.run(create_indexes())
```

---

## 9. JWT AUTHENTICATION FLOW — DETAILED

Understanding this end-to-end prevents a lot of confusion. Here is exactly what happens during login and every subsequent request.

### Registration Flow

```
Client sends POST /api/auth/register
Body: { "username": "john", "email": "john@example.com", "password": "secret123" }
                        ↓
FastAPI validates body against UserCreate pydantic model
                        ↓
auth_service.register_user() called
    → Check MongoDB: does this email already exist? If yes, raise 400 error.
    → Hash password with bcrypt: "secret123" → "$2b$12$KJ83..."
    → Insert document into 'users' collection
    → Return user info (no password hash)
                        ↓
Response: 201 Created
{ "id": "664f3a...", "username": "john", "email": "john@...", "created_at": "..." }
```

### Login Flow

```
Client sends POST /api/auth/login
Body: { "email": "john@example.com", "password": "secret123" }
                        ↓
auth_service.login_user() called
    → Find user by email in MongoDB
    → If not found → raise 401 (same error message as wrong password — security best practice)
    → bcrypt.verify("secret123", "$2b$12$KJ83...") → True/False
    → If False → raise 401
    → Create JWT token: encode { "sub": "664f3a...", "exp": <60 mins from now> }
    → Sign with JWT_SECRET_KEY using HS256 algorithm
                        ↓
Response: 200 OK
{ "access_token": "eyJhbGciOiJIUzI1NiJ9...", "token_type": "bearer", "username": "john" }
```

### Authenticated Request Flow (e.g., POST /api/detect)

```
Client sends POST /api/detect
Headers: { "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9..." }
Body:     multipart/form-data with image file
                        ↓
FastAPI route has: Depends(get_current_user)
    → HTTPBearer extracts "eyJhbGciOiJIUzI1NiJ9..." from the header
    → decode_token() verifies signature and expiry
    → If invalid/expired → raise 401
    → Extract user_id from payload["sub"]
    → Find user in MongoDB by ObjectId(user_id)
    → If not found → raise 401
    → Return user dict to route handler
                        ↓
Route handler receives current_user = { "id": "664f3a...", "username": "john", ... }
Proceeds with detection logic
```

---

## 10. REACT FRONTEND

### Step 10.1 — Axios Instance

This is the first file to write in the frontend. All API calls go through this.

```javascript
// frontend/src/api/axiosInstance.js

import axios from "axios";

const axiosInstance = axios.create({
    baseURL: "http://localhost:8000",  // Your FastAPI server address
    timeout: 30000,                    // 30 second timeout (model inference can be slow)
});

// REQUEST INTERCEPTOR
// Runs before every request — automatically attaches the JWT token from localStorage
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// RESPONSE INTERCEPTOR
// Runs after every response — handles 401 errors globally
// If any API call returns 401 (token expired/invalid), automatically log the user out
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token is invalid or expired — clear storage and redirect to login
            localStorage.removeItem("access_token");
            localStorage.removeItem("username");
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;
```

### Step 10.2 — AuthContext (Global Auth State)

```jsx
// frontend/src/context/AuthContext.jsx

import { createContext, useState, useEffect } from "react";

// Create the context object
export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    // Initialize state from localStorage — so page refresh doesn't log user out
    const [token,    setToken]    = useState(() => localStorage.getItem("access_token"));
    const [username, setUsername] = useState(() => localStorage.getItem("username"));

    const isAuthenticated = !!token;  // Boolean: true if token exists

    const login = (accessToken, user) => {
        // Save to state and localStorage simultaneously
        setToken(accessToken);
        setUsername(user);
        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("username", user);
    };

    const logout = () => {
        setToken(null);
        setUsername(null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("username");
    };

    return (
        <AuthContext.Provider value={{ token, username, isAuthenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}
```

### Step 10.3 — useAuth Hook

```javascript
// frontend/src/hooks/useAuth.js

import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

// Convenience hook — instead of: const { login } = useContext(AuthContext);
// You write:                       const { login } = useAuth();
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used inside an AuthProvider");
    }
    return context;
}
```

### Step 10.4 — App.jsx (Router Setup)

```jsx
// frontend/src/App.jsx

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import HistoryPage from "./pages/HistoryPage";

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    {/* Public routes — accessible without login */}
                    <Route path="/login"    element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />

                    {/* Protected routes — redirect to /login if not authenticated */}
                    <Route element={<ProtectedRoute />}>
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/history"   element={<HistoryPage />} />
                    </Route>

                    {/* Default redirect */}
                    <Route path="/"  element={<Navigate to="/dashboard" replace />} />
                    <Route path="*"  element={<Navigate to="/login" replace />} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
```

### Step 10.5 — ProtectedRoute Component

```jsx
// frontend/src/components/ProtectedRoute.jsx

import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

// This component acts as a guard.
// If the user IS authenticated → render the page (<Outlet /> = child route)
// If the user is NOT authenticated → redirect to /login
export default function ProtectedRoute() {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
```

### Step 10.6 — LoginPage.jsx

```jsx
// frontend/src/pages/LoginPage.jsx

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useAuth } from "../hooks/useAuth";
import axiosInstance from "../api/axiosInstance";

export default function LoginPage() {
    const { register, handleSubmit, formState: { errors } } = useForm();
    const { login } = useAuth();
    const navigate  = useNavigate();
    const [serverError, setServerError] = useState("");
    const [loading,     setLoading]     = useState(false);

    const onSubmit = async (data) => {
        setLoading(true);
        setServerError("");
        try {
            const response = await axiosInstance.post("/api/auth/login", {
                email:    data.email,
                password: data.password
            });
            // Save token and username globally, then redirect
            login(response.data.access_token, response.data.username);
            navigate("/dashboard");
        } catch (err) {
            setServerError(err.response?.data?.detail || "Login failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
            <div className="w-full max-w-md bg-gray-900 rounded-2xl p-8 shadow-xl">
                <h1 className="text-3xl font-bold text-white mb-2">Sign In</h1>
                <p className="text-gray-400 mb-8">Detect deepfakes with AI precision</p>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                    <div>
                        <label className="block text-sm text-gray-300 mb-1">Email</label>
                        <input
                            type="email"
                            className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-violet-500"
                            {...register("email", { required: "Email is required" })}
                        />
                        {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>}
                    </div>

                    <div>
                        <label className="block text-sm text-gray-300 mb-1">Password</label>
                        <input
                            type="password"
                            className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-violet-500"
                            {...register("password", { required: "Password is required" })}
                        />
                        {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>}
                    </div>

                    {serverError && (
                        <p className="bg-red-900/40 text-red-400 text-sm px-4 py-2 rounded-lg">
                            {serverError}
                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold py-3 rounded-lg transition-colors"
                    >
                        {loading ? "Signing in..." : "Sign In"}
                    </button>
                </form>

                <p className="text-gray-400 text-sm text-center mt-6">
                    Don't have an account?{" "}
                    <Link to="/register" className="text-violet-400 hover:underline">Register</Link>
                </p>
            </div>
        </div>
    );
}
```

### Step 10.7 — RegisterPage.jsx

```jsx
// frontend/src/pages/RegisterPage.jsx
// Structure identical to LoginPage but calls /api/auth/register

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import axiosInstance from "../api/axiosInstance";

export default function RegisterPage() {
    const { register, handleSubmit, formState: { errors } } = useForm();
    const navigate = useNavigate();
    const [serverError, setServerError] = useState("");
    const [loading,     setLoading]     = useState(false);
    const [success,     setSuccess]     = useState(false);

    const onSubmit = async (data) => {
        setLoading(true);
        setServerError("");
        try {
            await axiosInstance.post("/api/auth/register", {
                username: data.username,
                email:    data.email,
                password: data.password
            });
            setSuccess(true);
            // Redirect to login after 2 seconds
            setTimeout(() => navigate("/login"), 2000);
        } catch (err) {
            setServerError(err.response?.data?.detail || "Registration failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-gray-950 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-green-400 text-5xl mb-4">✓</div>
                    <p className="text-white text-xl">Account created! Redirecting to login...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
            <div className="w-full max-w-md bg-gray-900 rounded-2xl p-8 shadow-xl">
                <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
                <p className="text-gray-400 mb-8">Join the deepfake detector</p>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                    <div>
                        <label className="block text-sm text-gray-300 mb-1">Username</label>
                        <input
                            className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-violet-500"
                            {...register("username", {
                                required: "Username is required",
                                minLength: { value: 3, message: "Minimum 3 characters" }
                            })}
                        />
                        {errors.username && <p className="text-red-400 text-xs mt-1">{errors.username.message}</p>}
                    </div>

                    <div>
                        <label className="block text-sm text-gray-300 mb-1">Email</label>
                        <input
                            type="email"
                            className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-violet-500"
                            {...register("email", { required: "Email is required" })}
                        />
                        {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>}
                    </div>

                    <div>
                        <label className="block text-sm text-gray-300 mb-1">Password</label>
                        <input
                            type="password"
                            className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-violet-500"
                            {...register("password", {
                                required: "Password is required",
                                minLength: { value: 6, message: "Minimum 6 characters" }
                            })}
                        />
                        {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>}
                    </div>

                    {serverError && (
                        <p className="bg-red-900/40 text-red-400 text-sm px-4 py-2 rounded-lg">{serverError}</p>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold py-3 rounded-lg transition-colors"
                    >
                        {loading ? "Creating account..." : "Register"}
                    </button>
                </form>

                <p className="text-gray-400 text-sm text-center mt-6">
                    Already have an account?{" "}
                    <Link to="/login" className="text-violet-400 hover:underline">Sign in</Link>
                </p>
            </div>
        </div>
    );
}
```

### Step 10.8 — DashboardPage.jsx (Core UI)

```jsx
// frontend/src/pages/DashboardPage.jsx

import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import axiosInstance from "../api/axiosInstance";
import Navbar from "../components/Navbar";
import ResultCard from "../components/ResultCard";
import LoadingSpinner from "../components/LoadingSpinner";

export default function DashboardPage() {
    const { username } = useAuth();
    const navigate     = useNavigate();

    const [selectedFile,  setSelectedFile]  = useState(null);
    const [preview,       setPreview]       = useState(null);   // data URL for preview
    const [result,        setResult]        = useState(null);   // detection result object
    const [loading,       setLoading]       = useState(false);
    const [error,         setError]         = useState("");

    const fileInputRef = useRef(null);

    const handleFileSelect = (file) => {
        if (!file) return;

        // Validate on the client side before sending to server
        const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
        if (!allowedTypes.includes(file.type)) {
            setError("Please select a JPG, PNG, or WEBP image.");
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            setError("File is too large. Maximum 5MB allowed.");
            return;
        }

        setError("");
        setResult(null);
        setSelectedFile(file);

        // Create a local URL to preview the image without uploading it
        const reader = new FileReader();
        reader.onloadend = () => setPreview(reader.result);
        reader.readAsDataURL(file);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    };

    const handleAnalyze = async () => {
        if (!selectedFile) return;

        setLoading(true);
        setError("");

        // FormData is required for multipart file uploads
        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await axiosInstance.post("/api/detect", formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || "Detection failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setSelectedFile(null);
        setPreview(null);
        setResult(null);
        setError("");
    };

    return (
        <div className="min-h-screen bg-gray-950">
            <Navbar />
            <div className="max-w-2xl mx-auto px-4 py-12">
                <h1 className="text-3xl font-bold text-white mb-2">
                    Welcome back, {username}
                </h1>
                <p className="text-gray-400 mb-10">
                    Upload an image to check if it's AI-generated or real.
                </p>

                {/* Upload Area */}
                {!preview ? (
                    <div
                        onDrop={handleDrop}
                        onDragOver={(e) => e.preventDefault()}
                        onClick={() => fileInputRef.current.click()}
                        className="border-2 border-dashed border-gray-700 hover:border-violet-500 rounded-2xl p-16 text-center cursor-pointer transition-colors"
                    >
                        <div className="text-5xl mb-4">🖼️</div>
                        <p className="text-gray-300 font-medium">
                            Drag & drop an image here, or click to select
                        </p>
                        <p className="text-gray-500 text-sm mt-2">
                            JPG, PNG, WEBP — max 5MB
                        </p>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/jpeg,image/png,image/webp"
                            className="hidden"
                            onChange={(e) => handleFileSelect(e.target.files[0])}
                        />
                    </div>
                ) : (
                    <div className="space-y-6">
                        {/* Image Preview */}
                        <div className="rounded-2xl overflow-hidden border border-gray-800">
                            <img
                                src={preview}
                                alt="Selected"
                                className="w-full object-contain max-h-80 bg-gray-900"
                            />
                        </div>

                        {/* Action Buttons */}
                        {!result && (
                            <div className="flex gap-3">
                                <button
                                    onClick={handleAnalyze}
                                    disabled={loading}
                                    className="flex-1 bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition-colors"
                                >
                                    {loading ? "Analyzing..." : "Analyze Image"}
                                </button>
                                <button
                                    onClick={handleReset}
                                    className="px-6 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium py-3 rounded-xl transition-colors"
                                >
                                    Cancel
                                </button>
                            </div>
                        )}

                        {/* Loading State */}
                        {loading && (
                            <div className="flex items-center justify-center py-6">
                                <LoadingSpinner />
                                <span className="text-gray-400 ml-3">Running AI analysis...</span>
                            </div>
                        )}

                        {/* Result */}
                        {result && (
                            <>
                                <ResultCard result={result} />
                                <button
                                    onClick={handleReset}
                                    className="w-full bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium py-3 rounded-xl transition-colors"
                                >
                                    Analyze Another Image
                                </button>
                            </>
                        )}
                    </div>
                )}

                {/* Error Display */}
                {error && (
                    <p className="mt-4 bg-red-900/40 text-red-400 text-sm px-4 py-3 rounded-lg">
                        {error}
                    </p>
                )}
            </div>
        </div>
    );
}
```

### Step 10.9 — ResultCard Component

```jsx
// frontend/src/components/ResultCard.jsx

export default function ResultCard({ result }) {
    const isFake      = result.label === "FAKE";
    const color       = isFake ? "red" : "green";
    const bgColor     = isFake ? "bg-red-900/30"  : "bg-green-900/30";
    const borderColor = isFake ? "border-red-700"  : "border-green-700";
    const textColor   = isFake ? "text-red-400"    : "text-green-400";
    const barColor    = isFake ? "bg-red-500"      : "bg-green-500";
    const emoji       = isFake ? "⚠️" : "✅";

    return (
        <div className={`rounded-2xl border ${borderColor} ${bgColor} p-6`}>
            <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">{emoji}</span>
                <div>
                    <h2 className={`text-2xl font-bold ${textColor}`}>
                        {isFake ? "DEEPFAKE DETECTED" : "LIKELY REAL"}
                    </h2>
                    <p className="text-gray-400 text-sm">{result.filename}</p>
                </div>
            </div>

            {/* Confidence Bar */}
            <div className="mt-4">
                <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">Confidence</span>
                    <span className={`font-bold ${textColor}`}>{result.confidence}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-3">
                    <div
                        className={`${barColor} h-3 rounded-full transition-all duration-700`}
                        style={{ width: `${result.confidence}%` }}
                    />
                </div>
            </div>

            <p className="text-gray-500 text-xs mt-4">
                Scanned at: {new Date(result.scanned_at).toLocaleString()}
            </p>
        </div>
    );
}
```

### Step 10.10 — Navbar Component

```jsx
// frontend/src/components/Navbar.jsx

import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
    const { username, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4">
            <div className="max-w-4xl mx-auto flex items-center justify-between">
                <Link to="/dashboard" className="text-white font-bold text-xl">
                    🔍 DeepDetect
                </Link>
                <div className="flex items-center gap-6">
                    <Link to="/dashboard" className="text-gray-400 hover:text-white text-sm transition-colors">
                        Detect
                    </Link>
                    <Link to="/history" className="text-gray-400 hover:text-white text-sm transition-colors">
                        History
                    </Link>
                    <span className="text-gray-500 text-sm">|</span>
                    <span className="text-gray-300 text-sm">{username}</span>
                    <button
                        onClick={handleLogout}
                        className="text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-1.5 rounded-lg transition-colors"
                    >
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    );
}
```

### Step 10.11 — HistoryPage.jsx

```jsx
// frontend/src/pages/HistoryPage.jsx

import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import axiosInstance from "../api/axiosInstance";
import LoadingSpinner from "../components/LoadingSpinner";

export default function HistoryPage() {
    const [scans,   setScans]   = useState([]);
    const [total,   setTotal]   = useState(0);
    const [loading, setLoading] = useState(true);
    const [error,   setError]   = useState("");

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await axiosInstance.get("/api/history");
                setScans(response.data.scans);
                setTotal(response.data.total);
            } catch (err) {
                setError("Failed to load history.");
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);  // Empty dependency array = run once on component mount

    return (
        <div className="min-h-screen bg-gray-950">
            <Navbar />
            <div className="max-w-4xl mx-auto px-4 py-12">
                <h1 className="text-3xl font-bold text-white mb-2">Scan History</h1>
                <p className="text-gray-400 mb-8">Your last {total} scans</p>

                {loading && (
                    <div className="flex justify-center py-20">
                        <LoadingSpinner />
                    </div>
                )}

                {error && (
                    <p className="text-red-400 bg-red-900/30 px-4 py-3 rounded-lg">{error}</p>
                )}

                {!loading && scans.length === 0 && (
                    <div className="text-center py-20 text-gray-500">
                        <p className="text-4xl mb-3">📂</p>
                        <p>No scans yet. Upload an image to get started.</p>
                    </div>
                )}

                {!loading && scans.length > 0 && (
                    <div className="overflow-x-auto rounded-xl border border-gray-800">
                        <table className="w-full text-sm">
                            <thead className="bg-gray-900">
                                <tr>
                                    <th className="text-left text-gray-400 px-4 py-3">File</th>
                                    <th className="text-left text-gray-400 px-4 py-3">Result</th>
                                    <th className="text-left text-gray-400 px-4 py-3">Confidence</th>
                                    <th className="text-left text-gray-400 px-4 py-3">Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {scans.map((scan) => (
                                    <tr key={scan.scan_id} className="border-t border-gray-800 hover:bg-gray-900/50">
                                        <td className="px-4 py-3 text-gray-300 truncate max-w-xs">
                                            {scan.filename}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                                                scan.label === "FAKE"
                                                    ? "bg-red-900/50 text-red-400"
                                                    : "bg-green-900/50 text-green-400"
                                            }`}>
                                                {scan.label}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-gray-300">
                                            {scan.confidence}%
                                        </td>
                                        <td className="px-4 py-3 text-gray-500">
                                            {new Date(scan.scanned_at).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
```

### Step 10.12 — LoadingSpinner Component

```jsx
// frontend/src/components/LoadingSpinner.jsx

export default function LoadingSpinner() {
    return (
        <div className="w-8 h-8 border-4 border-gray-700 border-t-violet-500 rounded-full animate-spin" />
    );
}
```

---

## 11. END-TO-END DATA FLOW

### Full Detection Request — Step by Step

```
① User drops an image on DashboardPage.jsx
   → handleFileSelect() runs
   → Client-side validation: type & size check
   → FileReader creates a local preview URL
   → selectedFile state is updated, preview shown

② User clicks "Analyze Image"
   → handleAnalyze() runs
   → new FormData() created, image appended
   → axiosInstance.post("/api/detect", formData) called
   → REQUEST INTERCEPTOR fires:
       reads localStorage["access_token"]
       adds header: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
   → Browser sends multipart POST to http://localhost:8000/api/detect

③ FastAPI receives the request at routes/detection.py
   → Depends(get_current_user) triggers BEFORE the route function:
       HTTPBearer extracts the token from the header
       decode_token() verifies signature + expiry
       MongoDB query: find user by ObjectId(user_id)
       Returns user dict to route handler
   → File type validated (content_type check)
   → file.read() reads all bytes into memory
   → File size validated (len(bytes) check)

④ run_detection() called in detection_service.py:
   → UUID generated for filename
   → File bytes saved to uploads/ folder (aiofiles async write)
   → full_preprocess_pipeline(file_bytes) called:
       load_and_validate_image(): bytes → PIL → NumPy → BGR
       detect_and_crop_face(): Haar Cascade finds face, crops it
       preprocess_for_model(): resize 224x224, normalize, add batch dim
       returns numpy array shape (1, 224, 224, 3)
   → predict(preprocessed_image) called:
       model.predict() runs TensorFlow inference
       raw sigmoid value extracted (e.g., 0.1266)
       label computed: "FAKE" (score ≤ 0.5)
       confidence computed: (1.0 - 0.1266) * 100 = 87.34
       returns {"label": "FAKE", "confidence": 87.34, "raw_score": 0.1266}
   → Scan document created, inserted into MongoDB "scans" collection
   → Result dict returned

⑤ FastAPI serializes result as JSON:
   {
     "scan_id": "550e8400...",
     "label": "FAKE",
     "confidence": 87.34,
     "raw_score": 0.1266,
     "filename": "face.jpg",
     "scanned_at": "2024-05-01T10:35:00Z"
   }

⑥ Axios receives the 200 OK response
   → setResult(response.data) updates React state
   → RESPONSE INTERCEPTOR: 200 OK, passes through

⑦ React re-renders DashboardPage
   → ResultCard rendered with result data
   → Red card (FAKE) or green card (REAL) shown
   → Confidence bar animated to 87.34%
```

---

## 12. LIBRARY REFERENCE — EVERY PACKAGE

### Backend (Python)

| Package | Version | Purpose |
|---|---|---|
| fastapi | 0.111.0 | Web framework — routes, request/response handling |
| uvicorn[standard] | 0.29.0 | ASGI server — runs the FastAPI app |
| motor | 3.4.0 | Async MongoDB driver |
| pymongo | 4.7.2 | Motor depends on pymongo internally |
| python-jose[cryptography] | 3.3.0 | JWT creation and verification |
| passlib[bcrypt] | 1.7.4 | Password hashing with bcrypt |
| python-multipart | 0.0.9 | Enables FastAPI to accept file uploads (required) |
| python-dotenv | 1.0.1 | Reads .env file into environment variables |
| pydantic-settings | 2.2.1 | Settings class that reads from .env |
| Pillow | 10.3.0 | Image format validation and conversion |
| opencv-python-headless | 4.9.0.80 | Image preprocessing and face detection |
| numpy | 1.26.4 | Array operations between OpenCV and TensorFlow |
| tensorflow | 2.16.1 | Model training and inference |
| aiofiles | 23.2.1 | Async file writing |

### Frontend (Node.js)

| Package | Version | Purpose |
|---|---|---|
| react | 18.x | UI library |
| react-dom | 18.x | DOM rendering |
| react-router-dom | 6.x | Client-side navigation |
| axios | 1.x | HTTP client with interceptors |
| react-hook-form | 7.x | Form state management and validation |
| tailwindcss | 3.x | Utility-first CSS styling |
| autoprefixer | latest | Tailwind dependency |
| postcss | latest | Tailwind dependency |
| vite | 5.x | Build tool and dev server |

---

## 13. RUNNING THE FULL PROJECT

### Step 1 — Train the Model (One Time Only)

```bash
cd deepfake-detector/backend
source venv/bin/activate
python ml_training/dataset_prep.py     # Organize dataset
python ml_training/train.py            # Train the model (~20-40 mins on CPU)
python ml_training/evaluate.py         # Check accuracy on test set
```

After training, the file `backend/saved_model/efficientnet_deepfake.h5` should exist.

### Step 2 — Run the Backend

```bash
cd deepfake-detector/backend
source venv/bin/activate

# Run from inside the 'backend' directory so relative paths (uploads/, saved_model/) work correctly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
[Startup] Loading ML model...
[Startup] ML model ready.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit `http://localhost:8000/docs` to see the interactive Swagger UI — test your API here before touching the frontend.

### Step 3 — Run the Frontend

```bash
cd deepfake-detector/frontend
npm run dev
```

Visit `http://localhost:5173` — you should see the login page.

### Step 4 — Setup MongoDB Indexes (One Time Only)

```bash
cd deepfake-detector/backend
source venv/bin/activate
python setup_indexes.py
```

---

## 14. COMMON PITFALLS & HOW TO AVOID THEM

**CORS Error in the browser:** This means FastAPI's `CORSMiddleware` is either not configured or has the wrong origin. Double-check that `allow_origins=["http://localhost:5173"]` in `main.py` matches exactly what's in your browser's address bar. A trailing slash in the origin makes them not match.

**Model not found on startup:** The `uvicorn` command must be run from inside the `backend/` directory (not the project root), because `MODEL_PATH=saved_model/efficientnet_deepfake.h5` in `.env` is relative to where you run the command from.

**`422 Unprocessable Entity` from FastAPI:** This is a Pydantic validation error. It means the request body didn't match the expected schema. FastAPI will return a detailed message in the response body telling you exactly which field failed. Always check the `/docs` Swagger UI to see the expected format.

**Class index confusion (real labeled as fake):** When you train with `flow_from_directory`, class indices are assigned alphabetically. `fake → 0, real → 1`. This means a high sigmoid output (close to 1.0) means REAL. If your results seem inverted (real images coming back as fake), check `train_gen.class_indices` and adjust the threshold logic in `model_loader.py`.

**TensorFlow loading the model every request (making it slow):** Make absolutely sure `load_model()` is only called once in the lifespan startup event in `main.py`, and that `model_loader.py` stores the model in a module-level `_model` variable. Do not import or call `load_model()` inside any route or service function.

**`bson.errors.InvalidId` error:** This happens when you try to do `ObjectId(user_id)` but `user_id` is not a valid 24-character hex string. Make sure the JWT `sub` claim stores `str(user["_id"])` (the string form of the ObjectId), and that you convert it back with `ObjectId(user_id)` only in MongoDB queries.

**Image with no face detected still needs to be handled:** The `detect_and_crop_face()` function already handles this — if no face is found, it returns the full image. The model will still run, it just won't have the benefit of face-cropping. The prediction will still work, just potentially less accurately. This is the correct behavior.

**Large model file in Git:** The `.h5` model file can be 50-200MB. Add it to `.gitignore`. Never commit it. Add this to your root `.gitignore`:

```
backend/saved_model/
backend/uploads/
backend/venv/
backend/.env
frontend/node_modules/
__pycache__/
*.pyc
dataset/
```

---

*End of Blueprint — Every implementation decision is documented above. Follow phases in order: Model → Backend → Frontend. Test each phase in isolation before connecting to the next.*
