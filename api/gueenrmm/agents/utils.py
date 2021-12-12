import random
import urllib.parse
import requests

from django.conf import settings
from core.models import CodeSignToken


def get_exegen_url() -> str:
    urls: list[str] = settings.EXE_GEN_URLS
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
        except:
            continue

        if r.status_code == 200:
            return url

    return random.choice(urls)


def get_winagent_url(arch: str) -> str:

    dl_url = settings.DL_32 if arch == "32" else settings.DL_64

    try:
        t: CodeSignToken = CodeSignToken.objects.first()  # type: ignore
        if t.is_valid:
            base_url = get_exegen_url() + "/api/v1/winagents/?"
            params = {
                "version": settings.LATEST_AGENT_VER,
                "arch": arch,
                "token": t.token,
            }
            dl_url = base_url + urllib.parse.urlencode(params)
    except:
        pass

    return dl_url
