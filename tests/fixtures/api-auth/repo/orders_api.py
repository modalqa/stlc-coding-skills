"""Request handlers for the orders API (framework-free)."""

TOKENS = {  # synthetic test tokens, not real credentials
    "tok-alice": {"user": "alice", "role": "user"},
    "tok-bob": {"user": "bob", "role": "user"},
    "tok-admin": {"user": "root", "role": "admin"},
}

ORDERS = {
    "1001": {"id": "1001", "owner": "alice", "total": "19.99"},
    "1002": {"id": "1002", "owner": "bob", "total": "5.00"},
}


def _authenticate(request):
    header = request.get("headers", {}).get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return TOKENS.get(header.removeprefix("Bearer "))


def handle(request):
    principal = _authenticate(request)
    if principal is None:
        return 401, {"error": "unauthorized"}
    method, path = request["method"], request["path"]
    parts = path.strip("/").split("/")
    if len(parts) != 2 or parts[0] != "orders":
        return 404, {"error": "not found"}
    order = ORDERS.get(parts[1])
    if method == "GET":
        if order is None:
            return 404, {"error": "not found"}
        return 200, order
    if method == "DELETE":
        if principal["role"] != "admin":
            return 403, {"error": "forbidden"}
        if order is None:
            return 404, {"error": "not found"}
        return 204, None
    return 405, {"error": "method not allowed"}
