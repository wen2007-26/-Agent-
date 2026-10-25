import os
import base64
from dashscope import MultiModalConversation
from http import HTTPStatus
from typing import List, Dict, Any
from work.utils.logger_handler import logger


class ImageAnalyzer:
    """图片分析器：将图片转换为文字描述"""

    def __init__(self, model: str = "qwen-vl-max"):
        self.model = model
        self.api_key = os.environ.get("DASHSCOPE_API_KEY")

    def analyze(self, image_base64: str, question: str = "请描述这张图片中的内容") -> str:
        """
        分析图片，返回文字描述

        Args:
            image_base64: base64 编码的图片
            question: 对图片的提问

        Returns:
            图片的文字描述
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": image_base64},
                    {"text": question}
                ]
            }
        ]

        try:
            response = MultiModalConversation.call(
                model=self.model,
                messages=messages,
                api_key=self.api_key
            )

            if response.status_code == HTTPStatus.OK:
                description = response.output.choices[0].message.content[0]["text"]
                logger.info(f"[图片分析] 分析成功: {description[:100]}...")
                return description
            else:
                logger.error(f"[图片分析] API调用失败: {response.message}")
                return ""

        except Exception as e:
            logger.error(f"[图片分析] 异常: {str(e)}")
            return ""

    def analyze_for_agent(self, image_base64: str, user_text: str = "") -> str:
        """
        为 Agent 分析图片，生成适合 Agent 理解的描述

        Args:
            image_base64: base64 编码的图片
            user_text: 用户同时输入的文本

        Returns:
            用于 Agent 的图片描述文本
        """
        # 根据图片类型确定分析重点
        question = """请分析这张图片，提取以下信息（如果有）：
1. 聊天截图：提取对话内容、商家回复、时间、用户诉求
2. 快递面单：提取快递单号、寄收件人、物流状态
3. 订单截图：提取订单号、商品名称、金额、下单时间

请用简洁的文字描述图片中的关键信息。"""

        if user_text:
            question = f"用户问：{user_text}\n\n" + question

        return self.analyze(image_base64, question)

    def extract_text_from_image(self, image_base64: str) -> str:
        """
        专门提取图片中的文字（OCR功能）
        """
        question = "请提取这张图片中的所有文字内容，按原有顺序输出。"
        return self.analyze(image_base64, question)


# 创建全局实例
image_analyzer = ImageAnalyzer()