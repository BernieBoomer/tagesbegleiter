"""
REKONSTRUIERT am 08.08.2026. Dieser Code wurde im Chat-Verlauf (Antwort von Bodo)
im Wortlaut gezeigt und hier unverändert übernommen — im Gegensatz zu transcribe.py
und waste.py ist das also näher am Original als eine reine Spezifikations-Rekonstruktion.

Trotzdem: nach dem Deployment erneut testen (401 ohne Key, 401 falscher Key,
200 richtiger Key, 500 bei fehlendem API_KEY in der Umgebung).
"""

import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY = os.environ.get("TAGESBEGLEITER_API_KEY", "")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server",
        )
    if not api_key or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key
