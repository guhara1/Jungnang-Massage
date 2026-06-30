# 색인(인덱싱) 운영 가이드

빌드(`python3 build.py`)는 색인에 필요한 파일을 모두 자동 생성합니다.

| 파일 | 용도 |
|------|------|
| `sitemap.xml` | 색인 페이지 목록 + `lastmod`. 구글·네이버·빙 서치 콘솔에 제출 |
| `rss.xml` | 매거진 RSS 2.0 피드. 모든 페이지 `<head>`에 `alternate` 링크 포함 |
| `robots.txt` | 전봇 허용 + 사이트맵 위치 (구글봇·네이버 Yeti·빙봇 공통) |
| `{INDEXNOW_KEY}.txt` | IndexNow 키 파일 (루트). 키는 `content/site.py`의 `INDEXNOW_KEY` |

## 1. 최초 1회 (검색엔진 등록)

1. **네이버 서치어드바이저** (searchadvisor.naver.com)
   - 사이트 등록 → 소유확인(메인페이지 메타태그 이미 삽입됨)
   - 요청 → 사이트맵 제출: `https://jungnang-massage.netlify.app/sitemap.xml`
   - 요청 → RSS 제출: `https://jungnang-massage.netlify.app/rss.xml`
2. **구글 서치콘솔** (search.google.com/search-console)
   - 속성 추가 → 소유확인 → Sitemaps에 `sitemap.xml` 제출
3. **빙 웹마스터** (bing.com/webmasters) — 선택
   - 사이트 추가 → 사이트맵 제출 (구글 서치콘솔에서 가져오기 가능)
   - IndexNow는 빙이 주관하므로 별도 키 등록 없이 바로 동작

## 2. 즉시 색인 통보 (글 올릴 때마다)

### IndexNow — 빙·네이버·얀덱스 (구글 미참여)
```bash
python3 build.py                       # sitemap·키파일 갱신
python3 scripts/indexnow_submit.py     # sitemap.xml 전체 통보
# 또는 새 글만:
python3 scripts/indexnow_submit.py https://jungnang-massage.netlify.app/magazine/새글/
```
의존성 없음(표준 라이브러리). 응답 200/202 = 정상 접수.
키 파일(`/{key}.txt`)이 **배포된 뒤** 통보해야 검증됩니다. 배포 후 실행하세요.

### 구글 Indexing API
구글은 IndexNow에 참여하지 않아 별도 통보가 필요합니다.
```bash
pip install -r scripts/requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS=/경로/service-account.json
python3 scripts/google_indexing.py
```
서비스 계정을 **서치콘솔 소유자**로 추가해야 동작합니다(스크립트 상단 주석 참고).

## 3. 자동화 (GitHub Actions)

`.github/workflows/indexnow.yml` 이 `main` push 시 자동 실행됩니다.
- 빌드 → 배포 대기 → IndexNow 통보(자동)
- 구글 통보는 리포지토리 시크릿 `GOOGLE_SERVICE_ACCOUNT_JSON`(서비스 계정 JSON 전체)을
  넣으면 자동 활성화됩니다. 없으면 IndexNow만 실행.

## 참고: 사이트맵 핑(ping)은 더 이상 쓰지 않습니다

구글은 2023년 6월, 빙도 비슷한 시기에 **sitemap ping 엔드포인트
(`/ping?sitemap=`)를 폐지**했습니다. 지금은 서치콘솔 사이트맵 제출(1회) +
변경 시 IndexNow/Indexing API 통보가 표준 방식입니다. 그래서 이 리포지토리에는
죽은 ping 스크립트 대신 IndexNow·Indexing API 통보를 넣었습니다.
