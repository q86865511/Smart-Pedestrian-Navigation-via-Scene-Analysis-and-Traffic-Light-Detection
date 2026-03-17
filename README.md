# 街景智慧導航系統

整合街景語意分割、手勢辨識與手機導航的智慧輔助駕駛專題系統。

## 參考來源

| 功能 | 原始專案 |
|------|---------|
| 街景語意分割 | [Semantic-Segmentation-Suite](https://github.com/GeorgeSeif/Semantic-Segmentation-Suite) |
| 手機導航 | [FancyNavi](https://github.com/aquawill/FancyNavi) |
| 揮手辨識 | [hand-gesture-recognition-mediapipe](https://github.com/kinivi/hand-gesture-recognition-mediapipe) |

---

## 專案結構

```
程式結果/
├── Semantic-Segmentation-街景分析訓練/   # 訓練語意分割模型
├── change_color-更改資料集顏色/           # 資料集 label 顏色轉換工具
├── FancyNavi-master-手機APP程式/          # Android 導航 App
├── Project-主程式/                        # 整合主程式
│   ├── BDD-512-640/                       # 模型 checkpoints 存放位置
│   ├── CamVid/                            # label 顏色設定 (class_dict.csv)
│   ├── output/                            # 主程式輸出結果
│   ├── Video/                             # 欲測試的影片（可選）
│   ├── Main.py                            # 主程式入口
│   ├── app.py                             # 揮手偵測程式
│   ├── marking.py                         # 在圖上標記路線資訊與分析結果
│   ├── handGestrueandMark.py              # 整合揮手與標記功能（含語音支援）
│   ├── read_txt.py                        # 讀取路線資訊
│   ├── socketforapp.java                  # 接收手機 App 資料（需 Java 編譯執行）
│   ├── client.py                          # 圖片傳送（目前未啟用）
│   └── server.py                          # 圖片接收（目前未啟用）
└── model/                                 # 歷史訓練結果參考(https://drive.google.com/drive/folders/1pj0P5hZvEmF3WJqETP0xskZqOA6WRxk1?usp=sharing)
```

---

## 一、資料集準備

訓練資料夾 `Semantic-Segmentation-街景分析訓練/` 中已包含原版 **CamVid** 資料集。

- 若要混合補充資料集，將額外照片複製至 CamVid 資料夾即可。
- 最終採用 **CamVid 與補充資料集 1:1 混合** 進行訓練。

### 更改資料集 Label 顏色

使用 `change_color-更改資料集顏色/` 工具：

```bash
python a.py {圖片所在的資料夾}

# 範例：處理 ex/ 資料夾內所有圖片
python a.py ex/
```

- 轉換後的圖片輸出至原資料夾內的 `output/` 子資料夾。
- 顏色對應設定請編輯 `setting.txt`（格式：`原始RGB 目標RGB`，每行一組）。

---

## 二、訓練模型

在 `Semantic-Segmentation-街景分析訓練/` 資料夾中執行 `train.py`。

**完整參數說明：**

```
usage: train.py [-h] [--num_epochs NUM_EPOCHS]
                [--checkpoint_step CHECKPOINT_STEP]
                [--validation_step VALIDATION_STEP] [--image IMAGE]
                [--continue_training CONTINUE_TRAINING] [--dataset DATASET]
                [--crop_height CROP_HEIGHT] [--crop_width CROP_WIDTH]
                [--batch_size BATCH_SIZE] [--num_val_images NUM_VAL_IMAGES]
                [--h_flip H_FLIP] [--v_flip V_FLIP] [--brightness BRIGHTNESS]
                [--rotation ROTATION] [--model MODEL] [--frontend FRONTEND]
```

**範例指令：**

```bash
python train.py --num_epoch 300 --frontend InceptionV4 --model FC-DenseNet103 --crop_height 512 --crop_width 512 --dataset CamVid
```

- 訓練結果（checkpoints 與三張分析圖）會存放在同一資料夾內。
- 若要在主程式中使用不同的 checkpoint，可修改 `Main.py` 的 `--checkpoint_path` 參數。

### 過去訓練結果

`model/` 資料夾存放過去選用的模型與訓練集訓練結果，可供參考比較。

---

## 三、主程式執行

進入 `Project-主程式/` 資料夾後執行：

```bash
python Main.py
```

**可用參數：**

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--inputVideo` | `no` | 指定影片路徑；不指定則使用攝影機 |
| `--image` | `output/output.jpg` | 預測用的圖片路徑 |
| `--checkpoint_path` | `BDD-512-640/Checkpoint/latest_model_FC-DenseNet103_CamVid.ckpt` | 模型 checkpoint 路徑 |
| `--crop_height` | `480` | 輸入圖片裁切高度 |
| `--crop_width` | `640` | 輸入圖片裁切寬度 |
| `--model` | `FC-DenseNet103` | 使用的模型名稱 |
| `--dataset` | `CamVid` | 使用的資料集名稱 |

**使用影片範例：**

```bash
python Main.py --inputVideo Video/test.mp4
```

### 輸出結果

執行後結果會存放至 `output/` 資料夾，包含：

- 原始擷取圖片
- 揮手偵測結果
- 街景語意分割結果
- 完整合成結果
- 從手機端接收的路線資訊

### 各程式說明

| 檔案 | 功能 |
|------|------|
| `Main.py` | 主程式入口，整合所有功能 |
| `app.py` | 手勢揮手偵測 |
| `marking.py` | 在圖上標記路線資訊與分析結果（程式前幾行可設定參數） |
| `handGestrueandMark.py` | 整合揮手偵測與圖上標記（含語音播報功能） |
| `read_txt.py` | 讀取手機端傳來的路線資訊 |
| `socketforapp.java` | 接收手機 App 的路線資料（需 Java 編譯執行，Python 版本較慢） |
| `client.py` | 傳送圖片（目前未啟用） |
| `server.py` | 接收圖片（目前未啟用） |

---

## 四、手機 App 設定

App 位於 `FancyNavi-master-手機APP程式/`，使用 Android Studio 開啟。

### 必要設定

使用前需修改連線目標的 IP 與 Port，對象為執行主程式的電腦：

- 編輯檔案：`app/src/main/java/com/fancynavi/android/app/MainActivity.java`
  - **第 267 行**：設定 IP 位址
  - **第 269 行**：設定 Port 號

> **注意：** 同時也需要修改主程式端的 `socketforapp.java` 對應設定。

---

## 系統需求

- Python 3.x
- TensorFlow 1.x（`tensorflow.compat.v1`）
- OpenCV（`cv2`）
- NumPy
- Pillow（PIL）
- MediaPipe（手勢辨識）
- Java（執行 `socketforapp.java`）
- Android Studio（編譯手機 App）
