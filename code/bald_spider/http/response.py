from typing import Dict, Optional
from bald_spider import Request
import ujson
import re
from bald_spider.execptions import DecodeError
from urllib.parse import urljoin as _urljoin
from parsel import Selector


class Response:
    def __init__(
            self,
            url: str,
            *,
            request: Request,
            headers: Optional[Dict] = None,
            body: bytes = b"",
            status: int = 200
    ):
        self.url = url
        self.request = request
        self.headers = headers
        self.body = body
        self.status = status
        self.encoding = request.encoding
        # 设置缓存
        self._text_cache = None
        self._selector = None

    @property
    def text(self):
        """
        这个地方实际上是我们得到的body是bytes类型，但是我们得到数据需要转化成数据类型
        但是text = body.decode(),我们并不想存储两份，定义这个属性方法，需要用到的时候直接调用就行
        """
        if self._text_cache:
            return self._text_cache
        try:
            # 使用默认的encoding并不一定能decode成功
            self._text_cache = self.body.decode(self.encoding)
        except UnicodeDecodeError:
            try:
                # 从网页headers中的Content-Type处可以拿到encoding尝试进行decode
                _encoding_re = re.compile(r"charset=([\w-]+)", flags=re.I)
                _encoding_string = self.headers.get("Content-Type", "") or self.headers.get("content-type", "")
                _encoding = _encoding_re.search(_encoding_string)
                if _encoding:
                    _encoding = _encoding.group(1)
                    self._text_cache = self.body.decode(self.encoding)
                else:
                    raise DecodeError(f"{self.request} {self.request.encoding} error")
            except UnicodeDecodeError as exc:
                raise UnicodeDecodeError(
                    exc.encoding, exc.object, exc.start, exc.end, f"{self.request}"
                )
        return self._text_cache

    def json(self):
        return ujson.loads(self.text)

    def urljoin(self, url):
        return _urljoin(self.url, url)

    def xpath(self,xpath_string):
        if self._selector is None:
            self._selector = Selector(self.text)
        return self._selector.xpath(xpath_string)

    def __str__(self):
        return f"<{self.status}> {self.url}"

    @property
    def meta(self):
        return self.request.meta


