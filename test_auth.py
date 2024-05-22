import jwt
from comotion.auth import Auth
import json
    
public_key = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkSIAZaQ93DgrUjht+HHWpZzjugAP/4FtSkbB5XbSu7k18IYZFIUE0Xv6IE7nmZY2yThta+QZG0znCaMKbTNg13Fq5Smylaj/OMJ6ZvOMhBLdKmIow8NJtTWgVQlM18sNUsAqpUwGywsemh1ohfdBRBF6ykvb8woA/lq4XqTDMovNEiBuDPn/GK3P+BlP3IIWLQcHow4DWfs8TtZxsNQzXtRFtWByNtOfIGt+Wb83/W8dpjW8pnLzaOgeIHWMd8QLhEf0xhpmi3nvyuWfdutu88sqgoo2ZRBvP7gllaqBbHNSFMHXiwt5Bi2Fu0BCOmYj0pT+n5AaPpfQEVdahztyKQIDAQAB
-----END PUBLIC KEY-----
"""


access_token=(Auth(
    entity_type=Auth.APPLICATION,
    application_client_id="test",
    application_client_secret="P8YnJ9RPvoonPShaMv6kaoOFqgabY1Ei",
    orgname="poc2"
).get_access_token())

# Decoding the JWT
try:
    decoded_payload = jwt.decode(access_token, public_key,  options={"verify_signature": False})
    print("\nDecoded JWT payload:")
    print(json.dumps(decoded_payload, indent=4))
except jwt.ExpiredSignatureError:
    print("The token has expired.")
except jwt.InvalidTokenError as e:
    print(e)
    print("The token is invalid.")