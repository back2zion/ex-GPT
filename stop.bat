@echo off
echo === ex-GPT ??? ?? ===
echo.

echo  ?? ???? ???? ?...
docker-compose down

if %errorlevel% equ 0 (
    echo ? ?? ???? ???????.
) else (
    echo ? ??? ?? ? ??? ??????.
)

echo.
pause
