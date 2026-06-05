"""
对话记忆管理 - 让角色记住你们的对话
"""

import json
from pathlib import Path
from datetime import datetime


class MemoryManager:
    """对话记忆管理器"""

    def __init__(self, config: dict):
        self.config = config
        self.max_rounds = config.get("最大对话轮数", 50)
        self.save_path = Path(config.get("保存路径", "data/memory.json"))
        self._history = []

        self._ensure_dir()
        self._load()

    def _ensure_dir(self):
        """确保保存目录存在"""
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        """从文件加载记忆"""
        if self.save_path.exists():
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._history = data.get("history", [])
            except Exception:
                self._history = []

    def _save(self):
        """保存记忆到文件"""
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump({"history": self._history}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[记忆] 保存失败: {e}")

    def add(self, user_input: str, response: str):
        """添加一条对话记录"""
        self._history.append({
            "user": user_input,
            "assistant": response,
            "time": datetime.now().isoformat()
        })
        # 限制记忆轮数
        if len(self._history) > self.max_rounds:
            self._history = self._history[-self.max_rounds:]
        self._save()

    def get_history(self, last_n: int = None) -> list:
        """获取对话历史"""
        if last_n:
            return self._history[-last_n:]
        return self._history

    def get_summary(self) -> str:
        """获取对话摘要"""
        if not self._history:
            return "还没有对话记录"
        return f"共 {len(self._history)} 轮对话"

    def clear(self):
        """清空记忆"""
        self._history = []
        self._save()

    def get_recent_context(self, max_rounds: int = 5) -> str:
        """获取最近的对话上下文文本"""
        recent = self._history[-max_rounds:]
        lines = []
        for item in recent:
            lines.append(f"用户: {item['user']}")
            lines.append(f"你: {item['assistant']}")
        return "\n".join(lines)
