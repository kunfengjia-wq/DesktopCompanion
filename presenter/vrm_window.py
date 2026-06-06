"""
VRM 3D 角色悬浮窗 - PyQt6 透明窗口
显示 3D 角色，支持表情、口型同步、动画
"""

import sys
import os
import json
from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QScreen
from PyQt6.QtWebEngineWidgets import QWebEngineView


class VRMBridge(QObject):
    """Python 与 JavaScript 通信桥梁"""
    speak_signal = pyqtSignal(str, str, str)  # text, expression, emotion
    idle_signal = pyqtSignal(str)  # animation name
    config_signal = pyqtSignal(str)  # JSON config

    def __init__(self):
        super().__init__()

    def on_ready(self):
        print("[VRM] 3D 渲染引擎就绪")

    def on_click(self):
        print("[VRM] 角色被点击了")


class VRMWindow(QMainWindow):
    """VRM 3D 角色悬浮窗"""

    def __init__(self, config: dict, character_name: str = "助手", character_personality: str = ""):
        super().__init__()

        self.config = config
        self.character_name = character_name
        self.character_personality = character_personality
        self.window_width = config.get("窗口宽度", 400)
        self.window_height = config.get("窗口高度", 600)
        self.transparent = config.get("透明模式", True)
        self.always_on_top = config.get("始终置顶", True)

        self.bridge = VRMBridge()
        self.bridge.speak_signal.connect(self._on_speak_command)

        self._init_ui()
        self._page_loaded = False

        self._load_vrm_view()

        # 闲置动画定时器（页面加载完才启动）
        self._idle_timer = QTimer()
        self._idle_timer.timeout.connect(self._trigger_idle_animation)

    def _init_ui(self):
        """初始化窗口 UI"""
        self.setWindowTitle(f"{self.character_name} - 桌面伴侣")

        # 透明窗口设置
        if self.transparent:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setStyleSheet("background: transparent;")

        # 去掉边框
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint if self.always_on_top else Qt.WindowType.FramelessWindowHint
        )

        # 设置窗口大小
        self.resize(self.window_width, self.window_height)

        # 移动到屏幕右下角
        self._move_to_corner()

    def _move_to_corner(self):
        """移动到屏幕右下角"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.window_width - 20
        y = screen.height() - self.window_height - 60
        self.move(x, y)

    def _load_vrm_model(self):
        """加载 VRM 模型"""
        # 查找模型文件
        model_path = Path(self.config.get("模型文件", "presenter/webview/models/default.vrm"))

        if not model_path.exists():
            # 先用默认模型
            print(f"[VRM] 未找到模型文件: {model_path}")

    def showEvent(self, event):
        super().showEvent(event)
        # 窗口显示后加载 VRM
        self._load_vrm_model()

    def _load_vrm_view(self):
        """加载 VRM 3D 渲染页面"""
        self.web_view = QWebEngineView(self)
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # WebView 填满窗口
        self.web_view.setGeometry(0, 0, self.window_width, self.window_height)

        # 设置页面透明
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)

        # 加载 HTML
        html_path = Path(__file__).parent / "webview" / "index.html"
        url = QUrl.fromLocalFile(str(html_path.absolute()))
        self.web_view.load(url)

        # 等页面加载完成后再调用 JS
        self.web_view.loadFinished.connect(self._on_page_loaded)

    def speak(self, text: str):
        """角色说话"""
        # 生成表情和情绪
        emotion = self._detect_emotion(text)
        expression = "happy" if emotion == "开心" else "neutral"

        # 通知 JS 层说话
        js_code = f'vrmController.speak(`{self._escape_js(text)}`, "{expression}")'
        self._safe_js(js_code)

        print(f"[{self.character_name}] {text}")

    def show_thinking(self):
        """显示思考中"""
        self._safe_js('vrmController.showThinking()')

    def hide_thinking(self):
        """隐藏思考中"""
        self._safe_js('vrmController.hideThinking()')

    def set_expression(self, expression: str):
        """设置角色表情"""
        self._safe_js(f'vrmController.setExpression("{expression}")')

    def _on_page_loaded(self, ok: bool):
        """页面加载完成回调"""
        if ok:
            self._page_loaded = True
            print("[VRM] 页面加载完成")
            # 延迟一会儿等 Three.js 初始化完成
            QTimer.singleShot(1000, self._start_vrm_after_load)
        else:
            print("[VRM] 页面加载失败")

    def _start_vrm_after_load(self):
        """页面加载完成后启动 VRM 功能"""
        # 标记角色就绪
        js_code = """
        if (typeof vrmController !== 'undefined' && vrmController) {
            document.getElementById('loading').style.display = 'none';
            console.log('[VRM] 控制器已就绪');
            true;
        } else {
            // 还没加载完，等会再试
            console.log('[VRM] 等待控制器初始化...');
            false;
        }
        """
        self.web_view.page().runJavaScript(js_code, self._on_vrm_ready)

    def _on_vrm_ready(self, result):
        """VRM 控制器就绪回调"""
        if result:
            print("[VRM] 3D 角色就绪")
            self._idle_timer.start(8000)
        else:
            # 1秒后重试
            QTimer.singleShot(2000, self._start_vrm_after_load)

    def _trigger_idle_animation(self):
        """触发闲置动画"""
        if not self._page_loaded or not self._on_page_loaded:
            return
        import random
        actions = ["blink", "look_around", "stretch", "tilt"]
        action = random.choice(actions)
        self._safe_js(f'vrmController.playIdle("{action}")')

    def _safe_js(self, code: str):
        """安全执行 JS（页面未加载时不执行）"""
        if self._page_loaded:
            self.web_view.page().runJavaScript(code)

    def _detect_emotion(self, text: str) -> str:
        """简单情绪检测"""
        happy_words = ["哈哈", "开心", "棒", "好", "厉害", "嘿嘿", "wow", "赞", "喜欢"]
        sad_words = ["难过", "哭", "伤心", "累", "烦", "哎", "叹气"]
        surprise_words = ["哇", "真的", "天哪", "惊讶", "居然", "竟然"]

        for w in surprise_words:
            if w in text:
                return "惊讶"
        for w in happy_words:
            if w in text:
                return "开心"
        for w in sad_words:
            if w in text:
                return "难过"
        return "中性"

    def _on_speak_command(self, text: str, expression: str, emotion: str):
        """收到JS发送的说话完成事件"""
        pass

    def _escape_js(self, text: str) -> str:
        """转义 JavaScript 字符串"""
        return text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$").replace("\n", "\\n")

    def closeEvent(self, event):
        """关闭事件"""
        self._idle_timer.stop()
        super().closeEvent(event)
