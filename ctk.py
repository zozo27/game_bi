#-*- coding:utf-8 -*-

import customtkinter as ctk
from tkinter import filedialog
import pandas as pd

app = ctk.CTk()
app.title("데이터 정합성 검증 프로그램")
app.geometry("700x500")

# 결과 표시용 텍스트박스
textbox = ctk.CTkTextbox(app, width=650, height=350)
textbox.pack(pady=20)

# 전역 변수
df = None

def load_file():
    global df
    file_path = filedialog.askopenfilename(
        title="CSV 파일 선택",
        filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        return
    textbox.delete("1.0", "end")
    textbox.insert("end", f"📂 선택한 파일: {file_path}\n\n")

    try:
        df = pd.read_csv(file_path)
        textbox.insert("end", f"✅ 파일 로드 완료 ({len(df)}행)\n")
        textbox.insert("end", f"열 목록: {list(df.columns)}\n\n")
    except Exception as e:
        textbox.insert("end", f"❌ 파일을 읽는 중 오류: {e}\n")

def validate_data():
    global df
    if df is None:
        textbox.insert("end", "⚠ 먼저 CSV 파일을 불러오세요.\n")
        return

    textbox.insert("end", "\n🔍 데이터 정합성 검증 시작...\n")
    results = []

    # 1️⃣ 결측치(빈값) 검증
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            results.append(f"[결측치] {col}: {count}개")

    # 2️⃣ 중복 행 검증
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        results.append(f"[중복] 중복된 행 {dup_count}개 발견")

    # 3️⃣ 특정 열 값 범위 검사 (예: '나이' 열이 0~120 범위 벗어남)
    if "나이" in df.columns:
        invalid_age = df[(df["나이"] < 0) | (df["나이"] > 120)]
        if len(invalid_age) > 0:
            results.append(f"[범위 오류] 나이 열에 이상값 {len(invalid_age)}개")

    # 결과 출력
    if results:
        textbox.insert("end", "\n🚨 검증 결과:\n")
        for r in results:
            textbox.insert("end", f"- {r}\n")
    else:
        textbox.insert("end", "\n✅ 모든 데이터가 정상입니다.\n")

    # 결과 저장
    result_file = "validation_result.csv"
    df.to_csv(result_file, index=False, encoding="utf-8-sig")
    textbox.insert("end", f"\n💾 결과를 '{result_file}' 파일로 저장했습니다.\n")


ctk.CTkButton(app, text="📂 파일 선택", command=load_file).pack(pady=5)
ctk.CTkButton(app, text="✅ 검증 시작", command=validate_data).pack(pady=5)

app.mainloop()
