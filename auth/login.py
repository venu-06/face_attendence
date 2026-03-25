from utils.db import get_db
from utils.hash import verify_password

def authenticate(email, password):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, password FROM students WHERE email=?", (email,))
    user = cur.fetchone()
    db.close()

    if user and verify_password(user[1], password):
        return user[0]
    return None
