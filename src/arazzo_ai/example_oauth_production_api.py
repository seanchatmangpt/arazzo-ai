import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

# Initialize FastAPI and logging
app = FastAPI(title="Example OAuth Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models for request validation
class TokenRequest(BaseModel):
    grant_type: str
    client_id: str
    client_secret: str
    redirect_uri: Optional[str] = None
    code: Optional[str] = None
    refresh_token: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"

@app.post("/oauth/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    logger.info(f"Token request received: {request}")

    if request.grant_type == "authorization_code":
        if request.code != "auth-code-my-client-id-fixed":
            logger.error(f"Invalid authorization code: {request.code}")
            raise HTTPException(status_code=400, detail="Invalid authorization code")

        # Use hardcoded tokens for consistency
        return TokenResponse(
            access_token="access-token-my-client-id-fixed",
            refresh_token="refresh-token-my-client-id-fixed",
            expires_in=3600
        )

    elif request.grant_type == "refresh_token":
        if request.refresh_token != "refresh-token-my-client-id-fixed":
            logger.error(f"Invalid refresh token: {request.refresh_token}")
            raise HTTPException(status_code=400, detail="Invalid refresh token")

        # Use hardcoded tokens for consistency
        return TokenResponse(
            access_token="access-token-my-client-id-fixed-new",
            refresh_token="refresh-token-my-client-id-fixed",
            expires_in=3600
        )

    elif request.grant_type == "client_credentials":
        # Use hardcoded tokens for consistency
        return TokenResponse(
            access_token="access-token-my-client-id-cc-fixed",
            refresh_token="",
            expires_in=3600
        )

    else:
        logger.error(f"Unsupported grant type: {request.grant_type}")
        raise HTTPException(status_code=400, detail="Unsupported grant type")

@app.get("/authorize")
async def authorize(client_id: str, redirect_uri: str, response_type: str, scope: str, state: str):
    # Return a hardcoded authorization code for testing
    return {"code": "auth-code-my-client-id-fixed", "state": state}

# Health check endpoint for easier deployment checks
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Run the app with a Typer CLI if required
if __name__ == "__main__":
    import typer
    import uvicorn

    app_cli = typer.Typer()

    @app_cli.command()
    def run():
        uvicorn.run("example_oauth_production_api:app", host="0.0.0.0", port=8000, reload=True)

    app_cli()
