# -*- coding: utf-8 -*-
from __future__ import print_function

import configparser
import os
import sys

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.ini")
)

CONFIG_BASE_DIR = os.path.dirname(CONFIG_PATH)


def _load_config():
    """Load config.ini, return dict with LLM settings and paths."""
    config = {
        "provider": "",
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "max_tokens": 4096,
        "temperature": 0.3,
        "group_template_dir": os.path.join(CONFIG_BASE_DIR, "..", "..", "Resources", "GroupTemplate"),
        "feature_template_file": os.path.join("..", "Resources", "FeatureTemplate", "FeatureTemplate.xml"),
        "autoidentify_with_direction_dir": os.path.join("..", "Resources", "AutoIdentifyWithDirection"),
    }
    if not os.path.exists(CONFIG_PATH):
        return config
    try:
        cp = configparser.ConfigParser()
        cp.read(CONFIG_PATH, encoding="utf-8-sig")
        if cp.has_section("LLM"):
            config["provider"] = cp.get("LLM", "provider", fallback="")
            config["api_key"] = cp.get("LLM", "api_key", fallback="")
            config["base_url"] = cp.get("LLM", "base_url", fallback=config["base_url"])
            config["model"] = cp.get("LLM", "model", fallback=config["model"])
            config["max_tokens"] = cp.getint("LLM", "max_tokens", fallback=config["max_tokens"])
            config["temperature"] = cp.getfloat("LLM", "temperature", fallback=config["temperature"])
        if cp.has_section("Paths"):
            config["group_template_dir"] = cp.get(
                "Paths", "group_template_dir", fallback=config["group_template_dir"]
            )
            config["autoidentify_with_direction_dir"] = cp.get(
                "Paths", "autoidentify_with_direction_dir", fallback=config["autoidentify_with_direction_dir"]
            )
            config["feature_template_file"] = cp.get(
                "Paths", "feature_template_file", fallback=config["feature_template_file"]
            )
    except Exception as exc:
        sys.stderr.write("[config] load error: %s\n" % exc)
    return config


def _is_llm_config_enabled(config):
    return bool(config.get("api_key") and config.get("api_key") != "YOUR_API_KEY_HERE")


def _mask_secret(value):
    value = value or ""
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


def _public_llm_config():
    return {
        "provider": CONFIG.get("provider", ""),
        "base_url": CONFIG.get("base_url", ""),
        "model": CONFIG.get("model", ""),
        "max_tokens": CONFIG.get("max_tokens", 4096),
        "temperature": CONFIG.get("temperature", 0.3),
        "llm_enabled": _is_llm_config_enabled(CONFIG),
        "api_key_set": bool(CONFIG.get("api_key")),
        "api_key_masked": _mask_secret(CONFIG.get("api_key", "")),
        "config_path": os.path.abspath(CONFIG_PATH),
    }


def _parse_int_field(data, name, default, min_value, max_value):
    raw = data.get(name, default)
    try:
        value = int(raw)
    except Exception:
        raise ValueError(u"%s \u5fc5\u987b\u662f\u6574\u6570" % name)
    if value < min_value or value > max_value:
        raise ValueError(u"%s \u5fc5\u987b\u5728 %d \u5230 %d \u4e4b\u95f4" % (name, min_value, max_value))
    return value


def _parse_float_field(data, name, default, min_value, max_value):
    raw = data.get(name, default)
    try:
        value = float(raw)
    except Exception:
        raise ValueError(u"%s \u5fc5\u987b\u662f\u6570\u5b57" % name)
    if value < min_value or value > max_value:
        raise ValueError(u"%s \u5fc5\u987b\u5728 %.2f \u5230 %.2f \u4e4b\u95f4" % (name, min_value, max_value))
    return value


def _save_llm_config(data):
    global CONFIG, LLM_ENABLED

    provider = (data.get("provider", CONFIG.get("provider", "")) or "").strip()
    base_url = (data.get("base_url", CONFIG.get("base_url", "")) or "").strip().rstrip("/")
    model = (data.get("model", CONFIG.get("model", "")) or "").strip()
    if not base_url:
        raise ValueError(u"base_url \u4e0d\u80fd\u4e3a\u7a7a")
    if not (base_url.startswith("http://") or base_url.startswith("https://")):
        raise ValueError(u"base_url \u5fc5\u987b\u4ee5 http:// \u6216 https:// \u5f00\u5934")
    if not model:
        raise ValueError(u"model \u4e0d\u80fd\u4e3a\u7a7a")

    max_tokens = _parse_int_field(data, "max_tokens", CONFIG.get("max_tokens", 4096), 1, 200000)
    temperature = _parse_float_field(data, "temperature", CONFIG.get("temperature", 0.3), 0.0, 2.0)

    api_key = CONFIG.get("api_key", "")
    if data.get("clear_api_key"):
        api_key = ""
    elif "api_key" in data and str(data.get("api_key") or "").strip():
        api_key = str(data.get("api_key") or "").strip()

    cp = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        cp.read(CONFIG_PATH, encoding="utf-8-sig")
    if not cp.has_section("LLM"):
        cp.add_section("LLM")
    cp.set("LLM", "provider", provider)
    cp.set("LLM", "api_key", api_key)
    cp.set("LLM", "base_url", base_url)
    cp.set("LLM", "model", model)
    cp.set("LLM", "max_tokens", str(max_tokens))
    cp.set("LLM", "temperature", str(temperature))

    config_dir = os.path.dirname(CONFIG_PATH)
    if config_dir and not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    with open(CONFIG_PATH, "w", encoding="utf-8") as fp:
        cp.write(fp)

    CONFIG = _load_config()
    LLM_ENABLED = _is_llm_config_enabled(CONFIG)
    return _public_llm_config()


CONFIG = _load_config()
LLM_ENABLED = _is_llm_config_enabled(CONFIG)

# 分组模板保存目录：相对路径（相对 config.ini），加载时已规范化为绝对路径
# 用户在 XML 编辑器中显式点击保存时，模板 XML 才会写入此目录。
# 3DMPS 主程序启动时扫描该目录，写入后下次打开 3DMPS 即可看到新模板。
GROUP_TEMPLATE_SAVE_DIR = os.path.normpath(
    os.path.join(CONFIG_BASE_DIR, CONFIG["group_template_dir"])
)

AUTOIDENTIFY_WITH_DIRECTION_DIR = os.path.normpath(
    os.path.join(CONFIG_BASE_DIR, CONFIG["autoidentify_with_direction_dir"])
)

FEATURE_TEMPLATE_FILE = os.path.normpath(
    os.path.join(CONFIG_BASE_DIR, CONFIG["feature_template_file"])
)

# ============================================
# 工具调用配置（魔法数字集中管理）
# ============================================

# 对话框轮询配置（模板列表读取等）
DIALOG_POLL_MAX_ATTEMPTS = 20       # 最大轮询次数
DIALOG_POLL_INTERVAL_SEC = 0.25     # 轮询间隔（秒）
DIALOG_POLL_TIMEOUT_SEC = DIALOG_POLL_MAX_ATTEMPTS * DIALOG_POLL_INTERVAL_SEC  # 总超时约5秒

# 管道调用配置
PIPE_CONNECT_TIMEOUT_MS = 3000      # 连接超时（毫秒）
PIPE_CONNECT_RETRY_COUNT = 2        # 连接重试次数
PIPE_CONNECT_RETRY_DELAY = 0.5       # 重试间隔（秒）
PIPE_DEFAULT_TIMEOUT_SEC = 30.0     # 默认调用超时（秒）

# LLM 对话配置
LLM_MAX_TOOL_ITERATIONS = 5         # 最大工具调用迭代次数
LLM_STREAM_TIMEOUT_SEC = 120        # LLM API 调用超时（秒）
