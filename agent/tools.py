"""
智能体工具模块
提供联网搜索、天气查询、翻译等扩展功能
"""

import json
import urllib.request
import urllib.parse


class AgentTools:
    """智能体工具集"""

    def __init__(self):
        self.tools = {
            "联网搜索": self.web_search,
            "系统状态": self.system_status,
            "告诉我时间": self.get_time,
        }

    def get_tool_list(self) -> dict:
        """获取可用工具列表"""
        return {name: func.__doc__ for name, func in self.tools.items()}

    def web_search(self, query: str) -> str:
        """联网搜索（使用 DuckDuckGo）"""
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json"
            req = urllib.request.Request(url, headers={"User-Agent": "DesktopCompanion/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                results = data.get("RelatedTopics", [])
                if results:
                    return results[0].get("Text", "没有找到结果")
                return "没有找到相关结果"
        except Exception as e:
            return f"搜索失败: {e}"

    def system_status(self) -> str:
        """查看系统状态（CPU/内存使用）"""
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        return f"CPU使用率: {cpu}%, 内存使用: {mem.percent}%"

    def get_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%Y年%m月%d日 %H:%M")

    def execute(self, tool_name: str, params: dict = None) -> str:
        """执行工具"""
        func = self.tools.get(tool_name)
        if not func:
            return f"未知工具: {tool_name}"
        if params:
            return func(**params)
        return func()
