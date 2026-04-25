import os
import fitz

def load_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return doc

def load_documents_from_folder(folder_path):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            text = load_pdf(os.path.join(folder_path, filename))
            docs.append({"filename": filename, "text": text})

    return docs
