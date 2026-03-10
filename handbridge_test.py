import cv2
from ultralytics import YOLO

# 1. 모델 로드 (처음 실행 시 파일 다운로드로 10~20초 소요될 수 있음)
model = YOLO('yolo26n-pose.pt')

# 2. 카메라 연결 (0번이 안 되면 1번, 2번 순서대로 시도)
cap = cv2.VideoCapture(0) 

if not cap.isOpened():
    print("0번 카메라를 찾을 수 없어 1번으로 시도합니다...")
    cap = cv2.VideoCapture(1)

print("카메라가 켜졌습니다! 화면 창을 클릭한 후 'q'를 누르면 종료됩니다.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("화면을 가져올 수 없습니다. 카메라 연결을 확인하세요.")
        break

    # 3. YOLO26 추론 (인식 결과 그리기)
    results = model(frame, stream=True)
    
    for r in results:
        annotated_frame = r.plot() # 관절 점과 선 그리기
        
        # 4. 화면 표시
        cv2.imshow("HandBridge Test", annotated_frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()