import pinecone
import openai

class ConversationMemory:
    def __init__(self, index_name: str, pinecone_api_key: str, pinecone_env: str):
        # Initialize Pinecone
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        self.index = pinecone.Index(index_name)

    def _generate_embedding(self, text: str) -> list:
        # Generate an embedding for the input text using OpenAI's embedding API
        response = openai.Embedding.create(
            input=[text],
            engine="text-embedding-ada-002"
        )
        return response["data"][0]["embedding"]

    def store_conversation(self, conversation_id: str, text: str, metadata: dict = None):
        # Store the conversation fragment with associated metadata into Pinecone
        vector = self._generate_embedding(text)
        self.index.upsert(vectors=[{
            "id": conversation_id,
            "values": vector,
            "metadata": metadata or {}
        }])

    def retrieve_context(self, query: str, top_k: int = 5):
        # Retrieve context by querying the index with a generated embedding from the query
        query_vector = self._generate_embedding(query)
        results = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)
        return results.get("matches", [])
