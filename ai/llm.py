"""
LLM 对话引擎 - 对接 DeepSeek 等大语言模型
支持 OpenAI 兼容 API
"""

import json
from openai import OpenAI


class LLMEngine:
    """大语言模型对话引擎"""

    def __init__(self, config: dict):
        self.config = config
        self.api_key = config.get("API密钥", "")
        self.api_base = config.get("API地址", "https://api.deepseek.com")
        self.model = config.get("模型名称", "deepseek-v4-flash")
        self.temperature = config.get("温度", 0.8)
        self.max_tokens = config.get("最大Token数", 2048)

        self.character_name = ""
        self.character_personality = ""

        self._client = None
        self._init_client()

    def _init_client(self):
        """初始化 OpenAI 客户端"""
        if self.api_key:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
        else:
            print("[LLM] 警告: API密钥未设置，请配置 config.json")

    def set_character(self, name: str, personality: str):
        """设置角色信息"""
        self.character_name = name
        self.character_personality = personality

    def _build_system_prompt(self, has_image: bool = False) -> str:
        """构建系统提示词"""
        prompt = f"你是{self.character_name}，一个桌面AI伙伴。"
        if self.character_personality:
            prompt += f"\n性格特点：{self.character_personality}"
        prompt += (
            f"\n\n你的核心能力："
            f"\n1. 你能看到用户的屏幕画面（通过截图）"
            f"\n2. 你能听到用户说话"
            f"\n3. 你以3D角色形象出现在桌面上"
            f"\n\n回复要求："
            f"\n- 像朋友一样自然交谈，简短有力"
            f"\n- 根据看到的画面内容给出具体反应"
            f"\n- 使用口语化表达"
            f"\n- 回复控制在100字以内"
        )
        return prompt

    def chat(self, user_input: str, history: list = None, image_context: any = None) -> str:
        """对话接口"""
        if not self._client:
            return "我还没连上大脑呢，请先配置API密钥！"

        messages = [{"role": "system", "content": self._build_system_prompt(has_image=image_context is not None)}]

        # 添加上文记忆
        if history:
            for h in history[-10:]:
                messages.append({"role": "user", "content": h.get("user", "")})
                messages.append({"role": "assistant", "content": h.get("assistant", "")})

        # 当前输入（含图片）
        user_content = []
        if image_context is not None:
            # 将截图转为 base64 发送
            import base64
            from io import BytesIO
            from PIL import Image
            if isinstance(image_context, Image.Image):
                buf = BytesIO()
                image_context.save(buf, format="JPEG", quality=70)
                b64 = base64.b64encode(buf.getvalue()).decode()
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                })
        user_content.append({"type": "text", "text": user_input})
        messages.append({"role": "user", "content": user_content})

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM] API调用失败: {e}")
            return "唔，我刚才走神了，你再说一遍？"

    def update_config(self, config: dict):
        """更新配置"""
        self.config.update(config)
        self._init_client()
