# ─────────────────────────────────────────────
# ssl_patch.py
#
# Purpose : Global SSL bypass for restricted/corporate networks
# Import  : Must be imported FIRST in api.py and data_loader.py
# ─────────────────────────────────────────────

import os
import ssl
import urllib3

# Python ssl
ssl._create_default_https_context = ssl._create_unverified_context

# requests / urllib3
os.environ["CURL_CA_BUNDLE"]     = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
os.environ["SSL_CERT_FILE"]      = ""
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# curl_cffi (used by yfinance)
try:
    import curl_cffi.requests as _curl
    _orig = _curl.Session.__init__
    def _patched(self, *args, **kwargs):
        kwargs.setdefault("verify", False)
        _orig(self, *args, **kwargs)
    _curl.Session.__init__ = _patched
except Exception:
    pass
