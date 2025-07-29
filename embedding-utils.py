import os
from langchain.embeddings import AzureOpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()


embedder = AzureOpenAIEmbeddings(
    deployment_name=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "resume-embedder"),
    openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version=os.getenv("AZURE_OPENAI_VERSION", "2024-12-01-preview"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

def get_embedding(text):
    return embedder.embed_query(text)
