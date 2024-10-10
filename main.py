#!/usr/bin/env python3

import grpc
import json
import threading
import sys
import os
import time
# ランダムにじゃんけんの手を決める
import random  
from typing import Any
from akari_client import AkariClient
from akari_client.color import Colors
from akari_client.position import Positions

# 手を常に認識するために使用する
from depthai_handface.HandFaceTracker import HandFaceTracker
from depthai_handface.HandFaceRenderer import HandFaceRenderer

sys.path.append(os.path.join(os.path.dirname(__file__), "akari_motion_server/lib/grpc"))
import motion_server_pb2
import motion_server_pb2_grpc

json_path = "log/log.json"

# Akariロボットのモーションサーバーの設定
motion_server_port = "localhost:50055"
channel = grpc.insecure_channel(motion_server_port)
stub = motion_server_pb2_grpc.MotionServerServiceStub(channel)
akari = AkariClient()
m5 = akari.m5stack

# じゃんけんの結果を表示する
def display_result(result):
    m5.set_display_text(
        text=result,
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=12,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )

# 
def recognize_gesture(gesture_result):
    if gesture_result == "rock":  # グー
        return "グー"
    elif gesture_result == "scissors":  # チョキ
        return "チョキ"
    elif gesture_result == "paper":  # パー
        return "パー"
    return None

# 勝ちか負けかを判断する
def judge(player_hand, akari_hand):
    if player_hand ==akari_hand:
        return "引き分け"
    elif (player_hand == "グー" and akari_hand == "チョキ") or \
         (player_hand == "チョキ" and akari_hand == "パー") or \
         (player_hand == "パー" and akari_hand == "グー"):
        return "勝ち"
    else:
        return "負け"

# メイン関数
def main() -> None:
    tracker = HandFaceTracker(
        input_src=None,
        double_face=False,
        use_face_pose=False,
        input_src=None, 
        with_attention=False,
        trace=0,
        # いちよ手の位置計算（視認用）
        xyz=True,
        # 手のジェスチャーを有効にする
        use_gesture=True, 
        # 片手のみ認識
        nb_hands=1
        )
    
    # 描画準備
    renderer = HandFaceRenderer(tracker=tracker, output=None)

    while True:
        # 次のフレームの情報を入手
        frame, faces, hands = tracker.next_frame()
        if frame is None:
            break

        # フレームを描画
        frame = renderer.draw(frame, faces, hands)

        
        for hand in hands:
            # じゃんけんの手を取得する
            gesture_result = hand.gesture
            player_hand = recognize_gesture(gesture_result)
            if player_hand:
                # akariの手を決める
                akari_hand = random.choice(["グー", "チョキ", "パー"])
                # じゃんけん判定
                result = judge(player_hand,akari_hand)
                display_result(f"あなたの手: {player_hand}, Akariの手: {akari_hand}, 結果: {result}")
                # display_result(result)
                time.sleep(1)
        
        if renderer.waitKey(delay=1) == ord('q'):
            break

    renderer.exit()
    tracker.exit()

if __name__ == "__main__":
    main()
