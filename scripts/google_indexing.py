#!/usr/bin/env python3
"""구글 Indexing API 색인 통보.

구글은 IndexNow에 참여하지 않으므로 Indexing API로 직접 통보한다.
서비스 계정(JSON 키)이 필요하며, 해당 서비스 계정을 구글 서치콘솔의
사이트 소유자(Owner)로 추가해야 한다.

준비:
  1) Google Cloud Console → 프로젝트 생성 → "Indexing API" 사용 설정
  2) 서비스 계정 생성 → JSON 키 다운로드
  3) 서치콘솔(https://search.google.com/search-console) → 설정 → 사용자 및 권한
     → 서비스 계정 이메일을 "소유자"로 추가
  4) pip install -r scripts/requirements.txt

사용법:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/service-account.json
  # sitemap.xml 전체 통보
  python3 scripts/google_indexing.py
  # 특정 URL만
  python3 scripts/google_indexing.py https://jungnang-massage.pages.dev/magazine/new-post/

주의: Indexing API는 공식적으로 JobPosting/BroadcastEvent 대상이지만, 일반
페이지의 URL_UPMDATED 통보에도 널리 쓰인다. 일일 쿼터(기본 200건)가 있다.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from content.site import BASE_URL  # noqa: E402

SITE = BASE_URL.rstrip("/")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def urls_from_sitemap() -> list:
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        sys.exit("sitemap.xml 이 없습니다. 먼저 python3 build.py 를 실행하세요.")
    return re.findall(r"<loc>([^<]+)</loc>", open(path, encoding="utf-8").read())


def main() -> None:
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("의존성 필요: pip install -r scripts/requirements.txt")

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS 환경변수에 서비스 계정 JSON 경로를 설정하세요.")

    creds = service_account.Credentials.from_service_account_file(
        cred_path, scopes=SCOPES)
    session = AuthorizedSession(creds)

    urls = sys.argv[1:] or urls_from_sitemap()
    print(f"구글 Indexing API 통보 대상 {len(urls)}건")
    ok = 0
    for url in urls:
        body = {"url": url, "type": "URL_UPDATED"}
        r = session.post(ENDPOINT, json=body, timeout=30)
        if r.status_code == 200:
            ok += 1
        else:
            print(f"  실패 {r.status_code}: {url}\n    {r.text[:200]}")
    print(f"완료: {ok}/{len(urls)} 성공")


if __name__ == "__main__":
    main()
