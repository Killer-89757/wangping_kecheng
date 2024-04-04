from typing import Dict, Optional,Callable


class Request:
    def __init__(
            self, url: str, *,
            headers: Optional[Dict] = None,
            callback:Callable = None,
            priority: int = 0,
            method: str = "GET",
            cookies: Optional[Dict] = None,
            proxy: Optional[Dict] = None,
            body=""
    ):
        self.url = url
        self.headers = headers
        self.callback = callback
        self.priority = priority
        self.method = method
        self.cookies = cookies
        self.proxy = proxy
        self.body = body
