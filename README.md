# ⚖️ 网上消费维权 AI 智能助手

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-v0.1-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B)
![Qwen](https://img.shields.io/badge/LLM-Qwen--Max-blueviolet)

这是一个基于 **LangChain**、**RAG (检索增强生成)** 与 **多模态大模型 (Qwen-VL)** 构建的智能消费维权 Agent。旨在帮助消费者解决网购中遇到的假货、食品过期、质量问题等纠纷，提供法律咨询、赔偿计算、证据核对及投诉文书自动生成的一站式服务。

## ✨ 核心功能

- 🧠 **ReAct 智能体**：具备自主思考与工具调用（Function Calling）能力，能根据用户问题自动规划解决路径。
- 📚 **RAG 法律知识库**：内置《消费者权益保护法》《食品安全法》等法律法规及真实维权案例，回答有法可依，杜绝模型幻觉。
- 💰 **精准赔偿计算**：内置“退一赔三”、“退一赔十”等法定赔偿算法，一键算出应得赔偿。
- 📝 **多平台文书生成**：自动检索平台政策，生成符合淘宝、抖音、京东等平台要求的官方投诉信/申诉书。
- 📸 **多模态图片分析**：支持上传聊天截图、快递面单、订单截图，调用 Qwen-VL-Max 自动提取关键信息并辅助维权。
- 📋 **动态证据核对**：根据当前对话场景自动识别维权类型（假货/食品/质量等），动态生成证据清单并提示缺失项。

## 🛠️ 技术栈

- **大模型**：阿里云通义千问 (`qwen-max`, `qwen-vl-max`)
- **开发框架**：LangChain (Agent, RAG, Tools, Middleware), Streamlit
- **向量数据库**：ChromaDB
- **文档处理**：RecursiveCharacterTextSplitter, DashScope Embeddings
- **配置管理**：YAML, Toml

## 📂 项目结构

```text
├── app.py                      # Streamlit 前端交互界面入口
├── config.toml                 # Streamlit 主题与页面配置
├── agent/                      # Agent 核心逻辑
│   ├── react_agent.py          # ReAct 智能体构建与流式输出处理
│   └── tools/                  # 工具链封装
│       ├── agent_tools.py      # 赔偿计算、法条检索等基础工具
│       ├── complaint_tool.py   # 平台投诉信生成工具
│       └── complaint_form12315.py # 12315 表单生成工具
├── RAG/                        # 检索增强生成模块
│   ├── rag_service.py          # RAG 链式调用封装
│   └── vector_store.py         # Chroma 向量库构建与操作
├── data/                       # 法律条文与案例知识库 (txt)
├── prompts/                    # 系统提示词 (System Prompts)
├── config/                     # yaml 配置文件
└── requirements.txt            # 依赖项清单
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/summer_wind/-Agent-.git
cd -Agent-
```

### 2. 安装依赖
推荐使用虚拟环境运行：
```bash
python -m venv venv
source venv/bin/activate  # Windows 系统使用: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量
在项目根目录新建一个 `.env` 文件，填入你的阿里云百炼 API Key：
```env
DASHSCOPE_API_KEY=sk-你的真实阿里云API密钥
```

### 4. 构建本地知识库
首次运行前，需要将 `data/` 目录下的法律法规 txt 文件切分并向量化存入 Chroma：
```bash
python RAG/vector_store.py
```
*(注：如果你修改了 `data/` 下的文件，再次运行此脚本，系统会根据 MD5 自动去重并更新知识库)*

### 5. 启动应用
```bash
streamlit run app.py
```
启动后，浏览器会自动打开交互页面。

## 💡 使用示例

你可以尝试在聊天框中输入以下问题，体验 Agent 的思考与工具调用过程：

- **法律检索**：“我在淘宝买了个手机，用了3天发现屏幕有坏点，商家说是我自己弄坏的不给退，消费者权益保护法怎么规定的？”
- **赔偿计算**：“300块钱的假货能赔多少？”
- **文书生成**：“帮我在抖音平台写一份投诉信，我买了件羽绒服，到货发现是假货，订单号是DD123456789，商家叫『潮流男装店』，我的诉求是退一赔三。”
- **图文混合**：在左侧边栏上传一张与商家的“聊天截图”，并输入：“客服不给我退款，我该怎么做？”

## ⚠️ 免责声明

本项目仅供学习与技术交流使用。生成的投诉文书、赔偿金额与法律建议仅供参考，不构成正式的法律意见。实际维权请结合具体情况或咨询专业律师。

## 🤝 贡献与反馈

欢迎提交 Issue 或 Pull Request。如果这个项目对你有帮助，欢迎点个 Star ⭐ 支持一下！
