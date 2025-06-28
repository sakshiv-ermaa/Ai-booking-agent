from pydantic import BaseModel, field_validator

class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty.")
        return v
