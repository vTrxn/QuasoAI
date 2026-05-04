#!/bin/bash

echo "Iniciando Backend (FastAPI)..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

echo "Iniciando Frontend (Vite)..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Servicios iniciados."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Presiona Ctrl+C para detener ambos servicios."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
