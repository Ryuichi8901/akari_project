#!/usr/bin/env python3

import grpc
import json
import threading
import sys
import os
import time
from typing import Any
from akari_client import AkariClient
from akari_client.color import Colors
from akari_client.position import Positions

from depthai_handface.HandFaceTracker import HandFaceTracker
from depthai_handface.HandFaceRenderer import HandFaceRenderer

sys.path.append(os.path.join(os.path.dirname(__file__), "akari_motion_server/lib/grpc"))
import motion_server_pb2
import motion_server_pb2_grpc

json_path = "log/log.json"

motion_server_port = "localhost:50055"
channel = grpc.insecure_channel(motion_server_port)
stub = motion_server_pb2_grpc.MotionServerServiceStub(channel)
akari = AkariClient()
m5 = akari.m5stack


def display_good_count(num) -> None:
    """
    いいねの数を表示する

    Args:
        num: int 表示するいいねの数

    """
    m5.set_display_text(
        text=str(num),
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=12,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )
    m5.set_display_text(
        text="いいね!",
        pos_x=Positions.BOTTOM,
        pos_y=Positions.RIGHT,
        size=5,
        text_color=Colors.BLACK,
        back_color=Colors.WHITE,
        refresh=False,
    )


def good_update(num: int) -> None:
    """
    いいねの数を更新する

    Args:
        num: int いいねの数
    """
    motion = "nod"  # 頷く動作を送信
    print("Send motion " + str(motion))
    try:
        reply = stub.SetMotion(
            motion_server_pb2.SetMotionRequest(
                name=motion, priority=3, repeat=False, clear=True
            )
        )
    except Exception as e:
        print("akari motion server set motion error")
    m5.set_display_text(
        text="Thank you!",
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=5,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
        sync=True,
    )
    time.sleep(1)
    display_good_count(num)
    result = {"good_count": num}
    with open(json_path, mode="wt", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main() -> None:
    """
    メイン関数
    """

    tracker = HandFaceTracker(
        input_src=None,
        double_face=False,
        use_face_pose=False,
        use_gesture=True,
        xyz=True,
        with_attention=False,
        nb_hands=2,
        trace=0,
    )
    
    json_open = open(json_path, "r")
    try:
        log = json.load(json_open)
    except json.JSONDecodeError:
        log = {"good_count": 0}
    total_good_count = log.get("good_count", 0)

    renderer = HandFaceRenderer(tracker=tracker, output=None)
    HAND_GOOD_THRESHOLD = 5  # グーのジェスチャーがこの回数以上検出されたら1いいねとカウント
    HAND_ERROR_THRESHOLD = 3  # グー以外がこの回数以上検出されたらリセット
    GOOD_LOCK_TIME = 2  # いいね後のロック時間
    last_count_time = time.time()
    hand_good_count = [0, 0]  # グーのカウント回数[左手、右手]
    hand_good_error_count = [0, 0]  # グー以外が抜けた回数[左手、右手]
    display_good_count(total_good_count)
    
    while True:
        frame, faces, hands = tracker.next_frame()
        if frame is None:
            break
        
        # Draw face and hands
        frame = renderer.draw(frame, faces, hands)
        
        for hand in hands:
            hand_num = 0
            if hand.label == "left":
                hand_num = 0
            elif hand.label == "right":
                hand_num = 1
            else:
                continue
            
            gesture_result = hand.gesture
            
            if gesture_result == "ROCK" and time.time() - last_count_time > GOOD_LOCK_TIME:
                hand_good_count[hand_num] += 1
            else:
                hand_good_error_count[hand_num] += 1
            
            # グーの検出回数が一定回数になったらいいねを加算
            if hand_good_count[hand_num] > HAND_GOOD_THRESHOLD:
                last_count_time = time.time()
                total_good_count += 1
                hand_good_count[hand_num] = 0
                hand_good_error_count[hand_num] = 0
                
                # グーの時にだけ「頷く」動作をする
                good_thread = threading.Thread(target=good_update, args=(total_good_count,))
                good_thread.start()
                
            elif hand_good_error_count[hand_num] > HAND_ERROR_THRESHOLD:
                hand_good_count[hand_num] = 0
                hand_good_error_count[hand_num] = 0

        key = renderer.waitKey(delay=1)
        if key == 27 or key == ord("q"):
            good_thread.join()
            time.sleep(1)
            m5.set_display_image("/jpg/logo320.jpg")
            break

    renderer.exit()
    tracker.exit()


if __name__ == "__main__":
    main()

!/usr/bin/env python3






# #!/usr/bin/env python3

# import grpc
# import json
# import threading
# import sys
# import os
# import time
# # ランダムにじゃんけんの手を決める
# import random  
# from typing import Any
# from akari_client import AkariClient
# from akari_client.color import Colors
# from akari_client.position import Positions

# # 手を常に認識するために使用する
# from depthai_handface.HandFaceTracker import HandFaceTracker
# from depthai_handface.HandFaceRenderer import HandFaceRenderer

# sys.path.append(os.path.join(os.path.dirname(__file__), "akari_motion_server/lib/grpc"))
# import motion_server_pb2
# import motion_server_pb2_grpc

# json_path = "log/log.json"

# # Akariロボットのモーションサーバーの設定
# motion_server_port = "localhost:50055"
# channel = grpc.insecure_channel(motion_server_port)
# stub = motion_server_pb2_grpc.MotionServerServiceStub(channel)
# akari = AkariClient()
# m5 = akari.m5stack

# # じゃんけんの結果を表示する
# def display_result(result):
#     m5.set_display_text(
#         text=result,
#         pos_x=Positions.CENTER,
#         pos_y=Positions.CENTER,
#         size=12,
#         text_color=Colors.RED,
#         back_color=Colors.WHITE,
#         refresh=True,
#     )

# # 
# def recognize_gesture(gesture_result):
#     if gesture_result == "rock":  # グー
#         return "グー"
#     elif gesture_result == "scissors":  # チョキ
#         return "チョキ"
#     elif gesture_result == "paper":  # パー
#         return "パー"
#     return None

# # 勝ちか負けかを判断する
# def judge(player_hand, akari_hand):
#     if player_hand ==akari_hand:
#         return "引き分け"
#     elif (player_hand == "グー" and akari_hand == "チョキ") or \
#          (player_hand == "チョキ" and akari_hand == "パー") or \
#          (player_hand == "パー" and akari_hand == "グー"):
#         return "勝ち"
#     else:
#         return "負け"

# # メイン関数
# def main() -> None:
#     tracker = HandFaceTracker(
#         input_src=None,
#         double_face=False,
#         use_face_pose=False,
#         input_src=None, 
#         with_attention=False,
#         trace=0,
#         # いちよ手の位置計算（視認用）
#         xyz=True,
#         # 手のジェスチャーを有効にする
#         use_gesture=True, 
#         # 片手のみ認識
#         nb_hands=1
#         )
    
#     # 描画準備
#     renderer = HandFaceRenderer(tracker=tracker, output=None)

#     while True:
#         # 次のフレームの情報を入手
#         frame, faces, hands = tracker.next_frame()
#         if frame is None:
#             break

#         # フレームを描画
#         frame = renderer.draw(frame, faces, hands)

        
#         for hand in hands:
#             # じゃんけんの手を取得する
#             gesture_result = hand.gesture
#             player_hand = recognize_gesture(gesture_result)
#             if player_hand:
#                 # akariの手を決める
#                 akari_hand = random.choice(["グー", "チョキ", "パー"])
#                 # じゃんけん判定
#                 result = judge(player_hand,akari_hand)
#                 display_result(f"あなたの手: {player_hand}, Akariの手: {akari_hand}, 結果: {result}")
#                 # display_result(result)
#                 time.sleep(1)
        
#         if renderer.waitKey(delay=1) == ord('q'):
#             break

#     renderer.exit()
#     tracker.exit()

# if __name__ == "__main__":
#     main()
