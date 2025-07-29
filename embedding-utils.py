import os
from langchain_community.embeddings import AzureOpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()


embedder = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
)
def get_embedding(text):
    return embedder.embed_query(text)
