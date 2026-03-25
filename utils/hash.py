from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(pwd):
    return generate_password_hash(pwd)

def verify_password(hash, pwd):
    return check_password_hash(hash, pwd)
