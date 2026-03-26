# ─────────────────────────────────────────────
# ssl_patch.py
#
# Purpose : Global SSL bypass for restricted/corporate networks
# Import  : Must be imported FIRST in api.py and data_loader.py
# ─────────────────────────────────────────────

import os
import ssl
import urllib.request
import urllib3

# 1. Python ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 2. urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 3. urllib.request (standard library HTTPS calls)
_ssl_ctx = ssl._create_unverified_context()
_opener  = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_ssl_ctx))
urllib.request.install_opener(_opener)

_orig_urlopen = urllib.request.urlopen
def _patched_urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, **kwargs):
    if "context" not in kwargs:
        kwargs["context"] = _ssl_ctx
    return _orig_urlopen(url, data=data, timeout=timeout, **kwargs)

try:
    import socket
    urllib.request.urlopen = _patched_urlopen
except Exception:
    pass

# 4. requests.Session (News API, Wiki, World Bank)
import requests
_orig_req = requests.Session.request
def _patched_req(self, method, url, **kwargs):
    kwargs["verify"] = False
    return _orig_req(self, method, url, **kwargs)
requests.Session.request = _patched_req

# 5. httpx — used by ChromaDB DefaultEmbeddingFunction (line: httpx.stream("GET", url))
import httpx

_orig_client_init = httpx.Client.__init__
def _patched_client_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _orig_client_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_client_init

_orig_async_client_init = httpx.AsyncClient.__init__
def _patched_async_client_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _orig_async_client_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = _patched_async_client_init

_orig_stream = httpx.stream
def _patched_stream(method, url, **kwargs):
    kwargs["verify"] = False
    return _orig_stream(method, url, **kwargs)
httpx.stream = _patched_stream

# 6. curl_cffi (used by yfinance)
try:
    import curl_cffi.requests as _curl
    _orig_curl_init = _curl.Session.__init__
    def _patched_curl_init(self, *args, **kwargs):
        kwargs.setdefault("verify", False)
        _orig_curl_init(self, *args, **kwargs)
    _curl.Session.__init__ = _patched_curl_init
except Exception:
    pass
