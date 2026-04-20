import argparse
import os
from pathlib import Path


ENV_PATH = Path(".env")
KCISA_CACHE_PATH = Path("data/kcisa_sign_cache.json")
KCISA_API_URL = (
    "https://api.kcisa.kr/openapi/service/rest/meta13/getCTE01701"
)


def load_env_file(env_path: Path = ENV_PATH) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def build_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hand tracker and KCISA sign language data client",
    )
    parser.add_argument(
        "--fetch-sign-data",
        action="store_true",
        help="KCISA 일상생활수어 공공데이터를 조회합니다.",
    )
    parser.add_argument(
        "--num-of-rows",
        type=int,
        default=10,
        help="조회 또는 캐시 생성 시 페이지당 레코드 수입니다.",
    )
    parser.add_argument(
        "--page-no",
        type=int,
        default=1,
        help="조회할 페이지 번호입니다.",
    )
    parser.add_argument(
        "--sequence-log-path",
        type=str,
        default="",
        help="학습용 시퀀스 특징을 JSONL로 저장할 경로입니다.",
    )
    parser.add_argument(
        "--build-kcisa-cache",
        action="store_true",
        help="KCISA API 여러 페이지를 수집해 로컬 캐시를 생성합니다.",
    )
    parser.add_argument(
        "--cache-path",
        type=str,
        default=str(KCISA_CACHE_PATH),
        help="KCISA 로컬 캐시 파일 경로입니다.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="캐시 생성 시 수집할 최대 페이지 수입니다.",
    )
    return parser.parse_args()
