from langchain_core.tools import tool
from work.RAG.rag_service import RagSummarizeService
from datetime import datetime

# 直接复用你现有的RAG服务
rag = RagSummarizeService()

# 平台模板库
COMPLAINT_TEMPLATES = {
    "淘宝": """
【淘宝官方投诉申诉书】
订单编号：{order_id}
店铺名称：{shop_name}
问题描述：{user_problem}
平台政策依据：{policy_context}
法律法规依据：{law_context}
本人诉求：{user_demand}

请淘宝平台按官方规则介入处理，维护消费者合法权益。
投诉人：消费者
日期：{now_date}
""",

    "抖音": """
【抖音电商申诉函】
账号：{user_account}
订单号：{order_id}
问题描述：{user_problem}
平台政策：{policy_context}
法律依据：{law_context}
申诉诉求：{user_demand}

恳请抖音平台依规核查处理。
申诉人：消费者
日期：{now_date}
""",

    "通用": """
【{platform} 投诉书】
订单：{order_id}
问题：{user_problem}
政策依据：{policy_context}
法律依据：{law_context}
诉求：{user_demand}

请平台依法处理。
日期：{now_date}
"""
}

@tool(description="智能生成规范投诉信/申诉书，支持淘宝、抖音、通用平台自动适配")
def generate_complaint_letter(
    platform: str,
    issue: str,
    user_problem: str,
    order_id: str = "",
    shop_name: str = "",
    user_account: str = "",
    user_demand: str = "全额退款+平台介入处理"
) -> str:
    """
    自动生成维权投诉信，自动检索政策+法律依据
    """
    # 1. 检索平台政策（完全复用你现有的rag_summarize）
    policy_query = f"{platform} {issue} 维权政策 投诉规则"
    policy_context = rag.rag_summarize(policy_query)

    # 2. 检索法律依据（消保法）
    law_query = f"消费者权益保护法 {issue} 相关规定"
    law_context = rag.rag_summarize(law_query)

    # 3. 自动生成时间
    now_date = datetime.now().strftime("%Y年%m月%d日")

    # 4. 选择模板
    template = COMPLAINT_TEMPLATES.get(platform, COMPLAINT_TEMPLATES["通用"])

    # 5. 填充生成最终文书
    letter = template.format(
        platform=platform,
        issue=issue,
        user_problem=user_problem,
        order_id=order_id,
        shop_name=shop_name,
        user_account=user_account,
        user_demand=user_demand,
        policy_context=policy_context,
        law_context=law_context,
        now_date=now_date
    )

    return letter