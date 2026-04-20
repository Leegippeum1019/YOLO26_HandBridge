# YOLO26 HandBridge

실시간 손·팔 랜드마크를 기반으로 수어 동작을 추적하고, KCISA 일상생활수어 공공데이터와 연결해 자막형 번역 결과를 보여주는 프로토타입 프로젝트입니다.

## Overview

이 프로젝트는 단순 손가락 카운터가 아니라, 아래 흐름을 목표로 구성되어 있습니다.

- `MediaPipe Hands + Pose`로 손과 팔 자세 추적
- 프레임 특징을 시퀀스 특징으로 누적
- 실시간 제스처/수어 예측
- KCISA API 또는 로컬 캐시와 연결해 번역 문구 출력
- 하단 자막과 상태 카드 형태의 실시간 UI 제공

현재는 규칙 기반 베이스라인과 시퀀스 구조가 함께 들어간 상태이며, 이후 학습 기반 수어 인식기로 확장할 수 있도록 설계되어 있습니다.

## Features

- 양손 동시 인식
- 손가락 상태 추정
- 팔 위치와 손목 이동 기반 연속 동작 감지
- `안녕하세요` 같은 시퀀스성 동작 인식 실험
- KCISA 일상생활수어 데이터 조회
- KCISA 데이터 로컬 캐시 생성 및 검색
- 하단 자막형 번역 UI
- 학습용 시퀀스 로그 JSONL 저장

## Project Structure

```text
YOLO26_HandBridge/
├─ main.py
├─ config.py
├─ README.md
├─ SIGN_RECOGNIZER_ARCHITECTURE.md
├─ hand_tracking/
│  ├─ logic.py
│  ├─ rendering.py
│  └─ tracker.py
├─ kcisa/
│  ├─ cache.py
│  ├─ client.py
│  ├─ models.py
│  └─ parser.py
└─ sign_language/
   ├─ dataset.py
   ├─ models.py
   ├─ phrasebook.py
   ├─ predictor.py
   ├─ recognizer.py
   ├─ sequence.py
   ├─ stabilizer.py
   └─ translator.py
```

## Quick Start

### 1. 환경 변수 설정

`.env` 파일을 만들고 KCISA 서비스키를 넣습니다.

```env
KCISA_SERVICE_KEY=your_service_key_here
```

예시는 [.env.example](/abs/path/c:/Users/LG/Desktop/YOLO26_HandBridge/.env.example)에 있습니다.

### 2. 실행

```bash
venv\Scripts\python.exe main.py
```

실행 후 웹캠 화면에서:

- 상단: 라이브 뷰 타이틀
- 좌측/우측 카드: 손별 인식 상태
- 하단 배너: 자막형 번역 문구

## CLI Examples

### KCISA 단일 페이지 조회

```bash
venv\Scripts\python.exe main.py --fetch-sign-data --num-of-rows 10 --page-no 1
```

### KCISA 캐시 생성

```bash
venv\Scripts\python.exe main.py --build-kcisa-cache --num-of-rows 100 --max-pages 10
```

기본 캐시 경로:

```text
data/kcisa_sign_cache.json
```

### 학습용 시퀀스 로그 저장

```bash
venv\Scripts\python.exe main.py --sequence-log-path data\sequence_log.jsonl
```

## Runtime Pipeline

```text
Camera Frame
-> MediaPipe Hands / Pose
-> BodyFrameFeatures
-> SequenceBuffer
-> SequenceFeatures
-> RealTimeSignRecognizer
-> PredictionStabilizer
-> SignLanguageTranslator
-> Subtitle + UI Overlay
```

## Data Sources

- KCISA 일상생활수어 공공데이터
- 문화공공데이터포털

참고 링크:

https://www.culture.go.kr/data/openapi/openapiView.do?id=367&keyword=%EC%9D%BC%EC%83%81%EC%83%9D%ED%99%9C%EC%88%98%EC%96%B4&searchField=all&gubun=A#/default/%EC%9A%94%EC%B2%AD%EB%A9%94%EC%8B%9C%EC%A7%80_Get

## Current Status

이 프로젝트는 아직 완성형 수어 번역기가 아니라, 아래를 갖춘 연구/프로토타입 단계입니다.

- 규칙 기반 실시간 인식 베이스라인
- 시퀀스 인식 구조
- 캐시 기반 공공데이터 연결
- 학습 데이터 수집 기반

즉, “손 모양 데모”를 넘어서 “실제 수어 인식기”로 발전시킬 수 있는 골격까지는 갖춘 상태입니다.

## Next Step

- 라벨링 가능한 데이터 수집 모드 추가
- 학습 기반 시퀀스 분류기 도입
- 얼굴/표정 기반 비수지 신호 추가
- 생활 수어 표현 확장

프로젝트 설계 메모는 [SIGN_RECOGNIZER_ARCHITECTURE.md](/abs/path/c:/Users/LG/Desktop/YOLO26_HandBridge/SIGN_RECOGNIZER_ARCHITECTURE.md)에서 확인할 수 있습니다.
