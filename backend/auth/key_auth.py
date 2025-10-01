from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

# Define the header name
API_KEY_NAME = "api_key"
API_KEY = "supersecretapikey"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# Dependency that validates the API key
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Could not validate API Key",
    )
