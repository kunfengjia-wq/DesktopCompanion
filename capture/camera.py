"""
摄像头捕获模块
使用 OpenCV 从摄像头获取画面
"""

import cv2
import numpy as np
from PIL import Image
import threading
import time


class CameraCapture:
    """摄像头捕获器"""

    def __init__(self, config: dict):
        self.config = config
        self.device_id = config.get("设备ID", 0)
        self._running = False
        self._cap = None
        self._latest_frame = None
        self._thread = None
        self._on_frame_callback = None

    def start(self):
        """打开摄像头并开始捕获"""
        if self._running:
            return

        try:
            self._cap = cv2.VideoCapture(self.device_id)
            if not self._cap.isOpened():
                print("[摄像头] 无法打开摄像头")
                return

            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self._running = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            print("[摄像头] 已启动")
        except Exception as e:
            print(f"[摄像头] 初始化失败: {e}")

    def stop(self):
        """关闭摄像头"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._cap:
            self._cap.release()

    def _capture_loop(self):
        """捕获循环"""
        while self._running:
            try:
                ret, frame = self._cap.read()
                if ret:
                    # BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    self._latest_frame = pil_img
                    if self._on_frame_callback:
                        self._on_frame_callback(pil_img)
            except Exception as e:
                print(f"[摄像头] 读取失败: {e}")

            time.sleep(1)

    def get_latest_frame(self) -> Image.Image:
        """获取最新帧"""
        return self._latest_frame

    def set_frame_callback(self, callback):
        """设置帧回调"""
        self._on_frame_callback = callback
