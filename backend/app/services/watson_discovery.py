"""
IBM Watson Discovery integration (optional).
If credentials are provided, queries the Watson Discovery collection.
Otherwise, returns None to signal fallback.
"""
from typing import Optional
from app.core.config import settings

def query_discovery(query_text: str, count: int = 3) -> Optional[str]:
    """
    Search Watson Discovery for relevant agricultural documents.
    Returns a concatenated string of passages, or None if not configured.
    """
    if not all([settings.WATSON_DISCOVERY_API_KEY,
                settings.WATSON_DISCOVERY_PROJECT_ID,
                settings.WATSON_DISCOVERY_COLLECTION_ID]):
        return None  # not configured → fallback

    try:
        from ibm_watson import DiscoveryV2
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

        authenticator = IAMAuthenticator(settings.WATSON_DISCOVERY_API_KEY)
        discovery = DiscoveryV2(
            version="2023-03-31",
            authenticator=authenticator
        )
        discovery.set_service_url(settings.WATSON_DISCOVERY_URL)

        response = discovery.query(
            project_id=settings.WATSON_DISCOVERY_PROJECT_ID,
            collection_ids=[settings.WATSON_DISCOVERY_COLLECTION_ID],
            natural_language_query=query_text,
            count=count,
            return_fields=["text"],
        ).get_result()

        passages = []
        for result in response.get("results", []):
            text = result.get("text")
            if text:
                passages.append(text.strip())
        if passages:
            return "\n\n".join(passages)
        return None
    except Exception as e:
        print(f"⚠️  Watson Discovery query failed: {e}")
        return None