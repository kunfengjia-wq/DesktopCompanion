"""
VLM 视觉识别引擎 - 让角色看到屏幕/摄像头画面
支持多个视觉提供商：
- DeepSeek (通过 OpenAI 兼容 API，可能不支持视觉)
- Gemini (Google Generative Language API)
"""

import base64
from io import BytesIO
import numpy as np
from PIL import Image


class VLMEngine:
    """视觉语言模型引擎 - 分析图像内容"""

    def __init__(self, config: dict):
        self.config = config
        self.provider = config.get("视觉提供商", "")

        # 检查 DeepSeek 是否支持视觉（官方 API 目前不支持）
        self.ds_client = None
        ds_key = config.get("API密钥", "")
        if ds_key:
            from openai import OpenAI
            self.ds_client = OpenAI(api_key=ds_key, base_url=config.get("API地址", "https://api.deepseek.com"))

        # Gemini 视觉配置
        self.gemini_key = config.get("视觉API密钥", "")
        self.gemini_model = config.get("视觉模型名称", "gemini-2.0-flash-exp")
        self._gemini_available = bool(self.gemini_key)

        # 自动检测可用视觉提供商
        self._vision_available = self._check_vision_support()
        if not self._vision_available:
            print("[VLM] 未配置视觉模型，屏幕分析功能不可用")
            print("[VLM] 如需视觉功能，请在 config.json 中配置 视觉API密钥 (Gemini API Key)")

    def _check_vision_support(self) -> bool:
        """检查是否有可用的视觉提供商"""
        return self._gemini_available

    def describe_image(self, image, prompt: str = "请描述这张图片里有什么") -> str:
        """描述图像内容"""
        if not self._vision_available:
            return ""

        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # 尝试 Gemini
        if self._gemini_available:
            return self._describe_with_gemini(image, prompt)

        return ""

    def _describe_with_gemini(self, image, prompt: str) -> str:
        """使用 Gemini 进行图像分析"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel(self.gemini_model)

            # 准备图片
            buf = BytesIO()
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(buf, format="JPEG", quality=60)
            img_data = buf.getvalue()

            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_data}
            ])
            return response.text.strip() if response.text else ""

        except Exception as e:
            print(f"[VLM] Gemini 分析失败: {e}")
            return ""

    def detect_change(self, current_image, previous_image, threshold: float = 0.1) -> bool:
        """检测画面是否有显著变化"""
        if current_image is None or previous_image is None:
            return True

        if isinstance(current_image, Image.Image):
            current_arr = np.array(current_image.resize((128, 72)))
        else:
            current_arr = np.array(current_image)

        if isinstance(previous_image, Image.Image):
            prev_arr = np.array(previous_image.resize((128, 72)))
        else:
            prev_arr = np.array(previous_image)

        diff = np.mean(np.abs(current_arr.astype(float) - prev_arr.astype(float)))
        return diff > threshold * 255

    def is_available(self) -> bool:
        """视觉模块是否可用"""
        return self._vision_available
