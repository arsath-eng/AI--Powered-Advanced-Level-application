# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

from app.crud import crud
from app.schemas import schemas
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, get_db, verify_refresh_token
from jose import JWTError, jwt

router = APIRouter()
oauth = OAuth()

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/drive.readonly'
    }
)

@router.get("/auth/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/callback", name="auth_google_callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials from Google")

    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="User info not in token")

    google_id = user_info['sub']
    email = user_info['email']
    full_name = user_info['name']

    db_user = crud.get_user_by_google_id(db, google_id=google_id)
    if not db_user:
        user_create = schemas.UserCreate(google_id=google_id, email=email, full_name=full_name)
        db_user = crud.create_user(db, user_create)

    access_token = create_access_token(data={"sub": db_user.google_id})
    refresh_token = create_refresh_token(data={"sub": db_user.google_id})

    # Store tokens in the database
    db_user.access_token = access_token
    db_user.refresh_token = refresh_token
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    response = RedirectResponse(
        url=f"http://localhost:3000/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    )
    return response

@router.post("/token/refresh", response_model=schemas.Token)
async def refresh_token(refresh_token: str = Form(...), db: Session = Depends(get_db)):
    user = verify_refresh_token(refresh_token, db)
    access_token = create_access_token(data={"sub": user.google_id})

    # Update access_token in the database
    user.access_token = access_token
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"access_token": access_token, "token_type": "bearer"}
