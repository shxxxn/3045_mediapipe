# gesture.py

import numpy as np
import math

class GestureRecognizer:
    """
    根據 landmarks 與 handedness 判斷手勢名稱。
    landmarks: 21 個點，格式可為：
        - list of mediapipe.framework.formats.landmark_pb2.NormalizedLandmark (有 .x, .y, .z)
        - 或 np.array shape (21,3)，用 normalized 值
    handedness: 字串 "Left" 或 "Right"
    """

    def __init__(self, ok_distance_threshold=0.05):
        # OK 手勢中，拇指與食指指尖距離(normalized)小於此閾值即視為 OK
        self.ok_dist_thresh = ok_distance_threshold

    def _landmarks_to_array(self, landmarks):
        """
        若 landmarks 為 mediapipe NormalizedLandmarkList，轉為 (21,3) np.array。
        """
        if isinstance(landmarks, np.ndarray):
            return landmarks  # 假設已是 (21,3)
        # 否則假設是 list of landmark 物件
        arr = np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32)
        return arr

    def _finger_is_extended(self, lm_arr, handedness_label):
        """
        判斷每隻手指是否伸直，回傳布林列表 [thumb, index, middle, ring, pinky]。
        lm_arr: np.array shape (21,3)，normalized 座標
        handedness_label: "Left" 或 "Right"，影響拇指判斷
        """
        # 指尖與相鄰關節的 index:
        # Thumb: TIP=4, IP=3, MCP=2, CMC=1; Handedness 影響方向判斷
        # Index: TIP=8, PIP=6
        # Middle: TIP=12, PIP=10
        # Ring: TIP=16, PIP=14
        # Pinky: TIP=20, PIP=18

        extended = [False]*5

        # Index finger, Middle, Ring, Pinky: 以 y 座標判斷（normalized，0 at top, 1 at bottom）
        # 若 tip.y < pip.y 表示手指向上伸展（畫面上方），視為伸直
        # 需注意：若手勢非垂直向上，規則僅適用簡單示意。更通用情況可考慮角度計算。
        # Index
        if lm_arr[8][1] < lm_arr[6][1]:
            extended[1] = True
        # Middle
        if lm_arr[12][1] < lm_arr[10][1]:
            extended[2] = True
        # Ring
        if lm_arr[16][1] < lm_arr[14][1]:
            extended[3] = True
        # Pinky
        if lm_arr[20][1] < lm_arr[18][1]:
            extended[4] = True

        # Thumb: 以 x 座標判斷拇指是否伸出
        # 參考方式：若右手 (handedness_label=="Right")，且 tip.x > ip.x，表示向畫面右側伸；左手則相反
        # 但因我們在 main.py 通常會對 frame 做水平翻轉 (mirror)，可能要調整；此處以未翻轉情況下示意：
        # 若在 main 裡有做 frame = cv2.flip(frame,1)，normalized 座標 x 可能也鏡像，handedness_label 來自 MediaPipe 是就相對鏡像後畫面手左右嗎？MediaPipe 的 handedness 是以相機視角而言，對翻轉後畫面需自行測試或反向。
        # 這裡假設未翻轉或已知 handedness 與座標關係：
        if handedness_label == "Right":
            if lm_arr[4][0] > lm_arr[3][0]:
                extended[0] = True
        else:  # Left
            if lm_arr[4][0] < lm_arr[3][0]:
                extended[0] = True

        return extended  # [thumb, index, middle, ring, pinky]

    def recognize(self, landmarks, handedness_label):
        """
        主辨識函式，回傳手勢名稱字串或 None。可自行擴充更多手勢。
        """
        lm_arr = self._landmarks_to_array(landmarks)
        fingers = self._finger_is_extended(lm_arr, handedness_label)
        # fingers 為 [thumb, index, middle, ring, pinky] 各布林

        # 簡單手勢判斷：
        # 1. 握拳 (fist): all False
        if not any(fingers):
            return "Fist"
        # 2. 張開手掌 (Open): all True
        if all(fingers):
            return "Open"
        # 3. Peace / V sign: index & middle True, others False
        if fingers[1] and fingers[2] and not fingers[0] and not fingers[3] and not fingers[4]:
            return "Peace"
        # 4. Thumbs Up: thumb True, 其他 False
        if fingers[0] and not any(fingers[1:]):
            return "Thumbs Up"
        # 5. OK sign: 拇指與食指指尖靠近，其他三指伸直或彎曲皆可依需求；此處要求 middle, ring, pinky 伸直
        #    計算 normalized 座標距離
        #    TIP thumb index: 4, 8
        if fingers[2] and fingers[3] and fingers[4]:
            dist = np.linalg.norm(lm_arr[4][:2] - lm_arr[8][:2])  # 僅 x,y 平面距離
            if dist < self.ok_dist_thresh:
                return "OK"
        # 6. 其他手勢：可再擴充...

        # 若以上皆不符合，可回傳 None 或 "Unknown"
        return None