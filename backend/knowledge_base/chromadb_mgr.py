import os
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


class ChromaDBManager:
    def __init__(
        self, emb_api_key: str, emb_base_url: str, emb_model_name: str
    ) -> None:
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
        )
        self.embedding_function = OpenAIEmbeddingFunction(
            api_base=emb_base_url,
            api_key=emb_api_key,
            model_name=emb_model_name,
        )

    def create_collection(self, name: str):
        """创建一个新的集合"""
        return self.chroma_client.get_or_create_collection(
            name=name,
            embedding_function=self.embedding_function,  # type: ignore
        )

    def upsert(self, collection_name: str, documents: list[str], ids: list[str]):
        """向指定集合中插入或更新文档"""
        collection = self.chroma_client.get_collection(
            name=collection_name,
            embedding_function=self.embedding_function,  # type: ignore
        )
        collection.upsert(documents=documents, ids=ids)

    def query(self, collection_name: str, query: str, n_results: int = 5):
        """查询指定集合中的文档"""
        collection = self.chroma_client.get_collection(
            name=collection_name, embedding_function=self.embedding_function # type: ignore
        )
        results = collection.query(query_texts=[query], n_results=n_results)
        return results

# global
chroma_db_manager = ChromaDBManager(
    emb_api_key=os.getenv("EMBEDDING_API_KEY", ""),
    emb_base_url=os.getenv("EMBEDDING_API_BASE_URL", "https://api.openai.com/v1/embeddings"),
    emb_model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
)
