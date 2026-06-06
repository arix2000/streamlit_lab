import streamlit as st
from openai import OpenAI
import os

from docloader import load_pdf, load_documents_from_folder
from embedder_rag import create_index, retrieve_docs

st.set_page_config(layout="wide", page_title="OpenRouter chatbot app")
st.title("OpenRouter chatbot app")

api_key, base_url = st.secrets["API_KEY"], st.secrets["BASE_URL"]
selected_model = "gemini-2.5-flash"

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?."}]

if "faiss_index" not in st.session_state:
    st.session_state["faiss_index"] = None

with st.sidebar:
    files = st.file_uploader('Choose your .pdf file', type="pdf", accept_multiple_files=True)
    if files:
        documents = []
        for uploaded_file in files:
            file_path = os.path.join(".", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            if file_path.endswith(".pdf"):
                doc = load_pdf(file_path)
                documents.append(doc)
            else:
                docs = load_documents_from_folder(file_path)
                documents.extend(docs)

            st.success("SAVED " + file_path)

        if documents:
            with st.spinner("Building index..."):
                st.session_state["faiss_index"] = create_index(documents)
            st.success("Index ready!")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not api_key:
        st.info("Invalid API key.")
        st.stop()

    client = OpenAI(api_key=api_key, base_url=base_url)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    api_messages = list(st.session_state.messages)

    if st.session_state["faiss_index"]:
        retrieved_results = retrieve_docs(prompt, st.session_state["faiss_index"])
        context_texts = [res["text"] for res in retrieved_results]
        combined_context = "\n\n".join(context_texts)

        augmented_prompt = f"Context information:\n{combined_context}\n\nUser Question:\n{prompt}"
        api_messages[-1] = {"role": "user", "content": augmented_prompt}

    response = client.chat.completions.create(
        model=selected_model,
        messages=api_messages
    )

    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)