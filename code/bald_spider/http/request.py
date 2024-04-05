from typing import Dict, Optional, Callable


class Request:
    def __init__(
            self, url: str, *,
            headers: Optional[Dict] = None,
            callback: Callable = None,
            priority: int = 0,
            method: str = "GET",
            cookies: Optional[Dict] = None,
            proxy: Optional[Dict] = None,
            body="",
            encoding="utf-8",
            # 和请求无关，但是和运行流程有关
            meta:Optional[Dict] = None
    ):
        self.url = url
        self.headers = headers
        self.callback = callback
        self.priority = priority
        self.method = method
        self.cookies = cookies
        self.proxy = proxy
        self.body = body
        self.encoding = encoding
        self._meta = meta if meta is not None else {}

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        return f"{self.url} {self.method}"

    @property
    def meta(self):
        return self._meta
