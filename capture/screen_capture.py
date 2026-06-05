"""
屏幕捕获模块
使用 mss 库高效截取屏幕（Windows 优化）
支持全屏/活动窗口模式
"""

import mss
import mss.tools
import numpy as np
from PIL import Image
import threading
import time
from datetime import datetime


class ScreenCapture:
    """屏幕捕获器"""

    def __init__(self, config: dict):
        self.config = config
        self.interval = config.get("捕获间隔", 3)
        self.mode = config.get("捕获模式", "活动窗口")
        self.max_width = config.get("最大宽度", 1280)
        self.detect_change = config.get("检测变化", True)

        self._running = False
        self._latest_frame = None
        self._previous_frame = None
        self._thread = None
        self._sct = mss.mss()
        self._on_frame_callback = None

    def start(self):
        """开始捕获屏幕"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        print(f"[截屏] 已启动 (间隔: {self.interval}s, 模式: {self.mode})")

    def stop(self):
        """停止捕获"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)

    def _capture_loop(self):
        """捕获循环"""
        while self._running:
            try:
                frame = self._capture()
                if frame is not None:
                    should_process = True
                    if self.detect_change and self._previous_frame is not None:
                        should_process = self._has_significant_change(frame)

                    if should_process:
                        self._latest_frame = frame
                        self._previous_frame = frame
                        if self._on_frame_callback:
                            self._on_frame_callback(frame)
            except Exception as e:
                print(f"[截屏] 捕获异常: {e}")

            time.sleep(self.interval)

    def _capture(self) -> Image.Image:
        """截取屏幕"""
        monitor = self._sct.monitors[1]  # 主显示器
        sct_img = self._sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

        # 缩放以降低分辨率
        if img.width > self.max_width:
            ratio = self.max_width / img.width
            new_size = (self.max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        return img

    def _has_significant_change(self, current: Image.Image, threshold: float = 15.0) -> bool:
        """检测画面是否有显著变化"""
        if self._previous_frame is None:
            return True

        curr_arr = np.array(current.resize((160, 90)), dtype=float)
        prev_arr = np.array(self._previous_frame.resize((160, 90)), dtype=float)
        diff = np.mean(np.abs(curr_arr - prev_arr))
        return diff > threshold

    def get_latest_frame(self):
        """获取最新一帧截图"""
        return self._latest_frame

    def set_frame_callback(self, callback):
        """设置帧回调"""
        self._on_frame_callback = callback
