
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from work.RAG.vector_store import VectorStoreService
from work.utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from work.model.factory import chat_model
from langchain_core.runnables import RunnableLambda


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


#RAG服务类->初始化向量库和检索器
class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()#向量存储
        self.retriever = self.vector_store.get_retriever()#检索器
        self.prompt_text = load_rag_prompts()#提示词文本
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)#提示词模板
        self.model = chat_model
        self.chain = self._init_chain()

#构建LCEL处理链
    def _init_chain(self):
        chain = self.prompt_template | RunnableLambda(print_prompt) | self.model | StrOutputParser()
        return chain

#方法
    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

#检索相关文档
    def rag_summarize(self, query: str) -> str:

        context_docs = self.retriever_docs(query)

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】: 参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

#调用模型概括参考资料
        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )



