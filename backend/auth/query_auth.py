from fastapi import FastAPI, Security, HTTPException
from fastapi.security.api_key import APIKeyQuery
from starlette.status import HTTP_403_FORBIDDEN

# 1. Define query parameter name
API_KEY_NAME = "api_query"
API_KEY = "supersecretapikey"

# 2. Create the APIKeyQuery object
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)


# 3. Dependency to validate API key
async def get_api_query(api_key: str = Security(api_key_query)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Could not validate API Key",
    )
