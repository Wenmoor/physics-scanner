import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from config import settings
from services.extractor import process_images
from services.user_settings import load_user_settings, save_user_settings

st.set_page_config(
    page_title="物理错题整理助手",
    page_icon="📐",
    layout="wide",
)

if "user_cfg" not in st.session_state:
    st.session_state.user_cfg = load_user_settings()

# 环境变量 / Streamlit Secrets 作为首次使用的默认值（不覆盖已保存的本地配置）
_env_key = settings.dashscope_api_key
if _env_key and not st.session_state.user_cfg.get("dashscope_api_key"):
    st.session_state.user_cfg["dashscope_api_key"] = _env_key
if settings.dashscope_base_url:
    st.session_state.user_cfg.setdefault("dashscope_base_url", settings.dashscope_base_url)
if settings.qwen_vl_model:
    st.session_state.user_cfg.setdefault("qwen_vl_model", settings.qwen_vl_model)

try:
    if st.secrets.get("DASHSCOPE_API_KEY") and not st.session_state.user_cfg.get(
        "dashscope_api_key"
    ):
        st.session_state.user_cfg["dashscope_api_key"] = st.secrets["DASHSCOPE_API_KEY"]
except (FileNotFoundError, AttributeError, KeyError):
    pass

st.title("📐 物理错题整理助手")
st.caption("上传错题照片 → 识别题干与公式 → 生成 B5 单页 Word（宋体五号，自动分配留白）")

with st.sidebar:
    st.header("设置")
    cfg = st.session_state.user_cfg

    provider = st.selectbox(
        "AI 提供商",
        options=["qwen", "mock"],
        format_func=lambda x: "千问多模态 (Qwen-VL)" if x == "qwen" else "演示模式 (无需 API)",
        index=0 if cfg.get("ai_provider", "qwen") == "qwen" else 1,
    )
    api_key = st.text_input(
        "DashScope API Key",
        value=cfg.get("dashscope_api_key", ""),
        type="password",
        help="填写后点击「保存设置」，将保存在本机 .local/user_settings.json",
    )
    base_url = st.text_input(
        "API 地址",
        value=cfg.get(
            "dashscope_base_url",
            "https://dashscope.aliyuncs.com/api/v1",
        ),
        help="国内: dashscope.aliyuncs.com；国际: dashscope-intl.aliyuncs.com",
    )
    model = st.text_input(
        "模型名称",
        value=cfg.get("qwen_vl_model", "qwen-vl-max"),
    )

    if st.button("保存设置", use_container_width=True):
        st.session_state.user_cfg = {
            "ai_provider": provider,
            "dashscope_api_key": api_key.strip(),
            "dashscope_base_url": base_url.strip(),
            "qwen_vl_model": model.strip(),
        }
        save_user_settings(st.session_state.user_cfg)
        st.success("已保存到本机，下次打开自动加载")

    st.divider()
    st.markdown("**排版**")
    st.text("汉字：宋体 五号")
    st.text("公式：Word 原生公式")
    st.text(f"B5：{settings.page_width_mm} × {settings.page_height_mm} mm")

uploaded_files = st.file_uploader(
    "上传错题图片（支持多张，合并为一份 Word）",
    type=["png", "jpg", "jpeg", "webp", "bmp"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.info(f"已选择 {len(uploaded_files)} 张图片")

if st.button("开始整理", type="primary", disabled=not uploaded_files):
    active_cfg = {
        "ai_provider": provider,
        "dashscope_api_key": api_key.strip(),
        "dashscope_base_url": base_url.strip(),
        "qwen_vl_model": model.strip(),
    }
    save_user_settings(active_cfg)
    st.session_state.user_cfg = active_cfg

    settings.output_dir.mkdir(parents=True, exist_ok=True)
    progress = st.progress(0, text="准备处理…")
    tmp_paths: list[Path] = []

    try:
        for uploaded in uploaded_files:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(uploaded.name).suffix
            ) as tmp:
                tmp.write(uploaded.getvalue())
                tmp_paths.append(Path(tmp.name))

        problems, docx_path = process_images(
            image_paths=tmp_paths,
            provider_name=provider,
            api_key=api_key.strip() or None,
            model=model.strip() or None,
            base_url=base_url.strip() or None,
        )

        progress.progress(1.0, text="处理完成")
        st.session_state["results"] = {
            "problems": problems,
            "filenames": [f.name for f in uploaded_files],
            "docx_path": docx_path,
            "error": None,
        }
    except Exception as exc:
        st.session_state["results"] = {
            "problems": None,
            "filenames": [f.name for f in uploaded_files],
            "docx_path": None,
            "error": str(exc),
        }
    finally:
        for p in tmp_paths:
            p.unlink(missing_ok=True)

if "results" in st.session_state:
    result = st.session_state["results"]
    st.divider()

    if result["error"]:
        st.error(result["error"])
    else:
        st.subheader("处理结果")
        for i, (name, problem) in enumerate(
            zip(result["filenames"], result["problems"]), start=1
        ):
            with st.expander(f"第 {i} 题 · {name}", expanded=i == 1):
                for para in problem.paragraphs:
                    line = ""
                    for seg in para:
                        if seg.type == "text":
                            line += seg.value
                        else:
                            line += f"${seg.value}$"
                    st.write(line)
                st.caption(f"预估手写留白权重：{problem.handwriting_lines} 行")

        docx_path: Path = result["docx_path"]
        st.success(f"已生成: `{docx_path}`")
        st.download_button(
            label=f"下载 {docx_path.name}",
            data=docx_path.read_bytes(),
            file_name=docx_path.name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
