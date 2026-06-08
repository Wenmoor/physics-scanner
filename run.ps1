Set-Location $PSScriptRoot
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "正在创建虚拟环境并安装依赖..."
    python -m venv .venv
    & .\.venv\Scripts\pip install -r requirements.txt
}
& .\.venv\Scripts\streamlit run app.py
