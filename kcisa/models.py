from dataclasses import asdict, dataclass


@dataclass
class KcisaItem:
    title: str = ""
    alternativeTitle: str = ""
    creator: str = ""
    regDate: str = ""
    collectionDb: str = ""
    subjectCategory: str = ""
    subjectKeyword: str = ""
    extent: str = ""
    description: str = ""
    spatialCoverage: str = ""
    temporal: str = ""
    person: str = ""
    language: str = ""
    sourceTitle: str = ""
    referenceIdentifier: str = ""
    rights: str = ""
    copyrightOthers: str = ""
    url: str = ""
    contributor: str = ""
    subDescription: str = ""
    signDescription: str = ""
    signImages: str = ""
    categoryType: str = ""


@dataclass
class KcisaHeader:
    resultCode: str = ""
    resultMsg: str = ""


@dataclass
class KcisaBody:
    items: list[KcisaItem]
    numOfRows: str = "0"
    pageNo: str = "0"
    totalCount: str = "0"


@dataclass
class KcisaResponse:
    header: KcisaHeader
    body: KcisaBody

    def to_dict(self) -> dict:
        return asdict(self)
