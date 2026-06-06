@echo off
echo Installing PillSafe backend dependencies...
python -m pip install fastapi uvicorn[standard] httpx pytesseract Pillow python-dotenv python-multipart
echo.
echo Done! To start the server run:
echo   python -m uvicorn main:app --reload
pause
