# Sign Recognizer Architecture

## Goal

This project is moving from a frame-based gesture demo toward a real sign-language recognizer.
The new direction is:

1. Capture frame-level body and hand landmarks.
2. Build sequence-level features over recent frames.
3. Run recognition on the sequence instead of a single frame.
4. Connect the recognized sign to KCISA metadata and subtitle output.

## Current Runtime Flow

`main.py`
-> `RealTimeSignRecognizer`
-> `hand_tracking/tracker.py`
-> `BodyFrameFeatures`
-> `SequenceBuffer`
-> `SequenceFeatures`
-> `predict_sign(...)`
-> `PredictionStabilizer`
-> `SignLanguageTranslator`
-> subtitle / translation UI

## Main Components

### `BodyFrameFeatures`
- Single-frame features
- Finger states
- Wrist position
- Shoulder / elbow relationship
- Head proximity

### `SequenceFeatures`
- Recent-frame motion summary
- X/Y movement range
- Direction changes
- Open-palm ratio
- Near-head ratio
- Above-shoulder ratio
- Mean elbow angle

### `RealTimeSignRecognizer`
- Central real-time recognition service
- Owns sequence buffering
- Owns stabilizer
- Optionally logs sequence data for training

### `SequenceDatasetLogger`
- Saves frame and sequence features to JSONL
- Intended for building a labeled training dataset later

## Why This Is Better Than Rule-Only Recognition

The old approach mostly asked:
- "What does the hand look like right now?"

The new approach also asks:
- "How has the hand and arm moved over the last several frames?"

That is the minimum structure needed for real sign recognition.

## Next Recommended Steps

1. Add labeled recording mode for target signs.
2. Train a sequence classifier on saved JSONL data.
3. Replace the rule predictor with a learned model interface.
4. Add face / head orientation features for non-manual signals.
