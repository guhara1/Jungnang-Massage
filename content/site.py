# 사이트 공통 설정
# 배포 도메인 확정 후 BASE_URL 을 실제 도메인으로 변경하세요.
BASE_URL = "https://jungnang-massage.netlify.app"

BRAND = "간다GO"
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

# 네이버 서치어드바이저 사이트 소유확인 메타 코드. 모든 페이지 <head>에 삽입된다.
NAVER_VERIFY = "61a9c1e61232403447b3cf84ff0257fe7ce97b47"

# IndexNow 키 — 빙·네이버·얀덱스 등 IndexNow 참여 검색엔진에 즉시 색인 통보용.
# 빌드 시 루트에 "{INDEXNOW_KEY}.txt" 키 파일이 생성된다. 키를 바꾸면 키 파일도 함께 바뀐다.
INDEXNOW_KEY = "a7f3c9e21b6d4f08a5c2e9d71b3f6a4e"

# 구조화 데이터(Review·AggregateRating)용 평점·대표 후기.
# 메인 사업자(HealthAndBeautyBusiness) 스키마에 자동 삽입되어 검색 결과의
# 별점·후기 표시 후보가 된다.
RATING_VALUE = "4.9"
RATING_COUNT = "212"
REVIEWS = [
    {
        "author": "김O연", "rating": "5", "date": "2026-05-18",
        "body": "상봉동 오피스텔로 늦은 밤에 예약했는데 안내해준 시간에 정확히 도착했어요. "
                "압 세기도 요청한 대로 맞춰주셔서 다음 날 어깨가 한결 가벼웠습니다.",
    },
    {
        "author": "박O훈", "rating": "5", "date": "2026-04-30",
        "body": "면목동 자택으로 스웨디시 받았습니다. 예약 전화부터 친절했고 위생용품도 "
                "새것으로 꼼꼼히 준비해 오셔서 믿음이 갔어요.",
    },
    {
        "author": "이O지", "rating": "5", "date": "2026-04-11",
        "body": "운동 후 회복용으로 신내동에서 타이마사지 예약했는데 스트레칭이 시원했습니다. "
                "종아리 뭉친 게 풀려서 컨디션이 좋아졌어요.",
    },
    {
        "author": "정O아", "rating": "4", "date": "2026-03-22",
        "body": "망우역 근처 숙소로 아로마 받았어요. 향이 은은하고 좋았습니다. 도착이 조금 "
                "늦었지만 미리 연락 주셔서 기다리는 데 불편함은 없었습니다.",
    },
    {
        "author": "최O석", "rating": "5", "date": "2026-03-05",
        "body": "부모님 선물로 묵동 본가에 홈타이를 예약해 드렸는데 두 분 다 만족하셨어요. "
                "대리 예약 과정도 매끄러웠습니다.",
    },
    {
        "author": "한O림", "rating": "5", "date": "2026-02-14",
        "body": "중화동에서 커플 관리로 둘이 같이 받았습니다. 동시에 조용하게 진행돼서 "
                "분위기 좋았고 재방문 의사 있어요.",
    },
]

# 상단 메뉴 — 하위 메뉴에는 키워드를 반복하지 않고 지역명·역명만 표시한다.
NAV = [
    ("홈", "/", []),
    ("중랑 출장마사지", "/massage/", [
        ("출장마사지 안내", "/massage/#service"),
        ("홈타이 안내", "/massage/#hometai"),
        ("전지역 방문 안내", "/massage/#coverage"),
        ("지하철역 인근 안내", "/massage/#stations"),
        ("예약 가능 시간", "/massage/#hours"),
        ("코스 선택 안내", "/massage/#course"),
        ("이용 전 확인사항", "/massage/#check"),
        ("위생·안전 안내", "/massage/#safety"),
        ("자주 묻는 질문", "/massage/#faq"),
    ]),
    ("지역별 안내", "/jungnang/", [
        ("중랑구 전체", "/jungnang/"),
        ("면목동", "/jungnang/myeonmok-chuljangmassage/"),
        ("상봉동", "/jungnang/sangbong-chuljangmassage/"),
        ("중화동", "/jungnang/junghwa-chuljangmassage/"),
        ("묵동", "/jungnang/mukdong-chuljangmassage/"),
        ("망우동", "/jungnang/mangwoo-chuljangmassage/"),
        ("신내동", "/jungnang/sinnae-chuljangmassage/"),
    ]),
    ("지하철역별 안내", "/jungnang/stations/", [
        ("역 전체", "/jungnang/stations/"),
        ("상봉역", "/jungnang/sangbong-station-chuljangmassage/"),
        ("망우역", "/jungnang/mangwoo-station-chuljangmassage/"),
        ("중랑역", "/jungnang/jungnang-station-chuljangmassage/"),
        ("중화역", "/jungnang/junghwa-station-chuljangmassage/"),
        ("먹골역", "/jungnang/meokgol-station-chuljangmassage/"),
        ("면목역", "/jungnang/myeonmok-station-chuljangmassage/"),
        ("사가정역", "/jungnang/sagajeong-station-chuljangmassage/"),
        ("용마산역", "/jungnang/yongmasan-station-chuljangmassage/"),
        ("봉화산역", "/jungnang/bonghwasan-station-chuljangmassage/"),
        ("신내역", "/jungnang/sinnae-station-chuljangmassage/"),
        ("양원역", "/jungnang/yangwon-station-chuljangmassage/"),
    ]),
    ("테마별 안내", "/themes/", [
        ("전체 테마", "/themes/"),
        ("스웨디시", "/themes/swedish/"),
        ("로미로미", "/themes/lomilomi/"),
        ("타이마사지", "/themes/thai/"),
        ("중국마사지", "/themes/chinese/"),
        ("아로마테라피", "/themes/aroma/"),
        ("홈케어", "/themes/homecare/"),
        ("호텔식마사지", "/themes/hotel-style/"),
        ("발마사지", "/themes/foot/"),
        ("스포츠·경락", "/themes/sports/"),
        ("스킨케어", "/themes/skincare/"),
        ("왁싱", "/themes/waxing/"),
        ("커플 관리", "/themes/couple/"),
        ("24시간", "/themes/24hours/"),
        ("수면 가능", "/themes/overnight/"),
    ]),
    ("코스안내", "/courses/", [
        ("전체 코스", "/courses/"),
        ("피로 회복 관리", "/courses/#recovery"),
        ("아로마 관리", "/courses/#aroma"),
        ("스포츠 관리", "/courses/#sports"),
        ("홈타이 코스", "/courses/#hometai"),
        ("커플·가족 방문 관리", "/courses/#couple"),
        ("기업·단체 방문 관리", "/courses/#group"),
        ("가격 안내", "/courses/#price"),
        ("코스 선택 가이드", "/courses/#guide"),
    ]),
    ("예약안내", "/reservation/", [
        ("예약 방법", "/reservation/#how"),
        ("예약 가능 시간", "/reservation/#hours"),
        ("방문 가능 장소", "/reservation/#place"),
        ("결제 안내", "/reservation/#payment"),
        ("변경·취소 안내", "/reservation/#change"),
        ("예약 전 체크사항", "/reservation/#check"),
    ]),
    ("이용가이드", "/guide/", [
        ("처음 이용하시는 분", "/guide/#first"),
        ("방문 전 준비사항", "/guide/#prepare"),
        ("위생 및 안전 기준", "/guide/#hygiene"),
        ("관리 후 주의사항", "/guide/#after"),
        ("금지행위 안내", "/guide/#prohibited"),
        ("이용 FAQ", "/guide/#faq"),
    ]),
    ("매거진", "/magazine/", [
        ("전체 글", "/magazine/"),
        ("마사지 비교 가이드", "/magazine/swedish-vs-thai/"),
        ("처음 이용 가이드", "/magazine/first-time-guide/"),
        ("수면과 마사지", "/magazine/sleep-and-massage/"),
        ("운동 후 회복", "/magazine/post-workout-timing/"),
        ("어깨·목 결림 관리", "/magazine/neck-shoulder-care/"),
        ("부모님 선물 가이드", "/magazine/parents-gift/"),
    ]),
    ("후기", "/reviews/", [
        ("전체 후기", "/reviews/"),
        ("지역별 후기", "/reviews/#area"),
        ("역세권 후기", "/reviews/#station"),
        ("후기 작성 안내", "/reviews/#write"),
    ]),
    ("고객센터", "/support/", [
        ("공지사항", "/support/#notice"),
        ("자주 묻는 질문", "/support/#faq"),
        ("1:1 문의", "/support/#contact"),
        ("제휴·기업 문의", "/support/#biz"),
        ("개인정보처리방침", "/support/privacy/"),
        ("이용약관", "/support/terms/"),
    ]),
]
