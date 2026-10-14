#!/usr/bin/env bash
# Build script for Render deployment
# Builds the React frontend and installs Python backend dependencies

set -o errexit

echo "=== Installing Python dependencies ==="
cd backend
pip install -r requirements.txt

echo "=== Installing Node.js dependencies ==="
cd ../frontend
npm install

echo "=== Building React frontend ==="
npm run build

echo "=== Copying frontend build to backend/static ==="
rm -rf ../backend/static
cp -r dist ../backend/static

echo "=== Build complete ==="
