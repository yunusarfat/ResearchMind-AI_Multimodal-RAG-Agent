"""Shared request/response schemas for the API layer."""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str  # the Google ID token obtained by the frontend


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    auth_provider: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    num_pages: int
    num_chunks: int
    duplicate: bool = False


class ChatQueryRequest(BaseModel):
    query: str
    chat_id: str  # every query belongs to a chat; the frontend creates one first


class CitationResponse(BaseModel):
    marker: str
    chunk_id: str
    document_id: str
    page_number: int | None
    section: str | None
    content_type: str
    snippet: str
    source_url: str | None = None


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: list[CitationResponse] = Field(default_factory=list)
    created_at: str  # ISO 8601


class ChatSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ChatDetail(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[MessageResponse]


class ChatCreateRequest(BaseModel):
    title: str | None = None  # optional; defaults to "New chat", renamed after first message
