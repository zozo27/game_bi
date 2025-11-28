#-*- coding:utf-8 -*-

import tkinter as tk
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup

def crawl_news():
    keyword = entry.get()
    if not keyword:
        text_area.insert(tk.END, "검색어를 입력하세요.\n")
        return

    url = f"https://search.naver.com/search.naver?where=news&query={keyword}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    titles = soup.select("a.news_tit")

    text_area.delete("1.0", tk.END)  # 기존 내용 삭제
    for t in titles:
        text_area.insert(tk.END, f"- {t.text}\n{t['href']}\n\n")

root = tk.Tk()
root.title("뉴스 크롤러")
root.geometry("500x400")

tk.Label(root, text="검색어를 입력하세요:").pack(pady=5)
entry = tk.Entry(root, width=40)
entry.pack(pady=5)

tk.Button(root, text="크롤링 시작", command=crawl_news).pack(pady=10)

text_area = scrolledtext.ScrolledText(root, width=60, height=15)
text_area.pack(pady=10)

root.mainloop()
