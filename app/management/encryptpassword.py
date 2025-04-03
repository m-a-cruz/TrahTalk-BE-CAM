from flask_bcrypt import Bcrypt
import management.cipherprivatekey as cipher

bcrypt = Bcrypt()

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password,password):
    return bcrypt.check_password_hash(hashed_password, password)

# def generate_token(email):
#     token = jwt.encode({"email": email, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, 
#                         cipher.SECRET_KEY, algorithm="HS256")
#     return token

# def decode_token(token):
#     return jwt.decode(token.split()[1], cipher.SECRET_KEY, algorithms=["HS256"])