"""
主动感知模块
根据时间、屏幕内容变化等主动发起对话
"""

import time
from datetime import datetime


class ProactiveEngine:
    """主动搭话引擎"""

    def __init__(self, config: dict, on_speak_callback):
        self.config = config
        self.interval = config.get("主动搭话间隔", 120)
        self.on_speak = on_speak_callback
        self._last_active = time.time()
        self._last_greeting = ""

    def check_triggers(self, screen_changed: bool = False, user_active: bool = True):
        """检查是否需要主动说话"""
        now = time.time()
        elapsed = now - self._last_active

        # 长时间沉默
        if elapsed > self.interval and not user_active:
            self._trigger_idle_chat()

        # 屏幕变化
        if screen_changed:
            self._last_active = now

    def _trigger_idle_chat(self):
        """触发闲聊"""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            msg = "早上好呀~今天有什么计划吗？"
        elif 12 <= hour < 14:
            msg = "中午啦，记得吃饭哦！"
        elif 14 <= hour < 18:
            msg = "下午好~要不要休息一下？"
        elif 18 <= hour < 22:
            msg = "晚上好呀，今天过得怎么样？"
        else:
            msg = "这么晚还不睡呀..."

        if msg != self._last_greeting:
            self.on_speak(msg)
            self._last_greeting = msg

        self._last_active = time.time()
