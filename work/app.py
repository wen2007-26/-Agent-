import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from agent.react_agent import ReactAgent

# ========== 图片分析功能 ==========
from work.vision.analyzer import image_analyzer
import base64


# ================================


def render_image_upload():
    """渲染图片上传组件"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📸 上传维权图片")
    st.sidebar.markdown("支持聊天截图、快递面单、订单截图")

    uploaded_file = st.sidebar.file_uploader(
        "选择图片",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="image_uploader"
    )

    return uploaded_file


def encode_image(uploaded_file) -> str:
    """将上传的图片转换为 base64"""
    bytes_data = uploaded_file.getvalue()
    base64_str = base64.b64encode(bytes_data).decode('utf-8')
    mime_type = uploaded_file.type
    return f"data:{mime_type};base64,{base64_str}"


def generate_12315_form_text(
        complainant_name: str,
        phone: str,
        merchant_name: str,
        order_id: str,
        product_name: str,
        amount: float,
        issue_description: str,
        demand: str = "退款+赔偿"
) -> str:
    """生成12315投诉表单文本"""
    from datetime import datetime
    now_date = datetime.now().strftime("%Y年%m月%d日")

    form = f"""
╔══════════════════════════════════════════════════════════════╗
║                    12315 投诉举报表单                         ║
╠══════════════════════════════════════════════════════════════╣
║ 【投诉人信息】                                                ║
║   姓名：{complainant_name}
║   电话：{phone}
║
║ 【被投诉方信息】                                              ║
║   商家名称：{merchant_name}
║
║ 【订单信息】                                                  ║
║   订单号：{order_id}
║   商品名称：{product_name}
║   消费金额：{amount}元
║
║ 【投诉内容】                                                  ║
║   问题描述：{issue_description}
║
║ 【投诉诉求】                                                  ║
║   {demand}
║
║ 【提交时间】                                                  ║
║   {now_date}
╚══════════════════════════════════════════════════════════════╝

【使用说明】
1. 复制以上内容
2. 访问全国12315平台官网：https://www.12315.cn/
3. 登录后选择「我要投诉」
4. 粘贴以上信息并提交
"""
    return form


def detect_complaint_type(messages):
    """
    根据最近一条用户消息判断维权类型

    Returns:
        str: "fake" (假货), "food" (食品问题), "quality" (质量问题), "general" (通用)
    """
    if not messages:
        return "general"

    # 获取最近一条用户消息
    last_user_msg = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_msg = msg["content"].lower()
            break

    # 判断类型
    if any(keyword in last_user_msg for keyword in ["假货", "假", "仿冒", "山寨", "A货"]):
        return "fake"
    elif any(keyword in last_user_msg for keyword in ["过期", "变质", "发霉", "异味", "异物", "食品"]):
        return "food"
    elif any(keyword in last_user_msg for keyword in ["质量", "坏了", "故障", "不能用", "破损"]):
        return "quality"
    else:
        return "general"


def get_evidence_items(complaint_type):
    """
    根据维权类型返回对应的证据清单
    """
    evidence_map = {
        "fake": {
            "name": "假货维权",
            "items": {
                "订单截图": "显示商品名称、价格、下单时间",
                "付款记录": "支付宝/微信支付凭证",
                "聊天记录": "与商家沟通的完整记录",
                "商品瑕疵照片": "假货细节对比图",
                "品牌鉴定证明": "品牌方出具的假货鉴定（如有）"
            }
        },
        "food": {
            "name": "食品安全维权",
            "items": {
                "订单截图": "显示商品名称、价格、下单时间",
                "付款记录": "支付宝/微信支付凭证",
                "商品照片": "食品包装整体照片",
                "生产日期/保质期照片": "清晰可见的日期信息",
                "问题部位特写": "过期/变质/异物特写",
                "购物小票": "线下购买的票据（如有）"
            }
        },
        "quality": {
            "name": "质量问题维权",
            "items": {
                "订单截图": "显示商品名称、价格、下单时间",
                "付款记录": "支付宝/微信支付凭证",
                "商品瑕疵照片": "质量问题特写",
                "快递面单": "物流信息",
                "维修记录": "维修单据（如有）"
            }
        },
        "general": {
            "name": "通用维权",
            "items": {
                "订单截图": "显示商品名称、价格、下单时间",
                "付款记录": "支付宝/微信支付凭证",
                "聊天记录": "与商家沟通的完整记录",
                "商品瑕疵照片": "商品问题照片",
                "快递面单": "物流信息"
            }
        }
    }
    return evidence_map.get(complaint_type, evidence_map["general"])


def search_similar_cases(query_text: str, top_k: int = 3) -> list:
    """
    从向量库检索相似案例

    Args:
        query_text: 用户问题描述
        top_k: 返回案例数量

    Returns:
        案例列表
    """
    if not query_text:
        return []

    try:
        from work.RAG.vector_store import VectorStoreService
        vs = VectorStoreService()
        retriever = vs.get_retriever()
        docs = retriever.invoke(query_text)

        cases = []
        for doc in docs[:top_k]:
            content = doc.page_content
            # 解析案例内容（格式：问题类型：xxx\n处理结果：xxx\n...）
            case = {}
            lines = content.strip().split('\n')
            for line in lines:
                if '：' in line:
                    key, value = line.split('：', 1)
                    case[key.strip()] = value.strip()
                elif ':' in line:
                    key, value = line.split(':', 1)
                    case[key.strip()] = value.strip()
            cases.append(case)
        return cases
    except Exception as e:
        print(f"案例检索失败: {e}")
        return []


def display_cases(cases):
    """在侧边栏显示案例"""
    if not cases:
        return

    with st.sidebar.expander("📚 相似维权案例参考", expanded=False):
        st.markdown("根据您的问题，为您找到以下相似案例：")
        st.markdown("---")
        for i, case in enumerate(cases, 1):
            st.markdown(f"**案例{i}**")
            st.markdown(f"- 问题类型：{case.get('问题类型', case.get('Problem Type', '未知'))}")
            st.markdown(f"- 处理结果：{case.get('处理结果', case.get('Result', '未知'))}")
            st.markdown(f"- 赔偿金额：{case.get('赔偿金额', case.get('Compensation', '未知'))}")
            st.markdown(f"- 关键证据：{case.get('关键证据', case.get('Key Evidence', '未知'))}")
            st.markdown("---")


def main():
    # 页面配置
    st.set_page_config(
        page_title="网上消费维权助手",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 自定义CSS样式
    st.markdown("""
        <style>
        .stExpander {
            background-color: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        .stChatMessage {
            margin-bottom: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 标题
    st.title("⚖️ 网上消费维权助手")
    st.markdown("我是您的专业维权助手，可以帮您解答消费维权问题、生成投诉信、提供法律依据等。图片上传工具在左上角。")
    st.divider()

    # ========== 图片上传组件 ==========
    uploaded_image = render_image_upload()
    # ================================

    # ========== 动态证据核对清单 ==========
    # 初始化证据清单状态
    if "evidence_checklist" not in st.session_state:
        st.session_state.evidence_checklist = {}
        st.session_state.current_evidence_type = "general"

    # 获取当前维权类型（根据对话历史自动判断）
    current_type = detect_complaint_type(st.session_state.get("messages", []))
    evidence_config = get_evidence_items(current_type)

    # 如果维权类型发生变化，重置证据清单
    if st.session_state.current_evidence_type != current_type:
        st.session_state.current_evidence_type = current_type
        st.session_state.evidence_checklist = {
            item: False for item in evidence_config["items"]
        }

    # 确保证据清单中的项与当前类型匹配
    current_items = set(evidence_config["items"].keys())
    saved_items = set(st.session_state.evidence_checklist.keys())
    if current_items != saved_items:
        new_checklist = {}
        for item in current_items:
            new_checklist[item] = st.session_state.evidence_checklist.get(item, False)
        st.session_state.evidence_checklist = new_checklist

    # 显示证据核对清单
    with st.sidebar.expander(f"📋 证据核对清单 - {evidence_config['name']}", expanded=False):
        st.markdown(f"*根据您的问题，系统自动识别为「{evidence_config['name']}」场景*")
        st.markdown("请勾选您已准备的证据：")

        for item, description in evidence_config["items"].items():
            st.session_state.evidence_checklist[item] = st.checkbox(
                f"**{item}**",
                value=st.session_state.evidence_checklist.get(item, False),
                key=f"evidence_{item}"
            )
            st.caption(f"   {description}")

        st.markdown("---")

        # 计算缺失证据
        missing = [item for item, checked in st.session_state.evidence_checklist.items() if not checked]
        checked_count = len([c for c in st.session_state.evidence_checklist.values() if c])
        total_count = len(st.session_state.evidence_checklist)

        # 显示进度条
        progress = checked_count / total_count if total_count > 0 else 0
        st.progress(progress, text=f"证据完整度：{checked_count}/{total_count}")

        if missing:
            st.warning(f"⚠️ 缺失证据：{', '.join(missing)}")
            st.info("💡 提示：缺少这些证据可能会影响维权成功率，请尽快补充。")
        else:
            st.success("✅ 证据已齐全！可以开始维权了。")
            st.balloons()
    # ====================================

    # ========== 12315投诉表单（侧边栏） ==========
    with st.sidebar.expander("📝 生成12315投诉表单", expanded=False):
        st.markdown("填写以下信息，一键生成投诉表单")

        with st.form("complaint_form"):
            complainant_name = st.text_input("投诉人姓名", placeholder="例：张三")
            phone = st.text_input("联系电话", placeholder="例：13812345678")
            merchant_name = st.text_input("被投诉商家名称", placeholder="例：XX旗舰店")
            order_id = st.text_input("订单号", placeholder="例：1234567890")
            product_name = st.text_input("商品名称", placeholder="例：智能手机")
            amount = st.number_input("消费金额（元）", min_value=0.0, step=10.0)
            issue_description = st.text_area("问题描述", placeholder="例：收到商品为假货...")
            demand = st.text_input("诉求", placeholder="例：退款+赔偿", value="退款+赔偿")

            submitted = st.form_submit_button("生成投诉表单", use_container_width=True)

            if submitted:
                if not all([complainant_name, phone, merchant_name, order_id, product_name, amount > 0,
                            issue_description]):
                    st.error("请填写所有必填项")
                else:
                    form_text = generate_12315_form_text(
                        complainant_name=complainant_name,
                        phone=phone,
                        merchant_name=merchant_name,
                        order_id=order_id,
                        product_name=product_name,
                        amount=amount,
                        issue_description=issue_description,
                        demand=demand
                    )
                    st.text_area("生成的投诉表单（可直接复制）", form_text, height=400)
                    st.success("✅ 表单已生成，请复制以上内容到12315平台提交")
    # ============================================

    # 初始化 session state
    if "agent" not in st.session_state:
        with st.spinner("正在初始化维权助手..."):
            try:
                st.session_state["agent"] = ReactAgent()
                st.success("初始化成功！", icon="✅")
            except Exception as e:
                st.error(f"初始化失败：{str(e)}")
                st.stop()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # 显示历史消息或欢迎消息
    if not st.session_state["messages"]:
        # 欢迎消息（首次打开时显示）
        with st.chat_message("assistant"):
            st.markdown("""
            👋 **您好！我是您的网上消费维权助手**

            我可以帮您：
            - 📖 **查询法律依据**（消费者权益保护法、食品安全法等）
            - 💰 **计算赔偿金额**（退一赔三、退一赔十）
            - 📝 **生成投诉信**（支持淘宝、抖音等平台）
            - 📋 **提供证据清单**（维权需要哪些证据）
            - 💬 **生成投诉话术**（与商家沟通的模板）
            - 📞 **查询维权渠道**（12315、12345等）

            **试试问我：**
            > 「300块钱的假货能赔多少？」
            > 「淘宝买手机有坏点，商家不给退怎么办？」
            > 「帮我在抖音写一份投诉信」

            📸 **左侧边栏可以上传聊天截图、快递面单或订单截图**
            """)
    else:
        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # ========== 相似维权案例推荐（根据最新用户问题） ==========
    if st.session_state.get("messages"):
        last_user_msg = ""
        for msg in reversed(st.session_state["messages"]):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break

        if last_user_msg and len(last_user_msg) > 5:
            similar_cases = search_similar_cases(last_user_msg, top_k=3)
            display_cases(similar_cases)
    # ========================================================

    # 用户输入
    prompt = st.chat_input("请输入您的维权问题...")

    # 提示用户同时输入文字
    if uploaded_image and not prompt:
        st.info("💡 请同时输入您的问题，例如「这张快递面单的快递丢了，怎么投诉？」")

    if prompt:
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
            if uploaded_image:
                st.image(uploaded_image, width=200)
                st.caption(f"📎 {uploaded_image.name}")

        # 保存用户消息（含图片信息）
        user_message_content = prompt
        if uploaded_image:
            user_message_content = f"[图片: {uploaded_image.name}]\n{prompt}"
        st.session_state["messages"].append({"role": "user", "content": user_message_content})

        # 生成助手回复
        with st.chat_message("assistant"):
            try:
                with st.spinner("正在分析您的问题..."):
                    # 获取历史消息（最近10条）
                    history = st.session_state["messages"][-10:] if len(st.session_state["messages"]) > 10 else \
                    st.session_state["messages"]

                    # ========== 图片分析 ==========
                    final_prompt = prompt
                    image_description = None

                    if uploaded_image:
                        analyze_status = st.empty()
                        analyze_status.info("📸 正在分析图片内容...")

                        image_base64 = encode_image(uploaded_image)
                        image_description = image_analyzer.analyze_for_agent(image_base64, user_text=prompt)

                        analyze_status.empty()

                        if image_description:
                            final_prompt = f"""【用户问题】{prompt}

【从图片中提取的信息】
{image_description}

请结合以上从图片中提取的信息，回答用户的问题。"""
                            with st.expander("📷 从图片中识别到的信息", expanded=False):
                                st.info(image_description[:500] + ("..." if len(image_description) > 500 else ""))
                        else:
                            st.warning("⚠️ 图片分析失败，将只根据文字问题回答")
                    # ============================

                    # 调用 Agent
                    result = st.session_state["agent"].execute(final_prompt, history=history)

                # 显示思考过程（折叠）
                if result["thinking"]:
                    with st.expander("🧠 查看AI思考过程", expanded=False):
                        st.markdown(result["thinking"])

                # 显示最终回答
                st.markdown(result["answer"])

                # 保存到历史记录
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": result["answer"]
                })

            except Exception as e:
                error_msg = f"❌ 处理您的请求时出错：{str(e)}\n\n请稍后重试或联系客服。"
                st.markdown(error_msg)
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.error(f"Agent 执行错误：{str(e)}")


if __name__ == "__main__":
    main()