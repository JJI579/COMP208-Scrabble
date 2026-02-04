import jwt
import os
from dotenv import load_dotenv
import datetime

cwd = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')

class Authentication:
	
    def __init__(self):
        secret_key = os.getenv('SECRET_KEY')
        if secret_key is None:
            # this will never be true.
            self.secret_key = "dxd"
        else:
            self.secret_key = secret_key

    def create_access_token(self, user_id: int, expires_at=86400):
        expiry = datetime.datetime.now(datetime.timezone.utc).timestamp() + expires_at
        jwt_token = {
            "type": "bearer",
            "id": user_id,
            "exp": expiry
        }
        return jwt.encode(jwt_token, self.secret_key, algorithm="HS256"), expiry

    def decode_access_token(self, token: str):
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except: 
            raise Exception("Invalid Token")