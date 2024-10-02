#!/usr/bin/env python3

import sys
import time
from akari_client import AkariClient
from akari_client.color import Colors
from akari_client.position import Positions

# DepthAIの手の認識クラスをインポート
from depthai_handface.HandFaceTracker import HandFaceTracker
from depthai_handface.HandFaceRenderer import HandFaceRenderer

# Akariのクライアント設定
akari = AkariClient()
m5 = akari.m5stack  # M5Stackのインスタンスを取得

# 手のジェスチャー結果をM5Stackに表示する関数
def display_gesture_result(gesture_result) -> None:
    m5.set_display_text(
        text=gesture_result,
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=12,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )

# メイン処理
def main() -> None:
    # DepthAIの手の認識トラッカーを初期化
    tracker = HandFaceTracker(
        input_src=None,         # カメラソースの設定
        double_face=False,      # 顔認識はオフ
        use_face_pose=False,    # 顔のポーズ推定もオフ
        use_gesture=True,       # ジェスチャー認識をオン
        xyz=True,               # 手の位置を取得
        with_attention=False,   # 注視機能はオフ
        nb_hands=2,             # 両手を認識
        trace=0,
    )

    # Rendererを初期化（画面に手の認識結果を描画）
    renderer = HandFaceRenderer(tracker=tracker, output=None)

    while True:
        # 手のフレームデータを取得
        frame, faces, hands = tracker.next_frame()
        if frame is None:
            break

        # 手が検出された場合、ジェスチャーを表示
        for hand in hands:
            gesture_result = hand.gesture  # ジェスチャーの結果を取得
            if gesture_result:
                print(f"Hand Gesture Detected: {gesture_result}")
                display_gesture_result(gesture_result)  # M5Stackに表示

        # 描画とキー入力の処理
        key = renderer.waitKey(delay=1)
        if key == 27 or key == ord("q"):  # 'q'キーで終了
            m5.set_display_image("/jpg/logo320.jpg")  # 終了時に画像を表示
            break

    # 終了処理
    renderer.exit()
    tracker.exit()

if __name__ == "__main__":
    main()
