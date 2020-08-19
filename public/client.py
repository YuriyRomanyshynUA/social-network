from datetime import datetime
from requests import Session

class SocialNetwork:
    
    host = "http://localhost:5000"
    actions = {
        "signup": f"{host}/api/signup",
        "signin": f"{host}/api/signin",
        "refresh-token": f"{host}/api/refresh-token",
        "create-post": f"{host}/api/posts/create",
        "like-post": f"{host}/api/post/like",
        "unlike-post": f"{host}/api/post/unlike",
    }
    
    @classmethod
    def signup(cls, user):
        session = Session()
        data = {
            "email": user["email"],
            "password": user["password"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "city": user["city"],
            "country": user["country"],
            "sex": user["sex"]
        }
        res = session.post(
            cls.actions["signup"],
            json=data
        )
        cls._handle_error(res)
        return cls.signin(user["email"], user["password"])
    
    @classmethod
    def signin(cls, email, password):
        session = Session()
        res = session.post(
            cls.actions["signin"],
            json = {
                "email": email,
                "password": password
            }
        )
        cls._handle_error(res)
        return cls(res.json(), session)
    
    @classmethod
    def _handle_error(cls, res):
        if res.status_code != 200:
            try:
                error_payload = res.json()
                raise Exception(error_payload.get("reason", "Unknown reason"))
            except ValueError:
                raise Exception("Request failed; Unknow error payload.")
    
    def __init__(self, token_payload, session=None):
        self.session = session or Session()
        self._jwt_token = token_payload["token"]
        self._refresh_token = token_payload["refresh_token"]
        self._expires_at = datetime.fromtimestamp(
            token_payload["expires_at"] / 1000.0
        )
        self._ref_token_expires_at = datetime.fromtimestamp(
            token_payload["refresh_token_expires_at"] / 1000.0
        )
    
    def is_expired(self):
        now = datetime.now()
        return True if now >= self._expires_at else False
    
    def is_reresh_token_expired(self):
        now = datetime.now()
        return True if now >= self._ref_token_expires_at else False
    
    def refresh_token(self):
        if self.is_reresh_token_expired():
            raise Exception("Refresh token expired")
        res = self.session.post(
            self.actions["refresh-token"],
            json = {"refresh_token": self._refresh_token},
            headers = {"Authorization": f"Bearer {self._jwt_token}"}
        )
        self._handle_error(res)
        token_payload = res.json()
        self._jwt_token = token_payload["token"]
        self._expires_at = datetime.fromtimestamp(
            token_payload["expires_at"] / 1000.0
        )
    
    def create_post(self, title, content):
        if self.is_expired():
            self.refresh_token()
        res = self.session.post(
            self.actions["create-post"],
            json = {"title": title,"content": content},
            headers = {"Authorization": f"Bearer {self._jwt_token}"}
        )
        self._handle_error(res)
        return res.json()
    
    def like_post(self, post_id):
        if self.is_expired():
            self.refresh_token()
        res = self.session.post(
            self.actions["like-post"],
            params = {"post_id": post_id},
            headers = {"Authorization": f"Bearer {self._jwt_token}"}
        )
        self._handle_error(res)
        return res.json()
    
    def unlike_post(self, post_id):
        if self.is_expired():
            self.refresh_token()
        res = self.session.post(
            self.actions["unlike-post"],
            params = {"post_id": post_id},
            headers = {"Authorization": f"Bearer {self._jwt_token}"}
        )
        self._handle_error(res)
        return res.json()
