"""
ASR 语音识别 - 让角色听懂你说什么
使用 SpeechRecognition 库（离线/云端多引擎）
"""

import queue
import threading
import time


class ASREngine:
    """语音识别引擎"""

    def __init__(self, config: dict):
        self.config = config
        self.engine = config.get("ASR引擎", "本地")
        self.wake_word = config.get("语音唤醒", False)
        self.interrupt = config.get("语音打断", True)
        self._listening = False
        self._audio_queue = queue.Queue()
        self._thread = None

    def start_listening(self, callback):
        """开始监听语音输入"""
        if self._listening:
            return

        self._listening = True
        self._callback = callback

        def listen_loop():
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.pause_threshold = 0.8
            recognizer.energy_threshold = 300

            try:
                mic = sr.Microphone()
                with mic as source:
                    print("[ASR] 正在校准麦克风...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("[ASR] 麦克风就绪，开始监听")
            except Exception as e:
                print(f"[ASR] 麦克风初始化失败: {e}")
                return

            while self._listening:
                try:
                    with mic as source:
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    text = None
                    try:
                        text = recognizer.recognize_google(audio, language="zh-CN")
                    except sr.RequestError:
                        # Google API 可能被墙，尝试本地 sphinx 或跳过
                        try:
                            text = recognizer.recognize_sphinx(audio, language="zh-CN")
                        except:
                            pass

                    if text and text.strip() and self._callback:
                        print(f"[ASR] 识别: {text}")
                        self._callback(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"[ASR] 识别异常: {e}")
                    time.sleep(1)

        self._thread = threading.Thread(target=listen_loop, daemon=True)
        self._thread.start()

    def stop_listening(self):
        """停止监听"""
        self._listening = False
        if self._thread:
            self._thread.join(timeout=2)
