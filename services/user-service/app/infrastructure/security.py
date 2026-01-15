from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BcryptHasher:
    def hash(self, password: str) -> str:
        return _pwd.hash(password)