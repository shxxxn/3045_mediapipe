Hand Tracking 與 Gesture Recognition 專案

專案簡介

本專案使用 Google MediaPipe Hands 進行手部 21 點骨架追蹤，並以簡單規則法實作手勢辨識 (Gesture Recognition)。程式採模組化設計，易於擴充其他手勢或整合至更大系統。

此專案適合想快速建立手部偵測與手勢辨識功能，並在 VSCode 等開發環境執行的使用者。可用於互動應用、控制介面、學術專題展示等場景。

功能特色
	•	即時手部 21 點骨架追蹤，顯示關鍵點與連線
	•	支援多隻手（預設最多 2 隻）偵測
	•	簡單規則法手勢辨識，包含：
	•	Fist (握拳)
	•	Open (張開手掌)
	•	Peace (勝利 V 字)
	•	Thumbs Up (豎大拇指)
	•	OK (拇指與食指指尖接觸)
	•	可設定平滑 (smoothing) 參數，減少抖動
	•	可顯示辨識結果文字在畫面上，方便測試與展示
	•	模組化程式結構，易於擴充更多手勢或整合 GUI/後端服務

專案結構

your_project_folder/
├── main.py           # 入口程式：攝影機串流、MediaPipe 偵測、呼叫 GestureRecognizer、顯示結果
├── gesture.py        # GestureRecognizer 類別：實作手勢辨識邏輯
├── utils.py          # 共用輔助函式：平滑、座標轉換、距離計算等工具
├── requirements.txt  # 所需套件版本
└── README.md         # 使用說明

安裝與環境設定
	1.	建議使用虛擬環境 (conda 或 venv)：
	•	conda:

conda create -n mediapipe_env python=3.10
conda activate mediapipe_env


	•	venv:

python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux


	2.	安裝所需套件：

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt


	3.	在 VSCode 中，透過「Python: Select Interpreter」選擇上述虛擬環境的 Python。
	4.	在 macOS 若遇相機權限問題，請於「系統偏好設定」→「隱私權與安全性」→「相機」允許 Terminal/VSCode 存取。

requirements.txt 範例

opencv-python>=4.5.0
mediapipe>=0.9.0
numpy>=1.19.0

可根據需求調整版本要求。

使用方法
	1.	開啟 VSCode，開啟本專案資料夾。確定已選擇正確虛擬環境。
	2.	透過 VSCode Terminal 啟動虛擬環境並執行：

python main.py


	3.	若攝影機正常開啟，將看到即時畫面，畫面中會疊加手部骨架與辨識出的手勢文字。按下 q 鍵可結束程式。
	4.	若要測試影片檔，可在 main.py 中將 cv2.VideoCapture(0) 改為 cv2.VideoCapture('path/to/video.mp4')，並執行相同流程。

參數與設定
	•	MediaPipe Hands 初始化（位於 main.py）：
	•	static_image_mode: False（串流模式）、True（每張影像重新偵測，較慢）。
	•	max_num_hands: 偵測手部數量上限，預設 2。
	•	min_detection_confidence: 偵測置信度門檻，範圍 0~1。
	•	min_tracking_confidence: 追蹤置信度門檻，僅在串流模式下生效。
	•	GestureRecognizer（位於 gesture.py）：
	•	OK 手勢距離閾值 (ok_distance_threshold)，可依畫面比例及測試結果微調。
	•	拇指伸展判斷邏輯，需留意是否有對畫面做水平翻轉 (cv2.flip)，可能影響座標關係，可在實測時調整。
	•	平滑 (Smoothing)（位於 utils.py）：
	•	LandmarkSmoother 的 maxlen，決定緩衝多少幀做平均，可減少抖動，但反應速度可能稍延遲。

範例截圖或輸出說明
	•	當偵測到手並辨識出手勢時，手腕位置上方會顯示辨識結果文字，例如 “Open” 或 “Fist”。
	•	骨架關鍵點以綠色點與連線顯示，連線顏色與圈大小可在 main.py 中調整。
	•	可自行截圖或錄影展示偵測與辨識效果，作為報告或演示素材。

故障排除
	•	找不到 OpenCV/MediaPipe：確認 VSCode 下方所選 Python Interpreter 與安裝套件環境一致，並在該環境執行 pip show opencv-python mediapipe 檢查。
	•	相機無法開啟：確認系統已允許 Terminal/VSCode 存取相機；攝影機索引若非 0，可嘗試其他索引。
	•	畫面不顯示或閃退：避免在 Notebook/Interactive Window 執行 OpenCV 顯示視窗，請直接執行 Python 檔於終端。
	•	偵測不穩或誤判：測試不同光線、手勢方向；可調高 min_detection_confidence、平滑參數；檢查拇指判斷邏輯在翻轉畫面後的效果，依情況微調。
	•	效能較慢：降低 max_num_hands、提高置信度門檻；如需更高效能，考慮 GPU、或只在必要時偵測。

開發與擴充
	•	新增手勢：在 gesture.py 裡編寫更多規則或載入訓練模型（如 SVM、輕量神經網路）進行分類。
	•	動態手勢：若需偵測動態序列，可蒐集多幀骨架序列，訓練 RNN/LSTM 或時間序列分類器。
	•	GUI 整合：使用 Tkinter、PyQt 等框架，將攝影機畫面嵌入自訂介面，並加上操作按鈕、參數滑動條、結果顯示區等。
	•	後端服務：在伺服器端處理上傳影像/影片，回傳骨架座標或辨識結果；或透過 WebSocket/HTTP API 傳遞結果給前端。
	•	資料分析：將辨識結果及骨架座標記錄成 CSV/JSON，做手勢使用頻率分析、行為軌跡可視化等。
	•	多手或多人場景：針對多隻手或多人場景設計對應追蹤機制，如依距離或上一框對應，處理遮擋情況。
	•	跨平台或硬體裝置：將 MediaPipe 整合到移動裝置、嵌入式系統，或搭配深度相機取得更精確深度資訊。

版權與授權

本範例參考 Google MediaPipe Hands API，請遵守相關授權條款；本專案程式碼以 MIT License (或依需求自行調整) 授權。

⸻

如有任何問題或建議，歡迎提出 Issue 或聯絡開發者，祝使用順利，專題成果豐碩！