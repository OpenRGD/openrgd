@echo off
setlocal EnableDelayedExpansion

:: ==========================================
:: OPENRGD WINDOWS INTEGRATION INSTALLER v0.3
:: Registers the .rgd file type and applies a
:: custom file icon via a locally cached asset.
::
:: Developer Notes:
:: ----------------
:: The .rgd extension is intentionally mapped to
:: "OpenRGD.Bundle" and associated with a ZIP-like
:: behavior so that Windows Explorer can browse
:: the bundle contents transparently.
::
:: TECHNICAL DETAILS:
:: - "Content Type" = application/x-zip-compressed
:: - "PerceivedType" = compressed
:: - CLSID {E88DCCE0-B7B3-11d1-A9F0-00AA0060FA31}
::
:: WHY THIS WORKS:
:: Windows uses this specific CLSID to identify
:: ZIP archives as "Compressed Folders". Assigning
:: it to .rgd instructs Explorer to treat the file
:: as a folder-like container.
::
:: IMPORTANT:
:: This is a deliberate hack and valid as long as
:: .rgd bundles remain ZIP-compatible.
:: If the container format changes in the future,
:: REMOVE this CLSID entry — otherwise Explorer may
:: behave incorrectly or fail to open the bundle.
::
:: Icon refresh:
:: We use ie4uinit.exe (icon cache rebuild) without
:: restarting Explorer. If icons do not update
:: immediately, the user may restart Explorer manually.
:: ==========================================

title OpenRGD Environment Setup
echo.
echo  [ OPEN R.G.D. WINDOWS INTEGRATION ]
echo  -----------------------------------
echo.

:: 1. PATH DEFINITIONS
set "REMOTE_ICON_URL=https://raw.githubusercontent.com/OpenRGD/openrgd/main/assets/windows/openrgd.ico"
set "LOCAL_DIR=%USERPROFILE%\.openrgd"
set "LOCAL_ICON=%LOCAL_DIR%\openrgd.ico"

:: 2. ADMIN PRIVILEGE CHECK
net session >nul 2>&1
if %errorlevel%==0 (
    echo  [OK] Administrator privileges detected.
) else (
    echo  [ERROR] Administrator privileges are required.
    echo  Please right-click this file and select "Run as Administrator".
    echo.
    pause
    exit /b 1
)

:: 3. DOWNLOAD ICON
echo.
echo  Creating local environment at: %LOCAL_DIR%
if not exist "%LOCAL_DIR%" mkdir "%LOCAL_DIR%"

echo  Downloading official icon from GitHub...
curl -L -o "%LOCAL_ICON%" "%REMOTE_ICON_URL%" --ssl-no-revoke

if not exist "%LOCAL_ICON%" (
    echo.
    echo  [WARNING] Failed to download icon.
    echo  Proceeding without a custom icon...
) else (
    echo  [OK] Icon downloaded successfully.
)

:: 4. REGISTRY REGISTRATION
echo.
echo  Registering .rgd file extension...

reg add "HKCR\.rgd" /ve /t REG_SZ /d "OpenRGD.Bundle" /f >nul
reg add "HKCR\.rgd" /v "Content Type" /t REG_SZ /d "application/x-zip-compressed" /f >nul
reg add "HKCR\.rgd" /v "PerceivedType" /t REG_SZ /d "compressed" /f >nul

reg add "HKCR\OpenRGD.Bundle" /ve /t REG_SZ /d "OpenRGD Robot Graph" /f >nul
reg add "HKCR\OpenRGD.Bundle\CLSID" /ve /t REG_SZ /d "{E88DCCE0-B7B3-11d1-A9F0-00AA0060FA31}" /f >nul

if exist "%LOCAL_ICON%" (
    reg add "HKCR\OpenRGD.Bundle\DefaultIcon" /ve /t REG_SZ /d "%LOCAL_ICON%" /f >nul
)

:: 5. ICON REFRESH (NO EXPLORER RESTART)
echo.
echo  Refreshing icon cache...
ie4uinit.exe -show >nul 2>&1

echo.
echo  -----------------------------------
echo  [SUCCESS] OpenRGD is now installed!
echo  File type: .rgd → OpenRGD Robot Graph
echo  Custom icon applied (if available).
echo.
echo  If icons do not refresh immediately,
echo  restart Explorer manually.
echo  -----------------------------------
echo.
pause
endlocal
