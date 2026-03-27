# AI Bot 嵌入式助手引擎 — 架构设计方案

> 不是独立聊天工具，而是嵌入到业务系统里的智能伴侣。
> 它知道你在看什么、知道系统发生了什么、会主动说话。

---

## 一、产品定位

**嵌入式 AI 助手引擎（Embedded AI Assistant Engine）**

传统 AI 聊天机器人：用户问 → AI 答，被动的。

我们的机器人：
- 用户登录 → "欢迎回来，今天有 3 个产品到期需要关注"
- 用户点击财务模块 → "这是财务概览，上周资金消耗较快，建议关注"
- 数据异常 → 机器人主动弹出 "检测到异常，今日到期产品比平时多 200%"
- 用户随时可以对它说话/打字问问题
- 可以选择它多话还是安静

---

## 二、三种交互模式

| 模式 | 名称 | 行为 | 适用场景 |
|------|------|------|---------|
| **A** | 伴侣模式 | 高频输出：页面切换介绍、数据变化提醒、主动建议、闲聊 | 新用户、需要引导 |
| **B** | 助手模式 | 中等频率：只在异常和关键操作时提醒，用户问才答 | 日常使用 |
| **C** | 安静模式 | 低频率：只在严重异常时提醒，最小化到角落 | 资深用户、不想被打扰 |

用户可以随时切换模式。模式配置存在用户偏好中。

---

## 三、系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端（React）                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   业务页面                              │   │
│  │  Dashboard | 知识库 | 数据看板 | 设置 ...               │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │ 页面事件                            │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              AI Bot 前端引擎                            │   │
│  │                                                        │   │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────────┐  │   │
│  │  │ Bot Avatar │ │ Chat Panel │ │ Voice Engine     │  │   │
│  │  │ 形象+动画  │ │ 对话面板   │ │ 语音输入/输出    │  │   │
│  │  │ 可拖拽移动 │ │ 消息流     │ │ Web Speech API  │  │   │
│  │  └────────────┘ └────────────┘ └──────────────────┘  │   │
│  │                                                        │   │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────────┐  │   │
│  │  │ Scene      │ │ Mode       │ │ Event            │  │   │
│  │  │ Detector   │ │ Controller │ │ Listener         │  │   │
│  │  │ 场景感知   │ │ A/B/C模式  │ │ 页面事件监听     │  │   │
│  │  └────────────┘ └────────────┘ └──────────────────┘  │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │ WebSocket（双向实时）
┌─────────────────────────▼───────────────────────────────────┐
│                    后端 Bot 引擎                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              WebSocket Manager                        │   │
│  │  管理所有客户端连接，双向消息推送                       │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────┐ ┌─────────▼──────────┐ ┌──────────────────┐  │
│  │ Scene    │ │ Bot Brain          │ │ Alert            │  │
│  │ Handler  │ │ (LangGraph)        │ │ Service          │  │
│  │          │ │                    │ │                  │  │
│  │ 场景配置 │ │ 意图识别           │ │ 定时检查数据     │  │
│  │ 页面→话术│ │ RAG检索            │ │ 异常检测         │  │
│  │ 事件→响应│ │ AI分析             │ │ 到期预警         │  │
│  │          │ │ 图表生成           │ │ 阈值触发         │  │
│  └──────────┘ └────────────────────┘ └──────────────────┘  │
│                         │                                    │
│  ┌──────────┐ ┌─────────▼──────────┐ ┌──────────────────┐  │
│  │ Bot      │ │ LiteLLM            │ │ TTS / STT        │  │
│  │ Persona  │ │ (模型自由切换)      │ │ 语音服务         │  │
│  │          │ │                    │ │                  │  │
│  │ 人设配置 │ │ Claude/GPT/        │ │ Web Speech API   │  │
│  │ 语气风格 │ │ DeepSeek/Ollama    │ │ 或云端TTS API    │  │
│  │ 称呼用户 │ │                    │ │                  │  │
│  └──────────┘ └────────────────────┘ └──────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Mode Controller                          │   │
│  │                                                       │   │
│  │  A模式（伴侣）: 所有事件都触发 → 高频输出              │   │
│  │  B模式（助手）: 异常+关键操作 → 中频输出               │   │
│  │  C模式（安静）: 严重异常 → 低频输出                    │   │
│  │                                                       │   │
│  │  过滤逻辑：                                            │   │
│  │  event.priority >= mode.threshold → 推送给前端         │   │
│  │  event.priority <  mode.threshold → 静默记录           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、核心模块设计

### 4.1 场景感知（Scene Handler）

前端触发事件 → 后端返回对应的机器人话术

```python
# 场景配置（可通过 JSON/数据库配置，不硬编码）
SCENE_CONFIG = {
    "login": {
        "priority": "high",
        "template": "欢迎回来，{username}！{summary}",
        "action": "fetch_daily_summary",  # 调用哪个数据接口
    },
    "page:dashboard": {
        "priority": "medium",
        "template": "这是系统总览。{highlight}",
        "action": "fetch_system_overview",
    },
    "page:finance": {
        "priority": "medium",
        "template": "财务概览：{finance_brief}",
        "action": "fetch_finance_summary",
    },
    "page:knowledge_base": {
        "priority": "low",
        "template": "这里是知识库，你可以上传文档让我学习。",
        "action": None,
    },
    "data:anomaly": {
        "priority": "critical",
        "template": "⚠️ 检测到异常：{anomaly_detail}",
        "action": "fetch_anomaly_detail",
    },
    "data:expiry_warning": {
        "priority": "high",
        "template": "📌 提醒：{expiry_count} 个产品即将到期",
        "action": "fetch_expiring_products",
    },
}
```

**前端触发方式：**
```javascript
// 用户切换页面时
botSocket.send({ type: "scene", scene: "page:dashboard" });

// 用户登录时
botSocket.send({ type: "scene", scene: "login", data: { username: "Alice" } });
```

---

### 4.2 主动提醒（Alert Service）

后台定时任务检查数据，异常时通过 WebSocket 主动推送：

```python
class AlertService:
    """定时检查数据，触发机器人主动提醒"""

    # 检查频率
    CHECK_INTERVALS = {
        "expiry_check": 300,      # 每5分钟检查到期产品
        "anomaly_check": 60,      # 每1分钟检查数据异常
        "daily_summary": 86400,   # 每天一次日报
    }

    async def check_expiry(self):
        """检查即将到期的产品"""
        products = await data_service.get_expiring_products("today")
        if products["total"] > 0:
            return {
                "type": "alert",
                "priority": "high",
                "scene": "data:expiry_warning",
                "data": {"expiry_count": products["total"]},
            }
        return None

    async def check_anomaly(self):
        """检查数据异常（同比环比偏差大）"""
        stats = await data_service.get_system_overview()
        # 例：今日新增用户比昨天多 200%
        if stats.get("growth_rate", 0) > 100:
            return {
                "type": "alert",
                "priority": "critical",
                "scene": "data:anomaly",
                "data": {"anomaly_detail": f"新增用户激增 {stats['growth_rate']}%"},
            }
        return None
```

---

### 4.3 交互模式控制（Mode Controller）

```python
class ModeController:
    """根据用户选择的模式过滤消息"""

    THRESHOLDS = {
        "A": 0,          # 伴侣模式：所有消息都推送
        "B": 2,          # 助手模式：medium 及以上
        "C": 4,          # 安静模式：只推送 critical
    }

    PRIORITY_LEVELS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    def should_push(self, mode: str, event_priority: str) -> bool:
        threshold = self.THRESHOLDS.get(mode, 2)
        level = self.PRIORITY_LEVELS.get(event_priority, 0)
        return level >= threshold

    def get_behavior(self, mode: str) -> dict:
        behaviors = {
            "A": {
                "auto_introduce_pages": True,      # 自动介绍页面
                "greet_on_login": True,             # 登录欢迎
                "idle_chat": True,                  # 空闲时主动聊天
                "alert_all": True,                  # 所有提醒
                "animation": "active",              # 活跃动画
            },
            "B": {
                "auto_introduce_pages": False,
                "greet_on_login": True,
                "idle_chat": False,
                "alert_all": False,                 # 只推重要提醒
                "animation": "normal",
            },
            "C": {
                "auto_introduce_pages": False,
                "greet_on_login": False,
                "idle_chat": False,
                "alert_all": False,                 # 只推紧急提醒
                "animation": "minimal",             # 最小化动画
            },
        }
        return behaviors.get(mode, behaviors["B"])
```

---

### 4.4 机器人人设（Bot Persona）

```python
# 可配置的人设（.env 或管理后台配置）
BOT_PERSONAS = {
    "default": {
        "name": "Nexus",
        "personality": "专业、简洁、友好",
        "system_prompt": """你是 Nexus，企业 AI 助手。
风格：专业但不冷漠，简洁不啰嗦。
规则：
1. 回答基于真实数据，不编造
2. 数据不足时明确说明
3. 用户称呼用"你"不用"您"
4. 重要数据用加粗标注
5. 适当使用 emoji 但不过多""",
        "greeting": "你好！我是 Nexus，有什么需要帮忙的？",
        "avatar": "nexus",  # 对应前端头像/模型
    },
    "casual": {
        "name": "小助",
        "personality": "活泼、幽默、话多",
        "system_prompt": "你是小助，一个活泼的 AI 助手...",
        "greeting": "嗨！我是小助~ 今天想聊点什么？",
        "avatar": "casual",
    },
}
```

---

### 4.5 语音对话（Voice Engine）

```
用户说话 → 浏览器 Web Speech API（STT）→ 文字
    → 发送到后端 → LangGraph 处理 → 返回文字
    → 前端 Web Speech API（TTS）→ 语音输出

或者：
用户说话 → 浏览器录音 → 发送音频到后端
    → 后端调 Whisper API（STT）→ 文字
    → LangGraph 处理 → 返回文字
    → 后端调 TTS API → 返回音频 → 前端播放
```

**两种方案：**

| 方案 | STT | TTS | 费用 | 质量 |
|------|-----|-----|------|------|
| 浏览器原生 | Web Speech API | SpeechSynthesis | 免费 | 一般 |
| 云端 API | Whisper / DeepSeek | OpenAI TTS / Edge TTS | 收费/免费 | 高 |

建议默认用浏览器原生（免费），可选配置云端 API（质量高）。

---

### 4.6 WebSocket 双向通信

```python
# 后端 WebSocket 管理器
class BotWebSocketManager:
    """管理所有客户端连接"""

    def __init__(self):
        self.connections: dict[str, WebSocket] = {}  # user_id → ws

    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.connections[user_id] = ws

    async def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)

    async def push_to_user(self, user_id: str, message: dict):
        """推送消息给指定用户"""
        ws = self.connections.get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        """广播给所有在线用户"""
        for ws in self.connections.values():
            await ws.send_json(message)
```

**消息协议：**

```json
// 前端 → 后端
{"type": "scene", "scene": "page:dashboard"}
{"type": "chat", "message": "资金还能撑多久"}
{"type": "voice", "audio": "base64..."}
{"type": "mode_change", "mode": "A"}

// 后端 → 前端
{"type": "bot_message", "content": "欢迎回来！今天有3个产品到期", "priority": "high"}
{"type": "bot_message", "content": "...", "chart": {...}, "sources": [...]}
{"type": "bot_action", "action": "move_to", "position": {"x": 100, "y": 200}}
{"type": "bot_action", "action": "animate", "animation": "wave"}
{"type": "bot_action", "action": "minimize"}
{"type": "mode_config", "behavior": {...}}
```

---

### 4.7 外部接入（Embed SDK）

让其他系统也能嵌入这个机器人：

```html
<!-- 外部系统只需加这两行 -->
<script src="https://your-domain.com/bot-sdk.js"></script>
<script>
    AiBot.init({
        server: "wss://your-domain.com/ws/bot",
        token: "user-jwt-token",
        mode: "B",
        position: "bottom-right",
        persona: "default",
    });
</script>
```

---

## 五、API 设计

### WebSocket

| 端点 | 说明 |
|------|------|
| `WS /ws/bot` | 机器人双向通信（场景/对话/语音/提醒） |

### REST API

| 端点 | 方法 | 说明 |
|------|------|------|
| `GET /api/v1/bot/config` | GET | 获取机器人配置（人设/模式） |
| `PUT /api/v1/bot/mode` | PUT | 切换模式（A/B/C） |
| `PUT /api/v1/bot/persona` | PUT | 切换人设 |
| `GET /api/v1/bot/history` | GET | 机器人消息历史 |
| `POST /api/v1/bot/scene` | POST | 手动触发场景（调试用） |
| `GET /api/v1/bot/alerts` | GET | 查看待推送的提醒 |

---

## 六、数据库新增表

```sql
-- 机器人消息记录
bot_messages (
    id, user_id, direction,  -- "bot_to_user" / "user_to_bot"
    type,                     -- "scene" / "chat" / "alert" / "voice"
    content, scene, priority,
    mode_at_time,             -- 推送时用户的模式
    created_at
)

-- 用户偏好
user_bot_preferences (
    id, user_id,
    mode,                     -- "A" / "B" / "C"
    persona,                  -- "default" / "casual"
    voice_enabled,            -- true/false
    tts_provider,             -- "browser" / "openai" / "edge"
    position_x, position_y,   -- 机器人位置记忆
    minimized,                -- 是否最小化
    updated_at
)

-- 场景配置（管理后台可编辑）
bot_scenes (
    id, scene_key,            -- "login" / "page:dashboard" / "data:anomaly"
    priority,                 -- "low" / "medium" / "high" / "critical"
    template,                 -- "欢迎回来，{username}！"
    action,                   -- "fetch_daily_summary"
    is_active,
    updated_at
)
```

---

## 七、后端新增文件

```
backend/app/
├── api/v1/
│   ├── bot.py                 # 机器人 REST API
│   └── ws.py                  # WebSocket 端点
├── services/
│   ├── bot_brain.py           # 机器人大脑（整合 LangGraph）
│   ├── bot_persona.py         # 人设管理
│   ├── alert_service.py       # 主动提醒（定时检查）
│   ├── scene_handler.py       # 场景感知处理
│   ├── mode_controller.py     # A/B/C 模式控制
│   ├── voice_service.py       # 语音 STT/TTS
│   └── ws_manager.py          # WebSocket 连接管理
├── models/
│   ├── bot_message.py         # 消息记录
│   ├── bot_preference.py      # 用户偏好
│   └── bot_scene.py           # 场景配置
└── schemas/
    └── bot.py                 # Bot 相关 Pydantic
```

---

## 八、前端需要的组件（给 Stitch / 自己做）

```
frontend/src/
├── components/bot/
│   ├── BotAvatar.tsx          # 机器人形象（Three.js 或 CSS 动画）
│   ├── BotChatPanel.tsx       # 聊天面板（消息流 + 输入框）
│   ├── BotVoiceButton.tsx     # 语音按钮（按住说话）
│   ├── BotModeSelector.tsx    # 模式切换（A/B/C）
│   ├── BotAlertBubble.tsx     # 提醒气泡（弹出动画）
│   └── BotContainer.tsx       # 总容器（可拖拽 + 最小化）
├── hooks/
│   ├── useBotWebSocket.ts     # WebSocket 连接管理
│   ├── useBotScene.ts         # 场景事件触发
│   └── useBotVoice.ts         # 语音输入/输出
└── store/
    └── botStore.ts            # 机器人状态（Zustand）
```

---

## 九、开发顺序

### Phase A：WebSocket + 场景感知（核心）
1. WebSocket 管理器（ws_manager.py）
2. 场景处理器（scene_handler.py）
3. 模式控制器（mode_controller.py）
4. Bot REST API（bot.py）
5. 登录欢迎 + 页面介绍

### Phase B：主动提醒
6. 定时检查服务（alert_service.py）
7. 到期预警 + 异常检测
8. WebSocket 推送提醒

### Phase C：人设 + 对话增强
9. 人设配置（bot_persona.py）
10. 整合 LangGraph 做对话（bot_brain.py）
11. 消息记录 + 历史

### Phase D：语音
12. 浏览器 Web Speech API（STT + TTS）
13. 可选：云端 Whisper + OpenAI TTS

### Phase E：外部接入
14. Embed SDK（bot-sdk.js）
15. iframe / Web Component 嵌入方案

---

## 十、.env 新增配置

```env
# Bot Configuration
BOT_PERSONA=default                    # default / casual / custom
BOT_DEFAULT_MODE=B                     # A(伴侣) / B(助手) / C(安静)

# Alert Check Intervals (seconds)
ALERT_EXPIRY_INTERVAL=300              # 到期检查频率
ALERT_ANOMALY_INTERVAL=60             # 异常检查频率

# Voice (optional)
VOICE_ENABLED=false
TTS_PROVIDER=browser                   # browser / openai / edge
STT_PROVIDER=browser                   # browser / whisper
OPENAI_TTS_VOICE=alloy                # alloy / echo / fable / onyx / nova / shimmer
```

---

*确认后按 Phase A 开始开发。*
