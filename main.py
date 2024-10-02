#!/usr/bin/env python3

import sys
from depthai_handface.HandFaceTracker import HandFaceTracker
from depthai_handface.HandFaceRenderer import HandFaceRenderer

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

    # Rendererを初期化（手の認識結果を描画するための設定）
    renderer = HandFaceRenderer(tracker=tracker, output=None)

    while True:
        # 手のフレームデータを取得
        frame, faces, hands = tracker.next_frame()
        if frame is None:
            break

        # 手が検出された場合、その情報をコンソールに出力
        for hand in hands:
            gesture_result = hand.gesture  # ジェスチャーの結果を取得
            if gesture_result:
                print(f"Hand Gesture Detected: {gesture_result}")

        # 描画とキー入力の処理
        key = renderer.waitKey(delay=1)
        if key == 27 or key == ord("q"):  # 'q'キーで終了
            break

    # 終了処理
    renderer.exit()
    tracker.exit()

if __name__ == "__main__":
    main()
