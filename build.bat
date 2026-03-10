@echo off
chcp 65001 >nul
title AI工具打包程序

echo ========================================
echo     Python Streamlit 工具打包程序
echo ========================================
echo.

echo [1/4] 正在安装 PyInstaller...
python -m pip install pyinstaller --quiet

echo [2/4] 正在安装项目依赖...
python -m pip install streamlit pandas openpyxl requests --quiet

echo [3/4] 正在打包应用（请耐心等待）...
python -m pyinstaller --onefile --windowed --name "AI工具" --clean app.py

echo.
echo [4/4] 打包完成！
echo.

echo 输出目录: dist\
dir dist\*.exe

echo.
echo ========================================
echo 打包完成！可执行文件位于: dist\AI工具.exe
echo ========================================
pause