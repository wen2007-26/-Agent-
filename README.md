# ⚖️ AI 智能消费维权助手 (AI Consumer Rights Assistant)

这是一个基于 **LangChain**、**RAG (检索增强生成)** 和 **Qwen 大模型** 构建的智能消费维权 Agent。旨在帮助消费者解决网购中遇到的假货、食品过期、质量问题等纠纷，提供法律咨询、赔偿计算、证据核对及投诉文书自动生成的一站式服务。

## ✨ 核心功能
- 🧠 **ReAct 智能体**：具备自主思考与工具调用能力，能根据用户问题自动规划解决路径。
- 📚 **RAG 法律知识库**：内置《消费者权益保护法》《食品安全法》等法律法规及真实维权案例，回答有法可依。
- 💰 **精准赔偿计算**：内置“退一赔三”、“退一赔十”等法定赔偿算法，一键算出应得赔偿。
- 📝 **多平台文书生成**：自动生成符合淘宝、抖音、京东等平台要求的官方投诉信/申诉书。
- 📸 **多模态图片分析**：支持上传聊天截图、快递面单、订单截图，调用 Qwen-VL-Max 自动提取关键信息并辅助维权。
- 📋 **动态证据核对**：根据维权场景，动态生成证据清单并提示缺失项，提高维权成功率。

## 🛠️ 技术栈
- **大模型**：阿里云通义千问 (Qwen-Max, Qwen-VL-Max)
- **框架**：LangChain, Streamlit
- **向量数据库**：ChromaDB
- **文本处理**：RecursiveCharacterTextSplitter, DashScope Embeddings

## 📂 项目结构
```text
├── app.py                      # Streamlit 前端交互界面
├── config.toml                 # Streamlit 主题与配置
├── agent/                      # Agent 核心逻辑
│   ├── react_agent.py          # ReAct 智能体构建
│   └── tools/                  # 工具链 (赔偿计算、文书生成等)
├── RAG/                        # 检索增强生成模块
│   ├── rag_service.py          # RAG 链式调用
│   └── vector_store.py         # Chroma 向量库操作
├── data/                       # 法律条文与案例知识库 (txt)
├── prompts/                    # 系统提示词与 RAG 提示词
├── config/                     # yaml 配置文件
└── requirements.txt            # 依赖项
