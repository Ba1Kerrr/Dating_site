from pydantic import BaseModel, EmailStr


class UserSchemas(BaseModel):
    username: str
    email: str
    age: int = None
    gender: str = None
    location: str = None
    avatar: str = None
    bio: str = None


class UserAddSchemas(UserSchemas):
    username: str
    email: str
    password: str
    confirm_password: str
    input_key: int


class EmailSchema(BaseModel):
    email: EmailStr