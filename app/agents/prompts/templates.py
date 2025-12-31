from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.prompts.system import (
    content_type_extract_system_prompt,
    reranker_system_prompt,
)
from app.schemas.chat_schema import RankedDocs
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=RankedDocs)


content_type_extract_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=content_type_extract_system_prompt),
        HumanMessage(content="Query:{query}"),
    ]
)

reranker_template = ChatPromptTemplate.from_messages(
    [
        ("system", reranker_system_prompt),
        (
            "human",
            """
            Query: {query}
            Documents:
            {docs_text}
            """,
        ),
    ]
)
