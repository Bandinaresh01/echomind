from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from google_auth_oauthlib.flow import Flow

router = APIRouter()

class AuthCodeRequest(BaseModel):
    code: str

@router.post("/auth/google")
async def exchange_google_code(request: AuthCodeRequest):
    client_id = os.getenv("VITE_GOOGLE_CLIENT_ID") 
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google Client credentials not properly configured on the server.")

    client_config = {
        "web": {
            "client_id": client_id,
            "project_id": "echomind",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret
        }
    }

    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/gmail.modify"],
            redirect_uri="postmessage"
        )
        flow.fetch_token(code=request.code)
        credentials = flow.credentials
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
