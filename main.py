# あいこがまだできていない状態
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
import queue

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
def display_result(player_hand, akari_hand, result):
    m5.set_display_text(
        text=f"あなたの手: {player_hand}",
        pos_x=Positions.CENTER,
        pos_y=30,
        size=2,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=False,
    )
    
    m5.set_display_text(
        text=f"Akariの手: {akari_hand}",
        pos_x=Positions.CENTER,
        pos_y=90,
        size=2,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=False,
    )
    
    m5.set_display_text(
        text=f"結果: {result}",
        pos_x=Positions.CENTER,
        pos_y=150,
        size=2,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )

    if result == "勝ち":
        joints = akari.joints
        joints.enable_all_servo()
        joints.set_joint_velocities(pan = 2, tilt = 2)
        joints.move_joint_positions(pan = 0.0, tilt = -0.5)
        time.sleep(3)
        joints.move_joint_positions(pan = 0.0, tilt = 0.0)

# カウントダウンを表示
def display_count(akari_hand, result_queue):

    for i in range(3, 0, -1):
        m5.set_display_text(
            text=f"じゃんけんスタートまで{i}秒",
            pos_x=Positions.CENTER,
            pos_y=Positions.CENTER,
            size=2,
            text_color=Colors.RED,
            back_color=Colors.WHITE,
            refresh=True,
        )
        time.sleep(1)

    m5.set_display_text(
        text="最初はグー",
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=2,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )
    time.sleep(1)

    m5.set_display_text(
        text="じゃんけん",
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=2,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )
    time.sleep(1)

    m5.set_display_text(
        text=f"ぽん {akari_hand}",
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=2,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )
    time.sleep(1)

    # カウントダウンが終わったタイミングでAkariの手をキューに追加
    result_queue.put(akari_hand)  

# 手の判定
def recognize_gesture(gesture_result):
    if gesture_result == "FIST":  # グー
        return "グー"
    elif gesture_result == "PEACE":  # チョキ
        return "チョキ"
    elif gesture_result == "FIVE":  # パー
        return "パー"
    return None

# じゃんけんの結果を判定
def judge(player_hand, akari_hand):
    if player_hand == akari_hand:
        return "引き分け"
    elif (player_hand == "グー" and akari_hand == "チョキ") or \
         (player_hand == "チョキ" and akari_hand == "パー") or \
         (player_hand == "パー" and akari_hand == "グー"):
        return "勝ち"
    else:
        return "負け"

# 手のジェスチャーを処理して，じゃんけんの進行状況を制御
def process_hand_gesture(hands, janken_progress, result_queue):
    for hand in hands:
        gesture_result = hand.gesture
        if janken_pose(gesture_result) and not janken_progress:
            janken_progress = True
            akari_hand = random.choice(["グー", "チョキ", "パー"])
            # display_countを非同期で実行（重くならないように）
            janken_thread = threading.Thread(target=display_count, args=(akari_hand, result_queue))
            janken_thread.start()
    return janken_progress, gesture_result

# akariの手をキューから取り出して，じゃんけんの結果を判定し表示する
def process_display_result(result_queue, gesture_result, janken_progress):
    if not result_queue.empty():
        akari_hand = result_queue.get()
        player_hand = recognize_gesture(gesture_result)
        if player_hand:
            result = judge(player_hand, akari_hand)
            display_result(player_hand, akari_hand, result)
        janken_progress = False  # ゲームを終了
    return janken_progress

# メイン関数
def main() -> None:
    tracker = HandFaceTracker(
        input_src=None,
        double_face=False,
        use_face_pose=False, 
        with_attention=False,
        trace=0,
        xyz=True,
        use_gesture=True, 
        nb_hands=1
    )
    
    renderer = HandFaceRenderer(tracker=tracker, output=None)

    janken_progress = False
    result_queue = queue.Queue()

    while True:
        frame, faces, hands = tracker.next_frame()
        if frame is None:
            break

        frame = renderer.draw(frame, faces, hands)
        
        # 手のジェスチャー処理，カウントダウン
        janken_progress, gesture_result = process_hand_gesture(hands, janken_progress, result_queue)

        # カウントダウンが終了したらじゃんけんを判定し結果を表示
        janken_progress = process_display_result(result_queue, gesture_result, janken_progress)

        if renderer.waitKey(delay=1) == ord('q'):
            break

    renderer.exit()
    tracker.exit()

if __name__ == "__main__":
    main()