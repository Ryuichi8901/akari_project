# akari_nemuken

## 他の案
### 参考文献
https://github.com/geaxgx/depthai_handface/blob/main/HandFaceTracker.py
https://docs.luxonis.com/software/


# akari_nemuken
AKARIとじゃんけんをしたり、AKARIがユーザーの眠気検知をするアプリです。

## 動作確認済み環境
AKARI上で動作確認済み。
**スピーカーは別途外付けする必要があります・**

## セットアップ
1. ローカルにクローンする  
cd ~  
git clone #########  
cd akari_project  
2. 仮想環境の作成  
pip install mediapipe
pip install depthai
pip install cv2

## 起動方法
1. 顔認識やて認識を行うためにAKARIのカメラを起動させる



# akari_treasure_hunt
AKARIと宝探しゲームで勝負できるアプリです。  

## セットアップ方法
1. ローカルにクローンする  
cd ~  
git clone https://github.com/AkariGroup/akari_treasure_hunt.git  
cd akari_treasure_hunt  
2. submoduleの更新  
git submodule update --init  
3. 仮想環境の作成  
python3 -m venv venv  
. venv/bin/activate  
pip install -r requirements.txt  
## 配置方法
![AKARI_Setting.jpg](jpg/akaritreasurehunt.jpg)

## 起動方法
1. 仮想環境の有効化  
. venv/bin/activate

2. 問題をディスプレイに表示する。  
問題表示用のPCを準備し、questionsディレクトリ内の candy.mp4 もしくは key.mp4を選択して画面に映す。

3. 物体認識を実行する
python3 treasure_hunt.py

4. 物体認識を終了する  
AKARI_VIEWウィンドウを選択した状態でキーボードのqキーを押す。

## その他
このアプリケーションは愛知工業大学 情報科学部 知的制御研究室により作成されたものです。