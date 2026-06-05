# 桌面伴侣 - 设计文档

## 概述
一个有 VRM 3D 形象的 AI 桌面伙伴，能看见屏幕画面、听懂语音，像朋友一样陪伴用户。

## 核心架构（三层）

### 捕获层 (Capture Layer)
- **屏幕捕获**: mss 库定时截屏（1-3秒/帧），检测画面变化才发送给 AI
- **摄像头**: OpenCV 可选开启，捕获用户表情
- **Windows Graphics Capture**: 后续升级方向（OBS 同款 API，硬件加速）

### AI 理解层 (AI Layer)
- **LLM**: DeepSeek Chat 对话引擎（OpenAI 兼容 API）
- **VLM**: DeepSeek-VL 视觉理解（图像分析）
- **ASR**: SpeechRecognition + Google 引擎（中文语音识别）
- **记忆**: 本地 JSON 滑动窗口（最近 50 轮对话）

### 表现层 (Presentation Layer)
- **VRM 3D 角色**: PyQt6 + QWebEngineView + Three.js + @pixiv/three-vrm
- **透明悬浮窗**: 无边框、背景透明、始终置顶、右下角吸附
- **TTS**: edge-tts（微软免费 TTS，自然中文发音）
- **对话气泡**: 角色说话时显示文字气泡

## 核心功能

| 功能 | 状态 |
|------|------|
| 3D 角色显示（Three.js + VRM） | ✅ 基础版（占位模型） |
| 真实 VRM 模型加载 | 🔄 待实现 |
| 屏幕捕获 → AI 理解 | ✅ 基础版 |
| 语音输入 → 文字 | ✅ 基础版 |
| AI 对话回复 | ✅ 基础版 |
| 语音回复（TTS） | ✅ 基础版 |
| 对话记忆 | ✅ 基础版 |
| 表情/口型同步 | 🔄 待完善 |
| 透明悬浮窗 | ✅ 基础版 |
| 主动搭话 | ✅ 基础版 |
| 配置界面 | ❌ 待实现 |

## 技术栈
- Python 3.10+ / PyQt6 / QWebEngineView
- Three.js + @pixiv/three-vrm
- DeepSeek API / edge-tts / SpeechRecognition
- mss / OpenCV / Pillow

## 无 GPU 优化策略
- 使用云端 API（DeepSeek）而非本地模型
- mss 库硬件加速截图，CPU 占用低
- Three.js WebGL 渲染在 CPU 上也能运行
- 截图缩放（1280px 上限）+ 画面变化检测减少 API 调用

## 待整合的开源工具
- **Amica**: VRM 模型加载与表情系统参考
- **AIMouto**: 情绪状态切换参考（5种情绪）
- **MCP Screenshot Server**: mss 截图最佳实践
