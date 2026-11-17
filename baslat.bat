@echo off
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  echo Python bulunamadi. Kuruluyor...
  winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
  echo.
  echo Python kuruldu. Bu pencereyi kapatip baslat.bat dosyasini TEKRAR calistirin.
  pause
  exit /b
)
where ffmpeg >nul 2>&1
if errorlevel 1 (
  echo ffmpeg bulunamadi. Kuruluyor...
  winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
  echo.
  echo ffmpeg kuruldu. Bu pencereyi kapatip baslat.bat dosyasini TEKRAR calistirin.
  pause
  exit /b
)
py -m pip install -U yt-dlp
py sync_videos.py
echo.
echo Bitti. videos klasoru ve videos.json olustu.
pause
