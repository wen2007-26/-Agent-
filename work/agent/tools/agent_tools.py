from work.agent.tools.complaint_tool import generate_complaint_letter
from work.agent.tools.complaint_form12315 import generate_12315_form
from langchain_core.tools import tool
from work.RAG.rag_service import RagSummarizeService


rag = RagSummarizeService()
external_data = {}


# 1 法律RAG检索
@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    result = rag.rag_summarize(query)
    return result if result else "未在知识库中找到相关信息"


# 2 维权热线渠道
@tool(description="查询网购维权投诉电话、官方线上投诉入口")
def get_rights_hotline(query: str) -> str:
    info = "通用维权拨12315；政务兜底12345；快递纠纷12305；金融保险12378。"
    return info


@tool(description="给出网购维权需要留存的全部证据清单")
def get_evidence_guide(scene: str) -> str:
    guide = "需留存：订单截图、付款记录、聊天记录、商品瑕疵照片、快递面单、宣传页面截图。"
    return guide


@tool(description="从投诉话术知识库检索标准投诉、维权、沟通话术，返回可直接复用的文案")
def get_complain_words(scene: str) -> str:
    """
    检索特定场景的投诉话术

    Args:
        scene: 维权场景描述，如「商家拒绝退货」「假货维权」「快递丢失索赔」

    Returns:
        标准话术文案，纯文本格式，可直接复制使用
    """
    query = f"{scene} 投诉话术 维权沟通模板"
    result = rag.rag_summarize(query)

    # 如果检索结果为空或太短，返回通用话术
    if not result or len(result) < 20:
        return f"【{scene}维权话术】\n根据《消费者权益保护法》，您可以这样与商家沟通：「您的问题属于消费者权益保护范围，请贵司依法处理。如48小时内未解决，我将向12315平台投诉。」"

    return result


# ========== 新增：赔偿金额计算工具 ==========
@tool(description="""根据消费金额和维权类型计算应赔偿金额。""")
def calculate_compensation(amount: float, type: str) -> str:
    """
    计算赔偿金额

    Args:
        amount: 消费金额（元），必须是数字，如 300
        type: 维权类型，中文，如 "假货"、"食品过期"

    Returns:
        返回赔偿金额和计算依据
    """
    # 验证金额合法性
    if amount <= 0:
        return "❌ 金额必须大于0，请提供正确的消费金额。"

    # 退一赔三场景（消法第55条）
    if type in ["假货", "欺诈", "虚假宣传"]:
        compensation = amount * 3
        if compensation < 500:
            compensation = 500
            return f"【赔偿计算结果】\n消费金额：{amount}元\n赔偿金额：{compensation}元\n法律依据：《消费者权益保护法》第55条（欺诈三倍赔偿）\n计算过程：{amount}元 × 3 = {amount * 3}元，不足500元按500元赔偿。"
        else:
            return f"【赔偿计算结果】\n消费金额：{amount}元\n赔偿金额：{compensation}元\n法律依据：《消费者权益保护法》第55条（欺诈三倍赔偿）\n计算过程：{amount}元 × 3 = {compensation}元。"

    # 退一赔十场景（食品安全法第148条）
    elif type in ["食品过期", "食品变质", "食品异物"]:
        compensation = amount * 10
        if compensation < 1000:
            compensation = 1000
            return f"【赔偿计算结果】\n消费金额：{amount}元\n赔偿金额：{compensation}元\n法律依据：《食品安全法》第148条（不符合食品安全标准十倍赔偿）\n计算过程：{amount}元 × 10 = {amount * 10}元，不足1000元按1000元赔偿。"
        else:
            return f"【赔偿计算结果】\n消费金额：{amount}元\n赔偿金额：{compensation}元\n法律依据：《食品安全法》第148条（不符合食品安全标准十倍赔偿）\n计算过程：{amount}元 × 10 = {compensation}元。"

    # 仅退款场景（消法第24条、第25条）
    elif type in ["质量问题", "少发漏发", "7天无理由"]:
        return f"【退款计算结果】\n退款金额：{amount}元\n法律依据：《消费者权益保护法》第{'24' if type != '7天无理由' else '25'}条\n说明：{amount}元全额退款，商家应承担必要费用。"

    # 不支持的类型
    else:
        return f"❌ 不支持的类型「{type}」。\n请使用以下类型：假货、欺诈、虚假宣传、食品过期、食品变质、食品异物、质量问题、少发漏发、7天无理由"