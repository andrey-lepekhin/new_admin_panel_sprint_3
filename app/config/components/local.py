INTERNAL_IPS = [
    '127.0.0.1',
]

# To make debug toolbar work in Docker
if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

# For swagger webui requests to work
CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:8080",]
