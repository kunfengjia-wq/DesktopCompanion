# 🎀 桌面伴侣 - AI Desktop Companion

一个拥有 **3D 角色形象**的 AI 桌面伙伴，能看到你的屏幕、听懂你的声音，像朋友一样陪伴你。

## ✨ 功能

| 功能 | 说明 |
|------|------|
| 🎭 **3D 角色** | 透明悬浮窗，始终置顶，可换 VRM 模型 |
| 👁️ **屏幕感知** | 角色能"看到"你的屏幕画面 |
| 🎤 **语音对话** | 直接说话聊天，不需要打字 |
| 📹 **摄像头** | 可选，角色能看到你的表情 |
| 🧠 **DeepSeek** | 使用 DeepSeek-VL 多模态模型 |
| 💬 **记忆** | 记得之前的对话 |
| 🎵 **语音回复** | 用自然语音回答你 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config.json`，填入你的 DeepSeek API 密钥：

```json
{
  "模型配置": {
    "API密钥": "你的 API Key 在这里",
    "API地址": "https://api.deepseek.com"
  }
}
```

### 3. 启动

双击 `start.bat`，或者：

```bash
python main.py
```

## 🎭 更换 VRM 模型

1. 下载 `.vrm` 格式的 3D 模型
2. 放到 `presenter/webview/models/` 目录
3. 修改 `config.json` 中的 `VRM模型.模型文件` 路径

推荐免费模型来源：
- [Open Source Avatars](https://www.opensourceavatars.com/) (CC0 协议)
- [VRoid Hub](https://hub.vroid.com/)

## ⚙️ 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `屏幕捕获.捕获间隔` | 每隔X秒截屏一次 | 3秒 |
| `语音.ASR引擎` | 语音识别引擎 | 本地 |
| `语音.TTS引擎` | 语音合成引擎 | edge-tts |
| `VRM模型.透明模式` | 窗口背景透明 | true |
| `VRM模型.始终置顶` | 窗口保持在最前 | true |

## 🖥️ 最低配置

- **CPU**: 双核 2.0GHz+
- **内存**: 4GB
- **显卡**: 不需要独立 GPU（使用 CPU 渲染）
- **系统**: Windows 10/11

## 📁 项目结构

```
DesktopCompanion/
├── main.py                  # 主入口
├── config.json              # 配置文件
├── capture/                 # 屏幕/摄像头捕获
│   ├── screen_capture.py
│   └── camera.py
├── ai/                      # AI 模块
│   ├── llm.py              # 对话引擎
│   ├── vlm.py              # 视觉理解
│   ├── asr.py              # 语音识别
│   └── memory.py           # 记忆管理
├── presenter/               # 表现层
│   ├── vrm_window.py       # VRM 悬浮窗
│   ├── tts.py              # 语音合成
│   └── webview/            # 3D 渲染页面
├── agent/                   # 智能体工具
└── data/                    # 数据存储
```

## 📜 许可证

MIT License
