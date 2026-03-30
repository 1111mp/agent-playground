# Agent Playground

一个从 0 到 1 实现的 **LLM CLI Agent 最小框架**。  
支持 DeepSeek、Streaming、Tool Calling、多轮推理（ReAct Loop）。

当前版本已经可以完成：

> 用户提问 → 模型调用本地工具 → 自动继续推理 → 返回最终答案
>
> 例如：明天纽约天气怎么样？
>
> → 自动调用天气工具 → 返回结果 → 模型总结回答

---

## 🚀 快速开始

### 1️⃣ 安装 uv（如果没有）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

验证：

```bash
uv --version
```

### 2️⃣ 创建虚拟环境并安装依赖

```bash
uv sync
```

### 3️⃣ 配置环境变量

```bash
cp .env.example .env
```

### 4️⃣ 运行项目

```bash
uv run python main.py
```

看到：

```bash
🤖 DeepSeek Chat 已启动 (输入 exit 退出)
```

现在可以开始聊天：

```bash
👤 You: 明天纽约天气怎么样
```

Agent 会自动：

1. 调用天气工具
2. 获取结果
3. 继续推理
4. 输出最终回答

---

## 🧠 Agent 工作流程

```text
User Input
   ↓
LLM 推理
   ↓
需要工具？
 ├─ 否 → 直接回答
 └─ 是 → 调用 Tool
          ↓
     Tool 返回结果
          ↓
     LLM 继续推理
          ↓
     最终回答
```

这是一个完整的 ReAct Agent Loop。

---

## 🏗️ 设计目标

这个项目不是一个完整框架，而是：

> 一个 最小但完整 的 Agent 实现示例

目标是帮助理解：

- streaming 如何工作
- tool call 如何拼接
- Agent loop 如何实现
- LLM 如何与工具协作

适合作为：

- Agent 学习项目
- 二次开发模板
- 实验 playground

## 📄 License

MIT
