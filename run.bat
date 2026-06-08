@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo 正在创建虚拟环境并安装依赖...
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt
)
.venv\Scripts\streamlit run app.py
