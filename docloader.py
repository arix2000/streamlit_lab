import os
import fitz


def load_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return {"filename": os.path.basename(file_path), "text": text}


def load_documents_from_folder(folder_path):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            doc_dict = load_pdf(os.path.join(folder_path, filename))
            docs.append(doc_dict)
    return docs
