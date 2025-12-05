import weaviate
from weaviate.auth import AuthApiKey
from typing import List, Dict

# Corrected imports for modern query syntax
from weaviate.classes.query import Filter, MetadataQuery

from app.core.config import settings

# --- Initialize Weaviate Client ---
try:
    client = weaviate.connect_to_wcs(
        cluster_url=settings.WEAVIATE_URL,
        auth_credentials=AuthApiKey(settings.WEAVIATE_API_KEY),
        headers={
            "X-Google-Api-Key": settings.GEMINI_API_KEY
        }
    )
    print("Successfully connected to Weaviate.")
except Exception as e:
    print(f"Error connecting to Weaviate: {e}")
    client = None

def get_theory_collection():
    """Gets a reference to the Theory collection in Weaviate."""
    if not client:
        raise ConnectionError("Weaviate client is not initialized.")
    return client.collections.get("Theory")

# --- Querying Function ---
def find_similar_theories(topic: str, language: str, subject: str, num_results: int = 3) -> List[Dict]:
    """
    Finds and returns relevant theory content directly from Weaviate using modern syntax.
    """
    try:
        theories = get_theory_collection()
        
        # --- THIS IS THE UPDATED QUERY SYNTAX ---
        response = theories.query.near_text(
            query=topic,
            # The filter syntax has been updated
            filters=(
                Filter.by_property("language").equal(language.lower()) &
                Filter.by_property("subject").equal(subject.title())
            ),
            limit=num_results,
            return_metadata=MetadataQuery(distance=True)
        )
        
        results = []
        for item in response.objects:
            result = {
                "content": item.properties.get("content"),
                "subject": item.properties.get("subject"),
                "language": item.properties.get("language"),
                "source_file": item.properties.get("source_file"),
                "distance": item.metadata.distance,
            }
            results.append(result)
        return results

    except Exception as e:
        print(f"Error querying Weaviate: {e}")
        return []