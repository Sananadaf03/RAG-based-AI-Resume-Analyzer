@echo off
title AI Resume Analyzer Pro — 3D UI
echo.
echo  ==========================================
echo   AI Resume Analyzer Pro  - 3D UI Edition
echo  ==========================================
echo.
echo  Installing / checking requirements...
pip install -r requirements.txt --quiet
echo.
echo  Starting app on http://localhost:8501
echo  Press Ctrl+C to stop.
echo.
streamlit run app.py
pause
