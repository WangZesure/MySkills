#!/usr/bin/env python3
"""arXiv 文献检索助手（点调研用）。

功能：串行执行多条 arXiv API 查询，代理 + 429 指数退避，打印标题/ID/摘要片段。
用法：
  python arxiv_search.py "查询1" "查询2" ...            # 命令行直接传查询
  python arxiv_search.py --file queries.txt             # 从文件读查询（每行一条）

查询语法（arXiv API）:
  all:"词组"         任意字段包含
  ti:"标题"          标题精确匹配
  cat:cs.CV          学科过滤
  多个词用 AND 连接，整体传给 API 前会自动 URL 编码
"""
import re
import sys
import time
import urllib.request
import urllib.parse

PROXY = "http://127.0.0.1:7890"   # 无代理时置 None
MAX_RESULTS = 8
SLEEP_BETWEEN = 20                 # 查询间隔（秒），防 429


def build_opener():
    if PROXY:
        proxy = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
        opener = urllib.request.build_opener(proxy)
    else:
        opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")]
    return opener


def fetch(opener, query, max_retries=5):
    url = ("https://export.arxiv.org/api/query?search_query="
           + urllib.parse.quote(query)
           + f"&sortBy=submittedDate&sortOrder=descending&max_results={MAX_RESULTS}")
    for attempt in range(max_retries):
        try:
            return opener.open(url, timeout=40).read().decode("utf-8", "ignore")
        except Exception as e:
            print(f"    [retry {attempt + 1}] {e}")
            time.sleep(15 * (attempt + 1))
    return None


def print_entries(xml, show_abstract=True, abstract_len=250):
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.S)
    print(f"    ({len(entries)} 条)")
    for e in entries:
        t = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, re.S).group(1)).strip()
        idm = re.search(r"<id>http://arxiv.org/abs/(.*?)</id>", e).group(1)
        print(f"  {idm} | {t}")
        if show_abstract:
            s = re.sub(r"\s+", " ", re.search(r"<summary>(.*?)</summary>", e, re.S).group(1)).strip()
            print(f"      {s[:abstract_len]}")


def main():
    queries = sys.argv[1:]
    if not queries:
        print(__doc__)
        return
    opener = build_opener()
    for q in queries:
        print(f"\n{'=' * 70}\n=== {q} ===\n{'=' * 70}")
        xml = fetch(opener, q)
        if xml:
            print_entries(xml)
        else:
            print("    FAILED after retries")
        time.sleep(SLEEP_BETWEEN)


if __name__ == "__main__":
    main()
