# 🚀 桌面伴侣 - 启动指南

## 一分钟启动

```bash
cd C:\Users\A\DesktopCompanion
pip install -r requirements.txt
python main.py
```

## 启动后

| 操作 | 说明 |
|------|------|
| 🎤 说话 | 对着麦克风说话，角色会回应你 |
| ⌨️ 打字 | 在终端窗口输入文字按回车 |
| 👋 /quit | 输入 `/quit` 退出 |
| 🖥️ 最小化 | 关闭窗口会缩到系统托盘 |

## 配置

编辑 `config.json`：
- `角色设定.名称` → 改角色名字
- `角色设定.性格` → 改性格描述
- `VRM模型.模型文件` → 换模型路径

## 已安装的 VRM 模型

`presenter/webview/models/` 目录下有：
- **default.vrm** (Rose) ← 当前使用的
- Rabbit.vrm, Erika.vrm, Snowy.vrm, Olivia.vrm, Teddy.vrm

想换模型 → 复制替换 `default.vrm` 或改 `config.json`

## 常见问题

**Q: 语音识别没反应？**
A: 确保麦克风已连接，或者在终端打字也一样

**Q: DeepSeek API 报错？**
A: 检查 `config.json` 里的 API密钥 是否正确

**Q: 窗口一片空白？**
A: 模型加载需要网络（从 CDN 加载 Three.js），等等就好

---

✅ 所有模块已通过测试 | 📂 GitHub: kunfengjia-wq/DesktopCompanion
