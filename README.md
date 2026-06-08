# 物理错题整理助手

上传高中物理错题照片，由 AI（千问多模态）识别题干与公式，排版生成 **B5 单页** Word 文档（宋体五号、Word 原生公式），多题自动分配手写留白。

## 功能

- 上传错题图片，AI 识别文字与公式
- 生成 B5 活页纸 Word，可直接打印
- API Key 在应用内填写，**保存到本机**（`.local/user_settings.json`），下次打开自动加载

## 本地运行

```bash
git clone https://github.com/YOUR_USERNAME/scanner.git
cd scanner

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt

# 启动
run.bat                       # Windows
# streamlit run app.py        # 或手动启动
```

浏览器打开 http://localhost:8501 ，在侧边栏填写 DashScope API Key 并点击 **保存设置**。

> 必须使用虚拟环境启动，否则可能报 `No module named 'pydantic_settings'`。

## 部署到 Streamlit Cloud

1. 将本仓库推送到你的 GitHub
2. 打开 [share.streamlit.io](https://share.streamlit.io)，用 GitHub 登录
3. **New app** → 选择仓库，Main file path 填 `app.py`
4. （推荐）在 **Secrets** 中添加：

```toml
DASHSCOPE_API_KEY = "sk-your-key"
```

5. 点击 Deploy

也可在部署后的应用侧边栏直接填写 API Key（云端会话内有效；Secrets 适合固定 Key）。

## API 配置说明

| 配置项 | 说明 |
|--------|------|
| DashScope API Key | 在[阿里云百炼](https://bailian.console.aliyun.com/)获取 |
| API 地址 | 国内 `https://dashscope.aliyuncs.com/api/v1` |
| | 国际 `https://dashscope-intl.aliyuncs.com/api/v1` |
| 模型 | 默认 `qwen-vl-max`，可换 `qwen-vl-plus` 等 |

本地配置保存在 `.local/user_settings.json`（已加入 `.gitignore`，不会提交到 Git）。

## 技术栈

| 模块 | 选型 |
|------|------|
| 界面 | Streamlit |
| AI | 千问 Qwen-VL (DashScope) |
| 文档 | python-docx |
| 公式 | latex2mathml + OMML |

## 项目结构

```
scanner/
├── app.py
├── config.py
├── run.bat / run.ps1
├── providers/          # AI 提供商（qwen / mock）
├── services/           # 提取、排版、用户配置
└── output/             # 生成的 Word（本地）
```

## 扩展

新增 AI 提供商：实现 `providers/base.py` 中的 `VisionProvider`，在 `providers/__init__.py` 注册即可。
