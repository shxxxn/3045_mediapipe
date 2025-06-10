# utils.py

import numpy as np
from collections import deque

class LandmarkSmoother:
    """
    簡單的移動平均平滑器，用於平滑 landmarks 座標。
    使用方式：對同一隻手、多幀連續呼叫 update()，再用 average_landmarks() 取得平均結果。
    """
    def __init__(self, maxlen=5):
        # 每個 frame 的 landmarks 為 list of (x,y,z) arrays，這裡用 deque 存最近幾幀
        self.buffer = deque(maxlen=maxlen)

    def update(self, landmarks):
        """
        landmarks: list of landmark，或 list of np.array([x,y,z])，長度應為 21
        """
        # 將 landmarks 轉為 np.array 便於計算：shape (21,3)
        arr = np.array([[lm.x, lm.y, lm.z] if hasattr(lm, 'x') else lm for lm in landmarks], dtype=np.float32)
        self.buffer.append(arr)

    def average_landmarks(self):
        """
        回傳平均後的 landmarks：shape (21,3) 的 np.array
        若 buffer 為空，回傳 None
        """
        if not self.buffer:
            return None
        stacked = np.stack(self.buffer, axis=0)  # shape (N,21,3)
        avg = np.mean(stacked, axis=0)  # shape (21,3)
        # 轉回 list of simple dict-like? 但 GestureRecognizer 可接受 np.array 形式
        return avg

def normalized_to_pixel_coordinates(norm_x, norm_y, image_width, image_height):
    """
    將 normalized 座標 (0~1) 轉為畫素座標 (int)。
    回傳 None 如果超出範圍
    """
    if 0 <= norm_x <= 1 and 0 <= norm_y <= 1:
        x_px = int(norm_x * image_width)
        y_px = int(norm_y * image_height)
        return x_px, y_px
    return None

def calc_euclidean_distance(a, b):
    """
    計算兩點距離，a, b 為 np.array 或可 index 為 [x,y,z]。
    """
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a - b)