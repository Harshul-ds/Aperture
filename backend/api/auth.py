# backend/api/auth.py

from fastapi import APIRouter, Depends, HTTPException
from backend.core.auth_service import AuthService, auth_service

# An APIRouter allows us to group related endpoints together.
router = APIRouter()

@router.post("/google", summary="Initiate or Verify Google OAuth2 Flow")
def start_or_verify_google_auth(
    service: AuthService = Depends(lambda: auth_service)
):
    """
    This endpoint is the single point of contact for authentication.
    It will either verify existing tokens or start the new user consent flow.
    """
    try:
        credentials = service.get_credentials()
        if credentials and credentials.valid:
            # You can add more logic here, like returning the user's email address
            return {"status": "success", "message": "Successfully authenticated with Google."}
        else:
            # This case shouldn't be hit if the flow works, but it's a good fallback.
            raise HTTPException(status_code=401, detail="Authentication failed or was cancelled.")
    except Exception as e:
        # This catches errors like a missing client_secret.json file
        print(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during authentication: {str(e)}")