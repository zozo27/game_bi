import os
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# ------------------------------
# KST 시간
# ------------------------------
def now_kst():
    return datetime.utcnow() + timedelta(hours=9)

# ------------------------------
# 오늘 CSV 파일 경로
# ------------------------------
def get_today_csv_path():
    date = now_kst().strftime("%Y%m%d")
    return f"/home/ubuntu/game_bi/dashboard/data/ccu_snapshot_{date}.csv"

# ------------------------------
# CSV 읽어서 CCU 반환
# ------------------------------
def load_ccu_csv():
    path = get_today_csv_path()

    if not os.path.exists(path):
        return [], []

    try:
        df = pd.read_csv(path)
        if df.empty:
            return [], []

        return df["snapshot_time"].tolist(), df["ccu"].tolist()

    except:
        return [], []

# ------------------------------
# CSV 읽어서 로그 형태로 반환
# ------------------------------
def load_log_csv():
    path = get_today_csv_path()

    if not os.path.exists(path):
        return []

    try:
        df = pd.read_csv(path)
        if df.empty:
            return []

        logs = []
        for _, row in df.iterrows():
            logs.append(f"[{row['snapshot_time']}] game:{row['game_id']} server:{row['server_id']} region:{row['region']} → CCU {row['ccu']}")

        return logs

    except Exception as e:
        print("CSV 로그 로드 오류:", e)
        return []

# ------------------------------
# API: CCU
# ------------------------------
@app.route("/api/ccu")
def api_ccu():
    time_list, ccu_list = load_ccu_csv()
    return jsonify({
        "time": time_list,
        "ccu": ccu_list
    })

# ------------------------------
# API: 로그
# ------------------------------
@app.route("/api/logs")
def api_logs():
    logs = load_log_csv()
    return jsonify(logs[-200:])   # 최신 200개만 전송

# ------------------------------
# 메인 화면
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ------------------------------
# 실행
# ------------------------------
if __name__ == "__main__":
    print("=== CCU CSV Dashboard 서버 시작 ===")
    app.run(host="0.0.0.0", port=5000, debug=True)
