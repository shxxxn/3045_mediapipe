# main.py

import cv2
import mediapipe as mp
from gesture import GestureRecognizer
from utils import LandmarkSmoother, normalized_to_pixel_coordinates

def main():
    # 初始化 Mediapipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # GestureRecognizer 實例
    gesture_recognizer = GestureRecognizer(ok_distance_threshold=0.05)

    # 若要針對每隻手做平滑，可用 dict: key 為手序號(自行定義)，value 為 LandmarkSmoother
    # 由於 MediaPipe Python API 並不直接回傳手的持續 ID，我們可簡單對應：每 frame 假設多手時依序 0,1；簡單平滑示範：
    smoothers = [LandmarkSmoother(maxlen=5) for _ in range(2)]  # 最多 2 隻手

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("無法開啟攝影機，請確認權限與裝置")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("擷取失敗，跳出")
            break

        # 翻轉鏡像：方便鏡像視覺，若用於手勢控制 UI，使用者習慣鏡像較直覺
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False
        results = hands.process(img_rgb)
        img_rgb.flags.writeable = True
        frame = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

        # 若有偵測到手且同時有 handedness 資訊
        if results.multi_hand_landmarks and results.multi_handedness:
            for idx, (hand_landmarks, hand_handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
                # hand_handedness.classification[0].label 為 "Left" 或 "Right"
                label = hand_handedness.classification[0].label

                # 先將 landmarks 用 smoother 平滑
                # 轉 array
                lm_arr = None
                try:
                    # 先轉 np.array，再更新至 smoother，再取平均
                    import numpy as np
                    arr = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark], dtype=np.float32)
                    smoothers[idx].update(hand_landmarks.landmark)
                    avg = smoothers[idx].average_landmarks()
                    if avg is not None:
                        lm_arr = avg
                    else:
                        lm_arr = arr
                except Exception:
                    # 若平滑失敗，直接轉 list
                    lm_arr = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark], dtype=np.float32)

                # 呼叫手勢辨識
                gesture_name = gesture_recognizer.recognize(lm_arr, label)

                # 繪製骨架關鍵點
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255,0,0), thickness=2)
                )

                # 若有辨識到手勢，畫到畫面上
                if gesture_name:
                    # 取得手腕 landmark 作為文字位置參考
                    wrist_lm = hand_landmarks.landmark[0]
                    coord = normalized_to_pixel_coordinates(wrist_lm.x, wrist_lm.y, w, h)
                    if coord:
                        cv2.putText(frame, gesture_name, (coord[0], coord[1]-20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)

        # 顯示畫面
        cv2.imshow('Hand Tracking with Gesture Recognition', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()