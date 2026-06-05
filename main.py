"""
桌面伴侣 - AI 桌面伙伴主入口
一个能看到你的屏幕、和你语音聊天的 3D 桌面角色
"""

import sys
import json
import os
import threading
import time
import queue
from pathlib import Path


class DesktopCompanionApp:
    """桌面伴侣主应用"""

    def __init__(self):
        self.config = self._load_config()
        self.running = True
        self.message_queue = queue.Queue()

        # 模块引用（启动后初始化）
        self.vrm_window = None
        self.capture = None
        self.camera = None
        self.asr = None
        self.tts = None
        self.llm = None
        self.vlm = None
        self.memory = None

    def _load_config(self):
        """加载配置文件"""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        print("[配置] 未找到 config.json，使用默认配置")
        return {}

    def initialize(self):
        """初始化所有模块"""
        print("[启动] 正在启动桌面伴侣...")
        print(f"[启动] 角色名称: {self.config.get('角色设定', {}).get('名称', '未知')}")

        self._init_ai_modules()
        self._init_capture_modules()
        self._init_voice_modules()
        self._init_vrm_window()

        print("[启动] 所有模块初始化完成！")

    def _init_ai_modules(self):
        """初始化AI模块"""
        from ai.llm import LLMEngine
        from ai.vlm import VLMEngine
        from ai.memory import MemoryManager

        model_config = self.config.get("模型配置", {})
        self.llm = LLMEngine(model_config)
        self.vlm = VLMEngine(model_config)
        self.memory = MemoryManager(self.config.get("记忆", {}))

        print("[AI] LLM + VLM + 记忆模块就绪")

    def _init_capture_modules(self):
        """初始化捕获模块"""
        capture_cfg = self.config.get("屏幕捕获", {})
        camera_cfg = self.config.get("摄像头", {})

        if capture_cfg.get("启用", False):
            from capture.screen_capture import ScreenCapture
            self.capture = ScreenCapture(capture_cfg)
            self.capture.start()
            print("[捕获] 屏幕捕获已启动")

        if camera_cfg.get("启用", False):
            from capture.camera import CameraCapture
            self.camera = CameraCapture(camera_cfg)
            self.camera.start()
            print("[捕获] 摄像头已启动")

    def _init_voice_modules(self):
        """初始化语音模块"""
        from ai.asr import ASREngine
        from presenter.tts import TTSEngine

        voice_cfg = self.config.get("语音", {})
        character_name = self.config.get("角色设定", {}).get("名称", "助手")

        self.tts = TTSEngine(voice_cfg, character_name)

        # ASR 语音识别（后台监听，有语音时自动处理）
        self.asr = ASREngine(voice_cfg)
        if voice_cfg.get("ASR引擎", "本地") != "关闭":
            try:
                self.asr.start_listening(callback=self._on_voice_input)
                print("[语音] 语音识别已启动（对着麦克风说话即可）")
            except Exception as e:
                print(f"[语音] 语音识别启动失败（可打字交互）: {e}")

        print("[语音] TTS 模块就绪")

    def _on_voice_input(self, text: str):
        """收到语音输入回调"""
        self.message_queue.put({"type": "voice_input", "text": text})

    def _init_vrm_window(self):
        """初始化VRM悬浮窗"""
        from presenter.vrm_window import VRMWindow

        vrm_cfg = self.config.get("VRM模型", {})
        character_name = self.config.get("角色设定", {}).get("名称", "助手")
        character_personality = self.config.get("角色设定", {}).get("性格", "")

        self.vrm_window = VRMWindow(
            config=vrm_cfg,
            character_name=character_name,
            character_personality=character_personality
        )

        print("[VRM] 3D角色窗口就绪")

    def run(self):
        """运行主循环"""
        self.initialize()
        print("\n✨ 桌面伴侣已启动！")
        print("💡 直接对着麦克风说话，或在终端输入文字按回车")
        print("💡 输入 /quit 退出")

        # 启动后台处理线程
        bg_thread = threading.Thread(target=self._background_loop, daemon=True)
        bg_thread.start()

        # 启动终端文字输入线程（作为语音的补充）
        input_thread = threading.Thread(target=self._console_input_loop, daemon=True)
        input_thread.start()

        # 启动 PyQt 事件循环（主线程）
        if self.vrm_window:
            self.vrm_window.show()
            from PyQt6.QtWidgets import QApplication
            return QApplication.instance().exec()

        return 0

    def _console_input_loop(self):
        """终端文字输入循环（语音识别的后备方案）"""
        while self.running:
            try:
                user_input = input()
                if user_input.strip():
                    if user_input.strip() == "/quit":
                        self.shutdown()
                        break
                    self.message_queue.put({"type": "text_input", "text": user_input.strip()})
            except (EOFError, KeyboardInterrupt):
                break
            except Exception:
                time.sleep(0.5)

    def _background_loop(self):
        """后台处理循环"""
        while self.running and self.vrm_window and self.vrm_window.isVisible():
            time.sleep(0.1)
            try:
                message = self.message_queue.get_nowait()
                self._handle_message(message)
            except queue.Empty:
                pass

    def _handle_message(self, message):
        """处理消息"""
        msg_type = message.get("type", "")
        if msg_type == "voice_input":
            self._process_voice_input(message.get("text", ""))
        elif msg_type == "text_input":
            self._process_text_input(message.get("text", ""))

    def _process_voice_input(self, text):
        """处理语音输入"""
        print(f"[用户] {text}")
        if self.vrm_window:
            self.vrm_window.show_thinking()
        self._generate_response(text)

    def _process_text_input(self, text):
        """处理文字输入"""
        print(f"[用户] {text}")
        if self.vrm_window:
            self.vrm_window.show_thinking()
        self._generate_response(text)

    def _generate_response(self, text):
        """生成回复"""
        try:
            # 获取最近画面（如果有）
            image_context = None
            if self.capture:
                screenshot = self.capture.get_latest_frame()
                if screenshot:
                    image_context = screenshot

            # 构建对话上下文
            history = self.memory.get_history()

            # 先用 VLM 分析画面（如果有截图且视觉模块可用）
            screen_desc = None
            if image_context is not None and self.vlm and self.vlm.is_available():
                screen_desc = self.vlm.describe_image(image_context, "请简要描述这个屏幕上发生了什么")
                print(f"[视觉] 画面分析: {screen_desc[:100]}...")

            # 文字回复（带画面描述作为上下文）
            extra_context = f"【当前屏幕画面】{screen_desc}" if screen_desc else None
            response = self.llm.chat(text, history, image_context)

            # 如果画面有变化且VLM可用，让角色主动提及
            if screen_desc:
                response = response  # LLM已看到图片，不需额外处理

            print(f"[{self.config.get('角色设定', {}).get('名称', '助手')}] {response}")

            # 隐藏思考状态
            if self.vrm_window:
                self.vrm_window.hide_thinking()

            # 保存记忆
            self.memory.add(text, response)

            # 更新VRM角色 + 语音播放
            if self.vrm_window:
                self.vrm_window.speak(response)
            self.tts.speak(response)

        except Exception as e:
            print(f"[错误] 生成回复失败: {e}")
            if self.vrm_window:
                self.vrm_window.hide_thinking()
                self.vrm_window.speak("唔，我刚才走神了，你再说一遍？")

    def shutdown(self):
        """关闭所有模块"""
        print("\n[关闭] 正在关闭桌面伴侣...")
        self.running = False

        if self.capture:
            self.capture.stop()
        if self.camera:
            self.camera.stop()

        if self.vrm_window:
            self.vrm_window.close()

        print("[关闭] 已安全退出")


def main():
    """程序入口"""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("桌面伴侣")

    companion = DesktopCompanionApp()

    try:
        exit_code = companion.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        companion.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
