from kcisa.models import KcisaBody, KcisaHeader, KcisaItem, KcisaResponse


def _to_string(value) -> str:
    if value is None:
        return ""
    return str(value)


def parse_kcisa_response(payload: dict) -> KcisaResponse:
    header_data = payload.get("header", {})
    body_data = payload.get("body", {})
    items_data = body_data.get("items", {}).get("item", [])

    if isinstance(items_data, dict):
        items_data = [items_data]

    items = [
        KcisaItem(
            title=_to_string(item.get("title")),
            alternativeTitle=_to_string(item.get("alternativeTitle")),
            creator=_to_string(item.get("creator")),
            regDate=_to_string(item.get("regDate")),
            collectionDb=_to_string(item.get("collectionDb")),
            subjectCategory=_to_string(item.get("subjectCategory")),
            subjectKeyword=_to_string(item.get("subjectKeyword")),
            extent=_to_string(item.get("extent")),
            description=_to_string(item.get("description")),
            spatialCoverage=_to_string(item.get("spatialCoverage")),
            temporal=_to_string(item.get("temporal")),
            person=_to_string(item.get("person")),
            language=_to_string(item.get("language")),
            sourceTitle=_to_string(item.get("sourceTitle")),
            referenceIdentifier=_to_string(item.get("referenceIdentifier")),
            rights=_to_string(item.get("rights")),
            copyrightOthers=_to_string(item.get("copyrightOthers")),
            url=_to_string(item.get("url")),
            contributor=_to_string(item.get("contributor")),
            subDescription=_to_string(item.get("subDescription")),
            signDescription=_to_string(item.get("signDescription")),
            signImages=_to_string(item.get("signImages")),
            categoryType=_to_string(item.get("categoryType")),
        )
        for item in items_data
    ]

    return KcisaResponse(
        header=KcisaHeader(
            resultCode=_to_string(header_data.get("resultCode")),
            resultMsg=_to_string(header_data.get("resultMsg")),
        ),
        body=KcisaBody(
            items=items,
            numOfRows=_to_string(body_data.get("numOfRows", "0")),
            pageNo=_to_string(body_data.get("pageNo", "0")),
            totalCount=_to_string(body_data.get("totalCount", "0")),
        ),
    )
