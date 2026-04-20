import json

from config import KCISA_CACHE_PATH, build_parser
from hand_tracking.tracker import run_hand_tracker
from kcisa.cache import KcisaCacheRepository
from kcisa.client import KcisaSignLanguageClient
from sign_language.recognizer import RealTimeSignRecognizer
from sign_language.translator import SignLanguageTranslator


def main() -> None:
    args = build_parser()
    cache_repository = KcisaCacheRepository(args.cache_path or str(KCISA_CACHE_PATH))

    if args.fetch_sign_data:
        client = KcisaSignLanguageClient()
        data = client.fetch_life_sign_words(
            num_of_rows=args.num_of_rows,
            page_no=args.page_no,
        )
        print(json.dumps(data.to_dict(), ensure_ascii=False, indent=2))
        return

    if args.build_kcisa_cache:
        client = KcisaSignLanguageClient()
        items = cache_repository.build_from_api(
            client=client,
            num_of_rows=args.num_of_rows,
            max_pages=args.max_pages,
        )
        print(
            json.dumps(
                {
                    "cache_path": args.cache_path,
                    "item_count": len(items),
                    "max_pages": args.max_pages,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    client = None
    try:
        client = KcisaSignLanguageClient()
    except ValueError:
        client = None

    translator = SignLanguageTranslator(
        client,
        num_of_rows=args.num_of_rows,
        cache_repository=cache_repository,
    )
    recognizer = RealTimeSignRecognizer(
        sequence_log_path=args.sequence_log_path or None,
    )
    run_hand_tracker(
        translator=translator,
        recognizer=recognizer,
    )


if __name__ == "__main__":
    main()
