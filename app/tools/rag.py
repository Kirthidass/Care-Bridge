import requests
import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
from google.adk.tools import BaseTool

# This tool acts as the "Medical Library".
# It uses ChromaDB to store and retrieve chunks of text from medical guidelines.
# We use Hugging Face for "embeddings" (turning text into numbers for search).

class MedicalRAGTool(BaseTool):
    name = "medical_rag"
    description = "Searches medical guidelines for relevant context."

    def __init__(self):
        super().__init__(name="medical_rag", description="Searches medical guidelines for relevant context.")
        # Initialize ChromaDB (persistent storage)
        self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_DIR)
        
        # We use a simple local embedding function via Chroma's built-in SentenceTransformers default
        # Or we could call HF API if local is too heavy. Let's try default lightweight local first.
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="medical_guidelines", 
            embedding_function=self.ef
        )

    def add_knowledge(self, text_chunks: list, source_name: str):
        """
        Adds new medical knowledge to the library.
        """
        ids = [f"{source_name}_{i}" for i in range(len(text_chunks))]
        metadatas = [{"source": source_name} for _ in text_chunks]
        
        self.collection.add(
            documents=text_chunks,
            ids=ids,
            metadatas=metadatas
        )

    def run(self, query: str):
        """
        Retrieves the top 3 most relevant medical facts for a query.
        """
        print(f"--- [RAG] Searching for: {query} ---")
        results = self.collection.query(
            query_texts=[query],
            n_results=3
        )
        
        # Format results into a single string context
        context_str = ""
        if results['documents']:
            context_str = "\n".join(results['documents'][0])
        
        return context_str if context_str else "No specific medical guidelines found for this."
