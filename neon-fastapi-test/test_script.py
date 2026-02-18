import hmac, hashlib, os
secret = b"test_webhook_secret_value"
body = b'{"repository":{"full_name":"me/repo"},"ref":"refs/heads/main","commits":[] }'
print("sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest())