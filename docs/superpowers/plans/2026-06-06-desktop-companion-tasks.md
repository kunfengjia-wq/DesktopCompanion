# 桌面伴侣 - 实施任务计划

## 任务 1: VRM 真实模型加载
- **描述**: 将占位角色升级为真正的 VRM 模型加载
- **文件**: presenter/webview/index.html, presenter/webview/vrm_controller.js
- **要求**:
  - 使用 @pixiv/three-vrm 加载 .vrm 文件
  - 支持 VRM 1.0 和 VRM 0.x 格式
  - 眨眼、呼吸、头部追踪动画
  - 口型同步（说话时张嘴）
  - 对话气泡显示
  - 回退方案：模型加载失败时显示占位角色

## 任务 2: Windows Graphics Capture 屏幕捕获
- **描述**: 实现 OBS 风格的硬件加速屏幕捕获
- **文件**: capture/screen_capture.py
- **要求**:
  - 使用 dxcam 或 mss 高速截图
  - 支持指定窗口捕获（活动窗口）
  - 画面变化检测（避免重复发送）
  - 低 CPU 占用
  - 配置化：捕获间隔、输出分辨率、变化灵敏度

## 任务 3: DeepSeek API 联调
- **描述**: 测试并修复 DeepSeek API 集成
- **文件**: ai/llm.py, ai/vlm.py
- **要求**:
  - 验证 API Key 可用
  - 修复对话流程中的错误
  - 测试带图片的视觉问答
  - 添加错误重试和超时处理

## 任务 4: 语音模块完善
- **描述**: 调试 ASR 和 TTS 模块
- **文件**: ai/asr.py, presenter/tts.py
- **要求**:
  - ASR: 中文语音识别测试
  - TTS: edge-tts 中文语音测试
  - ASR/TTS 线程安全
  - 语音打断支持

## 任务 5: 配置界面
- **描述**: 创建 PyQt6 设置窗口
- **文件**: ui/settings_window.py
- **要求**:
  - API Key 配置（加密存储）
  - 角色名称/性格设置
  - 捕获参数调节
  - 语音开关
  - 窗口位置/大小记忆

## 任务 6: GitHub 仓库初始化
- **描述**: 创建 GitHub 远程仓库并推送
- **要求**:
  - 在 kunfengjia-wq 账号下创建 DesktopCompanion 仓库
  - 推送所有代码
  - 配置 .gitignore
