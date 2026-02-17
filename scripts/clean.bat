@echo off
echo === Steam Guide Saver — Cleanup ===
echo.

cd /d "%~dp0\.."

if exist build (
    rmdir /s /q build
    echo   Deleted: build/
) else (
    echo   Skip:    build/
)

if exist __pycache__ (
    rmdir /s /q __pycache__
    echo   Deleted: __pycache__/
) else (
    echo   Skip:    __pycache__/
)

if exist dist (
    rmdir /s /q dist
    echo   Deleted: dist/
) else (
    echo   Skip:    dist/
)

if exist SteamGuideSaver.spec (
    del SteamGuideSaver.spec
    echo   Deleted: SteamGuideSaver.spec
) else (
    echo   Skip:    SteamGuideSaver.spec
)

if exist downloader.log (
    del downloader.log
    echo   Deleted: downloader.log
) else (
    echo   Skip:    downloader.log
)

echo.
echo === Done! ===
pause