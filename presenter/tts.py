"""
TTS 语音合成 - 让角色开口说话
使用 edge-tts（免费，自然，离线可用）
"""

import threading
import queue


class TTSEngine:
    """语音合成引擎"""

    def __init__(self, config: dict, character_name: str = "助手"):
        self.config = config
        self.engine_type = config.get("TTS引擎", "edge-tts")
        self.character_name = character_name
        self._speaking = False
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._speak_worker, daemon=True)
        self._thread.start()

    def _speak_worker(self):
        """后台语音工作线程"""
        while True:
            text = self._queue.get()
            if text is None:
                break
            self._speaking = True
            try:
                self._synthesize(text)
            except Exception as e:
                print(f"[TTS] 播放失败: {e}")
            finally:
                self._speaking = False

    def _synthesize(self, text: str):
        """合成并播放语音"""
        if self.engine_type == "edge-tts":
            import edge_tts
            import asyncio
            import tempfile
            import os

            async def _tts():
                communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tmp_path = f.name
                await communicate.save(tmp_path)
                self._play_audio(tmp_path)
                try:
                    os.unlink(tmp_path)
                except:
                    pass

            asyncio.run(_tts())
        else:
            # 回退方案：使用系统 TTS
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()

    def _play_audio(self, file_path: str):
        """播放音频文件"""
        try:
            import platform
            if platform.system() == "Windows":
                import winsound
                winsound.PlaySound(file_path, winsound.SND_FILENAME)
            else:
                import subprocess
                subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path],
                             capture_output=True, timeout=60)
        except Exception as e:
            print(f"[TTS] 播放异常: {e}")

    def speak(self, text: str):
        """说话（添加到队列）"""
        if text and self._queue:
            self._queue.put(text)

    def stop(self):
        """停止播放"""
        self._queue.put(None)

    def is_speaking(self) -> bool:
        """是否正在说话"""
        return self._speaking
