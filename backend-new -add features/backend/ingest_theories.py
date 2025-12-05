import weaviate
import os
from pypdf import PdfReader
import sys
from weaviate.auth import AuthApiKey
from weaviate.classes.config import Configure, Property, DataType
from app.core.config import settings

# --- Weaviate Client Setup ---
try:
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=settings.WEAVIATE_URL,
        auth_credentials=AuthApiKey(settings.WEAVIATE_API_KEY),
        headers={"X-Goog-Api-Key": settings.GEMINI_API_KEY}
    )
    print("✅ Connected to Weaviate for ingestion.")
except Exception as e:
    print(f"❌ Could not connect to Weaviate: {e}")
    client = None

def setup_weaviate_schema():
    """Defines and creates the Theory collection in Weaviate."""
    if not client:
        return
    
    collection_name = "Theory"
    if client.collections.exists(collection_name):
        print(f"✅ Collection '{collection_name}' already exists.")
        return

    print(f"⏳ Creating '{collection_name}' collection...")
    client.collections.create(
    name=collection_name,
    vector_config=[
        Configure.Vectors.text2vec_google(
            name="default",
            source_properties=["content", "language", "subject", "source_file"],
            project_id=settings.GCP_PROJECT_ID,
            
        )
    ],
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="language", data_type=DataType.TEXT),
        Property(name="subject", data_type=DataType.TEXT),
        Property(name="source_file", data_type=DataType.TEXT),
    ]
    )
    print(f"✅ Collection '{collection_name}' created successfully.")

def ingest_documents(folder_path: str, language: str, subject: str):
    """Reads all files from a folder, chunks them, and upserts to Weaviate."""
    if not client:
        return
        
    theories = client.collections.get("Theory")
    
    with theories.batch.dynamic() as batch:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            text_content = ""
            
            print(f"-> Processing file: {filename}")
            if filename.lower().endswith(".pdf"):
                try:
                    with open(file_path, 'rb') as f:
                        reader = PdfReader(f)
                        for page in reader.pages:
                            text_content += page.extract_text() + "\n"
                except Exception as e:
                    print(f"   - ❌ Error reading PDF {filename}: {e}")
                    continue
            elif filename.lower().endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            else:
                print(f"   - Skipping unsupported file: {filename}")
                continue

            chunks = [chunk for chunk in text_content.split('\n\n') if len(chunk.strip()) > 50]
            print(f"   - Found {len(chunks)} chunks.")

            for chunk in chunks:
                properties = {
                    "content": chunk.strip(),
                    "language": language.lower(),
                    "subject": subject.title(),
                    "source_file": filename,
                }
                batch.add_object(properties=properties)
    
    print(f"\n✅ Finished ingestion for {folder_path}.")
    if len(theories.batch.failed_objects) > 0:
        print(f"⚠️ WARNING: {len(theories.batch.failed_objects)} objects failed to import.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python ingest_theories.py <folder_path> <language> <subject>")
        sys.exit(1)

    folder_path = sys.argv[1]
    language = sys.argv[2]
    subject = sys.argv[3]

    if not os.path.isdir(folder_path):
        print(f"❌ Error: Folder not found at '{folder_path}'")
        sys.exit(1)

    if client:
        setup_weaviate_schema()
        ingest_documents(folder_path, language, subject)
        client.close()
        print("✅ Weaviate client connection closed.")