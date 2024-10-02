#!/usr/bin/env python3

import sys
import time
import threading
import json
import os
from akari_client import AkariClient
from akari_client.color import Colors
from akari_client.position import Positions
from depthai_handface.HandFaceTracker import HandFaceTracker
from depthai_handface.HandFaceRenderer import HandFaceRenderer

akari = AkariClient()
m5 = akari.m5stack

# グーチョキパーを表示する関数
def display_gesture_result(gesture_result) -> None:
    """
    ジェスチャーの結果をM5Stackに表示する
    """
    gesture_text = {
        "FIST": "グー ✊",     # グー (握り拳)
        "PEACE": "チョキ ✌️",   # チョキ (ピースサイン)
        "FIVE": "パー 🖐️",     # パー (手のひら)
    }.get(gesture_result, "不明 🤷")  # 該当しない場合は不明と表示

    m5.set_display_text(
        text=gesture_text,
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
        input_src=None,
        double_face=False,
        use_face_pose=False,
        use_gesture=True,       # ジェスチャー認識を有効化
        xyz=True,               # 手の位置を取得
        with_attention=False,
        nb_hands=2,             # 両手の認識
        trace=0,
    )

    # Rendererを初期化
    renderer = HandFaceRenderer(tracker=tracker, output=None)

    while True:
        frame, faces, hands = tracker.next_frame()
        if frame is None:
            break

        # 手が検出された場合、ジェスチャーを表示
        for hand in hands:
            gesture_result = hand.gesture  # ジェスチャーの結果を取得
            if gesture_result in ["FIST", "PEACE", "FIVE"]:  # グー、チョキ、パーのみ処理
                print(f"Detected Gesture: {gesture_result}")
                display_gesture_result(gesture_result)  # M5Stackに表示

        key = renderer.waitKey(delay=1)
        if key == 27 or key == ord("q"):  # 'q'キーで終了
            break

    # 終了処理
    renderer.exit()
    tracker.exit()

if __name__ == "__main__":
    main()
