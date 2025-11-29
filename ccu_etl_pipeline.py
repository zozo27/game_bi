import csv
import os
import time
from datetime import datetime, timedelta
import pandas as pd
from threading import Thread
import math
import random

# ===========================================================
#  KST 시간 함수
# ===========================================================
def now_kst():
    return datetime.utcnow() + timedelta(hours=9)


# ===========================================================
#  프로그램 시작 시 모든 CSV 삭제
# ===========================================================
def cleanup_csv_files(directory="dashboard/data"):
    """
    프로그램 시작 시 기존 모든 ccu_snapshot_*.csv 삭제
    """
    if not os.path.exists(directory):
        return

    removed = 0
    for filename in os.listdir(directory):
        if filename.startswith("ccu_snapshot_") and filename.endswith(".csv"):
            path = os.path.join(directory, filename)
            try:
                os.remove(path)
                removed += 1
            except Exception as e:
                print(f"[ERROR] 파일 삭제 실패: {path} - {e}")

    print(f"[INIT] 삭제된 CSV 파일 수: {removed}")


# ===========================================================
#  이전 날짜 CSV 자동 삭제 (오늘 날짜 제외)
# ===========================================================
def delete_old_snapshot_files(directory="dashboard/data", keep_date=None):
    """
    오늘 날짜(keep_date)만 유지하고 나머지 모든 스냅샷 CSV 삭제
    """
    if not os.path.exists(directory):
        return

    removed = 0
    for filename in os.listdir(directory):
        if filename.startswith("ccu_snapshot_") and filename.endswith(".csv"):

            # 오늘 날짜 파일은 유지
            if keep_date in filename:
                continue

            path = os.path.join(directory, filename)
            try:
                os.remove(path)
                removed += 1
            except Exception as e:
                print(f"[ERROR] 이전 파일 삭제 실패: {path} - {e}")

    print(f"[OLD CLEANUP] 이전 날짜 CSV 삭제 수: {removed}")


# ===========================================================
#  Daily CSV Writer (5초 단위 스냅샷 기록)
# ===========================================================
class DailyCSVWriter:
    def __init__(self, output_dir="dashboard/data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.current_date = now_kst().strftime("%Y%m%d")
        self.filepath = os.path.join(self.output_dir, f"ccu_snapshot_{self.current_date}.csv")

        # 새 파일 생성 시 헤더 넣기
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["snapshot_time", "game_id", "server_id", "region", "ccu"])

    def rollover_if_needed(self):
        """날짜 변경 감지 → 새로운 CSV 생성 + 이전 날짜 파일 삭제"""
        new_date = now_kst().strftime("%Y%m%d")
        if new_date != self.current_date:

            # 날짜 변경 → 새로운 파일로 롤오버
            self.current_date = new_date
            self.filepath = os.path.join(self.output_dir, f"ccu_snapshot_{new_date}.csv")

            # 헤더 생성
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["snapshot_time", "game_id", "server_id", "region", "ccu"])

            print(f"[롤오버] 새 CSV 파일 생성 → {self.filepath}")

            # ★ 날짜가 바뀌면 이전 파일 자동 삭제
            delete_old_snapshot_files(self.output_dir, keep_date=new_date)

    def write_snapshot(self, record):
        """5초 단위 스냅샷 기록"""
        self.rollover_if_needed()

        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(record)

        print(f"[스냅샷 저장] {record}")


# ===========================================================
#  1분 단위 집계
# ===========================================================
def aggregate_minute_snapshot(input_csv_path, output_dir="dashboard/data"):
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_csv_path):
        print(f"[WARN] 원본 CSV 없음 → {input_csv_path}")
        return

    df = pd.read_csv(input_csv_path)
    if df.empty:
        return

    df['snapshot_time'] = pd.to_datetime(df['snapshot_time'])
    df['minute'] = df['snapshot_time'].dt.strftime('%Y-%m-%d %H:%M')

    current_minute = now_kst().strftime('%Y-%m-%d %H:%M')
    df = df[df['minute'] < current_minute]

    if df.empty:
        print("[INFO] 확정된 1분 데이터 없음")
        return

    agg_df = df.groupby(['minute', 'game_id', 'server_id', 'region']).agg(
        ccu_avg=('ccu', 'mean'),
        ccu_max=('ccu', 'max'),
        ccu_min=('ccu', 'min'),
        samples=('ccu', 'count')
    ).reset_index()

    agg_df['ccu_avg'] = agg_df['ccu_avg'].astype(int)

    date_str = df['snapshot_time'].dt.strftime('%Y%m%d').iloc[0]
    output_file = os.path.join(output_dir, f"ccu_snapshot_{date_str}_minute.csv")
    agg_df.to_csv(output_file, index=False)

    now_str = now_kst().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now_str}] 1분 집계 완료 → {output_file}")


# ===========================================================
# 5초 스냅샷 쓰레드
# ===========================================================
def run_snapshot_writer():
    writer = DailyCSVWriter("dashboard/data")

    base_ccu = 10000
    period_day = 86400
    period_hour = 3600
    amplitude_day = 4000
    amplitude_hour = 1000

    start_time = time.time()
    interval = 5  # 5초

    while True:
        loop_start = time.time()

        snapshot_time = now_kst().strftime('%Y-%m-%d %H:%M:%S')
        elapsed = time.time() - start_time

        daily_wave = amplitude_day * math.sin(2 * math.pi * elapsed / period_day)
        hourly_wave = amplitude_hour * math.sin(2 * math.pi * elapsed / period_hour)
        noise = random.randint(-200, 200)

        event_spike = 0
        hour = now_kst().hour
        minute = now_kst().minute
        if (hour == 12 or hour == 18) and 0 <= minute < 5:
            event_spike = random.randint(800, 2000)

        ccu = int(base_ccu + daily_wave + hourly_wave + noise + event_spike)

        record = [snapshot_time, 1002, 2, "ASIA", ccu]
        writer.write_snapshot(record)

        loop_end = time.time()
        sleep_time = interval - (loop_end - loop_start)
        if sleep_time > 0:
            time.sleep(sleep_time)


# ===========================================================
# 1분 집계 쓰레드
# ===========================================================
def run_minute_aggregator():
    print("[1분 집계 스케줄러 시작]")

    while True:
        now = now_kst()
        sleep_time = 60 - now.second - now.microsecond / 1_000_000
        time.sleep(sleep_time)

        date = now_kst().strftime('%Y%m%d')
        input_file = f"dashboard/data/ccu_snapshot_{date}.csv"
        aggregate_minute_snapshot(input_file)


# ===========================================================
# 메인 실행부
# ===========================================================
if __name__ == "__main__":
    print("=== CCU 스냅샷 + 1분 단위 집계 통합 서비스 시작 ===")

    # 프로그램 시작 시 기존 파일 삭제
    cleanup_csv_files("dashboard/data")

    Thread(target=run_snapshot_writer, daemon=True).start()
    Thread(target=run_minute_aggregator, daemon=True).start()

    while True:
        time.sleep(1)
    

