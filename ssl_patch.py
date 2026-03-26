# ─────────────────────────────────────────────
# ssl_patch.py
#
# Purpose : Global SSL bypass for restricted/corporate networks
# Import  : Must be imported FIRST in api.py and data_loader.py
# ─────────────────────────────────────────────

import os
import ssl
import urllib3

# 1. Python ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 2. urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 3. HuggingFace hub (used by ChromaDB DefaultEmbeddingFunction)
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ["HUGGINGFACE_HUB_VERBOSITY"]        = "warning"

# 4. Monkey-patch requests.Session — covers ALL libraries using requests
import requests
_orig_request = requests.Session.request
def _patched_request(self, method, url, **kwargs):
    kwargs.setdefault("verify", False)
    return _orig_request(self, method, url, **kwargs)
requests.Session.request = _patched_request

# 5. curl_cffi (used by yfinance)
try:
    import curl_cffi.requests as _curl
    _orig_init = _curl.Session.__init__
    def _patched_init(self, *args, **kwargs):
        kwargs.setdefault("verify", False)
        _orig_init(self, *args, **kwargs)
    _curl.Session.__init__ = _patched_init
except Exception:
    pass
