# Deepfake Detector

Deepfake Detector is a full-stack project for binary image classification (REAL vs FAKE) using TensorFlow, FastAPI, MongoDB, and React.

## Stack

- Backend: FastAPI, Motor, JWT, TensorFlow, OpenCV
- Frontend: React 18, Vite, Tailwind CSS, React Router, Axios
- Database: MongoDB Atlas

## Project Structure

- `backend/`: API, auth, inference pipeline, model training scripts
- `frontend/`: React UI for authentication, image upload, and scan history
- `dataset/`: Dataset folders used for model training

## Quick Start

1. Configure backend environment variables in `backend/.env`.
2. Install backend dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Prepare and train the model:

```bash
python ml_training/dataset_prep.py
python ml_training/train.py
python ml_training/evaluate.py
```

4. Run backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Run frontend:

```bash
cd ../frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`  
Backend docs: `http://localhost:8000/docs`
