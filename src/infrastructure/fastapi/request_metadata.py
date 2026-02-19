from fastapi import Request


def get_x_forwarded_for(request: Request) -> str:
    return request.headers.get("X-Forwarded-For", "").strip()


def get_client_ip(request: Request) -> str:
    forwarded_for = get_x_forwarded_for(request)
    if forwarded_for:
        first_hop = forwarded_for.split(",")[0].strip()
        if first_hop:
            return first_hop

    x_real_ip = request.headers.get("X-Real-IP", "").strip()
    if x_real_ip:
        return x_real_ip

    if request.client and request.client.host:
        return request.client.host

    return "unknown"
