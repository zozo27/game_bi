from flask import Flask, render_template, request
import csv
from datetime import datetime

app = Flask(__name__)

# CSV 파일 경로
CSV_PATH = r"C:\Users\zozo26\Desktop\입사지원\portfolio\game_bi\dashboard\data\ccu_snapshot_20251128.csv"

# CSV 읽기 함수
def read_csv():
    data = []
    with open(CSV_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['game_id'] = int(row['game_id'])
            row['server_id'] = int(row['server_id'])
            row['ccu'] = int(row['ccu'])
            row['snapshot_time'] = datetime.strptime(row['snapshot_time'], "%Y-%m-%d %H:%M:%S")
            data.append(row)
    return data


@app.route('/', methods=['GET', 'POST'])
def index():
    rows = None  # 검색 결과 (처음엔 없음)

    if request.method == 'POST':
        game_id = request.form.get('game_id')
        server_id = request.form.get('server_id')
        region = request.form.get('region')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        min_ccu = request.form.get('min_ccu')
        max_ccu = request.form.get('max_ccu')

        data = read_csv()
        filtered = data

        if game_id:
            filtered = [d for d in filtered if d['game_id'] == int(game_id)]

        if server_id:
            filtered = [d for d in filtered if d['server_id'] == int(server_id)]

        if region:
            filtered = [d for d in filtered if d['region'].lower() == region.lower()]

        if start_time:
            t = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            filtered = [d for d in filtered if d['snapshot_time'] >= t]

        if end_time:
            t = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            filtered = [d for d in filtered if d['snapshot_time'] <= t]

        if min_ccu:
            filtered = [d for d in filtered if d['ccu'] >= int(min_ccu)]

        if max_ccu:
            filtered = [d for d in filtered if d['ccu'] <= int(max_ccu)]

        rows = filtered

    return render_template('search.html', rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
