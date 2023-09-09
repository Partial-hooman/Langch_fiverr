import sys
import sqlite3
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import os
#import sys
import streamlit as st
import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
import sqlite3
import constants

os.environ["OPENAI_API_KEY"] = st.secrets["db_credentials"]["KEY"]

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = True


query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
  loader = DirectoryLoader("./data")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

#chat_history = []
#while True:
#  if not query:
#    query = input("Prompt: ")
#  if query in ['quit', 'q', 'exit']:
#    sys.exit()
#  result = chain({"question": query, "chat_history": chat_history})
#  print(result['answer'])

#  chat_history.append((query, result['answer']))
#  query = None

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message[0]):
        st.markdown(message[1])

if prompt := st.chat_input("enter your query:"):
    #st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        prompt_placeholder = st.empty()
        prompt_placeholder.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        #full_response = ""
        result = chain({"question": prompt, "chat_history": st.session_state.messages})
            
        
        message_placeholder.markdown(result['answer'])
    st.session_state.messages.append((prompt,result['answer']))
