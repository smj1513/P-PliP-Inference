from app.core.llm import mini_llm
from app.agents.prompts.templates import reranker_template
from app.schemas.chat_schema import RankedDocs

rerank_chain = reranker_template | mini_llm.with_structured_output(RankedDocs)
