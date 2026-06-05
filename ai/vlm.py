"""
VLM 视觉识别引擎 - 让角色看到屏幕/摄像头画面
使用 DeepSeek-VL 等视觉理解模型
"""

import base64
from io import BytesIO
from openai import OpenAI


class VLMEngine:
    """视觉语言模型引擎 - 分析图像内容"""

    def __init__(self, config: dict):
        self.config = config
        self.api_key = config.get("API密钥", "")
        self.api_base = config.get("API地址", "https://api.deepseek.com")
        self.model = config.get("视觉模型", "deepseek-vl2")

        self._client = None
        if self.api_key:
            self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)

    def describe_image(self, image, prompt: str = "请描述这张图片里有什么") -> str:
        """描述图像内容"""
        if not self._client:
            return "视觉模块未配置"

        import numpy as np
        from PIL import Image

        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        buf = BytesIO()
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(buf, format="JPEG", quality=60)
        b64 = base64.b64encode(buf.getvalue()).decode()

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                        {"type": "text", "text": prompt}
                    ]
                }],
                max_tokens=512
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[VLM] 视觉分析失败: {e}")
            return ""

    def detect_change(self, current_image, previous_image, threshold: float = 0.1) -> bool:
        """检测画面是否有显著变化"""
        import numpy as np
        if current_image is None or previous_image is None:
            return True

        from PIL import Image
        if isinstance(current_image, Image.Image):
            current_image = np.array(current_image.resize((128, 72)))
        if isinstance(previous_image, Image.Image):
            previous_image = np.array(previous_image.resize((128, 72)))

        diff = np.mean(np.abs(current_image.astype(float) - previous_image.astype(float)))
        return diff > threshold * 255
