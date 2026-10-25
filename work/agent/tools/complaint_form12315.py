from langchain_core.tools import tool
from datetime import datetime
from typing import Optional


@tool
def generate_12315_form(
        complainant_name: str,
        phone: str,
        merchant_name: str,
        order_id: str,
        product_name: str,
        amount: float,
        issue_description: str,
        demand: str = "退款+赔偿"
) -> str:
    """
    生成12315投诉表单（文本格式）

    Args:
        complainant_name: 投诉人姓名
        phone: 联系电话
        merchant_name: 被投诉商家名称
        order_id: 订单号
        product_name: 商品名称
        amount: 消费金额
        issue_description: 问题描述
        demand: 诉求（默认：退款+赔偿）

    Returns:
        格式化的12315投诉表单文本
    """
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
    """纯文本版本（供直接调用）"""
    now_date = datetime.now().strftime("%Y年%m月%d日")

    form = f"""
========== 12315 投诉举报表单 ==========

【投诉人信息】
姓名：{complainant_name}
电话：{phone}

【被投诉方信息】
商家名称：{merchant_name}

【订单信息】
订单号：{order_id}
商品名称：{product_name}
消费金额：{amount}元

【投诉内容】
问题描述：{issue_description}

【投诉诉求】
{demand}

【提交时间】
{now_date}

=========================================
使用说明：
1. 复制以上内容
2. 访问 https://www.12315.cn/
3. 登录后选择「我要投诉」，粘贴提交
"""
    return form