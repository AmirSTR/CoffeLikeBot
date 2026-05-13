@echo off
echo Installing dependencies with increased timeout...
pip install -r requirements.txt --timeout 120 --retries 5 -i https://pypi.org/simple/
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Primary mirror failed. Trying alternative mirror...
    pip install -r requirements.txt --timeout 120 --retries 5 -i https://mirrors.aliyun.com/pypi/simple/
)
echo Done.
pause
