#!/usr/bin/env python3

import grpc
import threading
import sys
import os
import time
import random
from akari_client import AkariClient
from akari_client.color import Colors
from akari_client.position import Positions
from depthai_handface.HandFaceTracker import HandFaceTracker
from depthai_handface.HandFaceRenderer import HandFaceRenderer

sys.path.append(os.path.join(os.path.dirname(__file__), "akari_motion_server/lib/grpc"))
import motion_server_pb2
import motion_server_pb2_grpc

# Akariロボットのモーションサーバーの設定
motion_server_port = "localhost:50055"
channel = grpc.insecure_channel(motion_server_port)
stub = motion_server_pb2_grpc.MotionServerServiceStub(channel)
akari = AkariClient()
m5 = akari.m5stack

# 特定のポーズを認識するため（goodであるかどうか）
def janken_pose(gesture_result):
    return gesture_result == "OK"

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

# カウントダウンを別スレッドで実行
def display_count(akari_hand):
    for i in range(3, 0, -1):
        m5.set_display_text(
            text=f"じゃんけんスタートまで{i}秒",
            pos_x=Positions.CENTER,
            pos_y=Positions.CENTER,
            size=12,
            text_color=Colors.RED,
            back_color=Colors.WHITE,
            refresh=True,
        )
        time.sleep(1)

    m5.set_display_text(
        text="最初はグー",
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=12,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )
    time.sleep(1)

    m5.set_display_text(
        text="じゃんけん",
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=12,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )
    time.sleep(1)

    m5.set_display_text(
        text=f"ぽん {akari_hand}",
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=12,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )

def recognize_gesture(gesture_result):
    if gesture_result == "FIST":  # グー
        return "グー"
    elif gesture_result == "PEACE":  # チョキ
        return "チョキ"
    elif gesture_result == "FIVE":  # パー
        return "パー"
    return None

def judge(player_hand, akari_hand):
    if player_hand == akari_hand:
        return "引き分け"
    elif (player_hand == "グー" and akari_hand == "チョキ") or \
         (player_hand == "チョキ" and akari_hand == "パー") or \
         (player_hand == "パー" and akari_hand == "グー"):
        return "勝ち"
    else:
        return "負け"

# じゃんけんの処理を別スレッドで実行
def start_janken(gesture_result):
    akari_hand = random.choice(["グー", "チョキ", "パー"])
    display_count_thread = threading.Thread(target=display_count, args=(akari_hand,))
    display_count_thread.start()

    player_hand = recognize_gesture(gesture_result)
    if player_hand:
        result = judge(player_hand, akari_hand)
        display_result(f"あなたの手: {player_hand}, Akariの手: {akari_hand}, 結果: {result}")
        display_count_thread.join()

# メイン関数
def main() -> None:
    tracker = HandFaceTracker(
        input_src=None,
        double_face=False,
        use_face_pose=False,
        input_src=None, 
        with_attention=False,
        trace=0,
        xyz=True,
        use_gesture=True, 
        nb_hands=1
    )
    
    renderer = HandFaceRenderer(tracker=tracker, output=None)

    while True:
        frame, faces, hands = tracker.next_frame()
        if frame is None:
            break

        frame = renderer.draw(frame, faces, hands)

        for hand in hands:
            gesture_result = hand.gesture
            if janken_pose(gesture_result):
                janken_thread = threading.Thread(target=start_janken, args=(gesture_result,))
                janken_thread.start()
        
        if renderer.waitKey(delay=1) == ord('q'):
            break

    renderer.exit()
    tracker.exit()

if __name__ == "__main__":
    main()
