#!/usr/bin/env python3
"""IndexNow 즉시 색인 통보 — 빙·네이버·얀덱스 등 IndexNow 참여 검색엔진.

사이트의 URL을 IndexNow 프로토콜로 제출한다. 한 곳(api.indexnow.org)에 보내면
참여 검색엔진(Bing, Naver, Yandex, Seznam)에 함께 전달된다. 구글은 IndexNow
미참여이므로 scripts/google_indexing.py 또는 서치콘솔을 사용한다.

사용법:
  # 로컬 sitemap.xml의 모든 URL 제출 (배포 후 실행)
  python3 scripts/indexnow_submit.py

  # 특정 URL만 제출 (글 새로 올렸을 때)
  python3 scripts/indexnow_submit.py https://jungnang-massage.netlify.app/magazine/new-post/

표준 라이브러리만 사용한다. 의존성 없음.
"""
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from content.site import BASE_URL, INDEXNOW_KEY  # noqa: E402

SITE = BASE_URL.rstrip("/")
HOST = re.sub(r"^https?://", "", SITE)
ENDPOINT = "https://api.indexnow.org/indexnow"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def urls_from_sitemap() -> list:
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        sys.exit("sitemap.xml 이 없습니다. 먼저 python3 build.py 를 실행하세요.")
    xml = open(path, encoding="utf-8").read()
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def submit(urls: list) -> None:
    if not urls:
        sys.exit("제출할 URL이 없습니다.")
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow 응답: {resp.status} {resp.reason}")
            print(f"제출 URL {len(urls)}건 (host={HOST})")
            # 200/202 = 정상 접수
    except urllib.error.HTTPError as e:
        print(f"IndexNow 오류: {e.code} {e.reason}")
        print(e.read().decode("utf-8", "ignore"))
        sys.exit(1)


if __name__ == "__main__":
    urls = sys.argv[1:] or urls_from_sitemap()
    print(f"IndexNow 제출 대상 {len(urls)}건")
    submit(urls)
