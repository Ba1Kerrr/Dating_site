from passlib.context import CryptContext
from passlib.exc import UnknownHashError
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    try:
        return pwd_context.hash(password)
    except UnknownHashError as e:
        print(f"Error: {e}")
        return None