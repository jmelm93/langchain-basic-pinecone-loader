import pandas as pd
from io import StringIO
from dotenv import load_dotenv
#helpers
from helpers.get_google_documentation import extract_and_convert_html_to_text
from helpers.flatten_extend import flatten_extend
#langchain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
#vector_stores
from vector_stores.pinecone_setup import vector_store

load_dotenv()

csv_path = "source_data/urls.csv"

# csv = """Page Name,URL
# Essentials - Technical,https://developers.google.com/search/docs/essentials/technical
# Essentials - Spam Policies,https://developers.google.com/search/docs/essentials/spam-policies"""

data = pd.read_csv(csv_path)

chat = ChatOpenAI()
# embeddings = OpenAIEmbeddings()

text_splitter = CharacterTextSplitter(
    # Define the separator as a period followed by a newline for splitting text
    separator=".\n", 
    # Set the desired chunk size to be at least 200 characters
    # (may be slightly longer due to waiting for the next "./n" after 200 characters)
    chunk_size=500,
    # Introduce a 50-character overlap between adjacent chunks to maintain contextual coherence
    chunk_overlap=100
)

docs_list_of_lists = []

# get text from html for each row in data
for index, row in data.iterrows():
    print(f'Processing row {index} of {len(data)}')
    text = extract_and_convert_html_to_text(row)
    doc =  Document(
        page_content=text, 
        metadata={
            "page_name": row.get("Page Name"),
            "url": row.get("URL"),
            "doc_group": "Google Search Documentation"
        }
    )
    
    # convert to list for split_documents method
    docs = [doc] 
    
    # convert to list for split_documents method
    split_docs = text_splitter.split_documents(docs)
    
    # append to list
    docs_list_of_lists.append(split_docs)


# flatten list of lists
flattened_docs = flatten_extend(docs_list_of_lists)

# add documents to vector store
vector_store.add_documents(flattened_docs)