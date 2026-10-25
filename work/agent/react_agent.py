from langchain.agents import create_agent
from work.model.factory import chat_model
from work.utils.prompt_loader import load_system_prompts
from work.agent.tools.agent_tools import (rag_summarize, get_rights_hotline, get_evidence_guide, get_complain_words,
                                          generate_complaint_letter,calculate_compensation,generate_12315_form)
from work.agent.tools.middleware import monitor_tool, log_before_model


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize, get_rights_hotline, get_evidence_guide, get_complain_words,
                   generate_complaint_letter,calculate_compensation,generate_12315_form],
            middleware=[monitor_tool, log_before_model],
        )

    def execute(self, query: str, history: list = None) -> dict:
        """
        非流式执行Agent，返回思考过程和最终回答

        Args:
            query: 用户输入的问题
            history: 历史消息列表，格式 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

        Returns:
            dict: 包含 thinking 和 answer 两个字段
        """
        # 构建消息列表
        messages = []

        # 添加历史消息（只保留最近10条，即5轮对话）
        if history:
            recent_history = history[-10:] if len(history) > 10 else history
            messages.extend(recent_history)

        # 添加当前用户消息
        messages.append({"role": "user", "content": query})

        input_dict = {
            "messages": messages
        }

        thinking_steps = []
        final_answer = None

        # 遍历Agent的执行过程
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                content = latest_message.content.strip()

                if content.startswith("【思考】") or content.startswith("【观察】"):
                    thinking_steps.append(content)
                elif content.startswith("【回答】"):
                    final_answer = content.replace("【回答】", "").strip()
                else:
                    if content:
                        final_answer = content

        result = {
            "thinking": "\n\n".join(thinking_steps) if thinking_steps else "",
            "answer": final_answer if final_answer else "抱歉，我暂时无法回答这个问题。"
        }

        return result