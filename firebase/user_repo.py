from .client import get_db

def create_user(username: str, password_hash: str) -> dict:
    """Creates a user in RTDB. Returns user dict."""
    db = get_db()
    users_ref = db.reference("users")
    # check if exists
    existing = users_ref.order_by_child("username").equal_to(username).get()
    if existing:
        return None # User exists
    
    new_user_ref = users_ref.push()
    user_data = {
        "id": new_user_ref.key,
        "username": username,
        "password_hash": password_hash
    }
    new_user_ref.set(user_data)
    return user_data

def get_user_by_username(username: str) -> dict:
    db = get_db()
    users_ref = db.reference("users")
    users = users_ref.order_by_child("username").equal_to(username).get()
    if users:
        key = list(users.keys())[0]
        return users[key]
    return None
