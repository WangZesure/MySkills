#!/usr/bin/env python3
"""Semantic Scholar 引用图助手（线调研用）。

功能：给定锚点论文的 arXiv ID，双向拉引用关系并输出按年份排序的时间线。
  references = 向后（根源）；citations = 向前（演进）

用法：
  python ss_graph.py 2606.27192 --depth 2 --filter "condition,diffusion,side network"
  python ss_graph.py 2606.27192 --direction both --filter ""

说明：
  --depth    扩展层数（1 或 2，避免图爆炸）
  --filter   逗号分隔关键词，标题/摘要命中任一才保留（排除基础设施引用）
  --direction both|references|citations
"""
import argparse
import json
import re
import time
import urllib.request
import urllib.parse

PROXY = "http://127.0.0.1:7890"   # 无代理时置 None
FIELDS = "title,year,abstract,externalIds"
SLEEP = 2.0                       # Semantic Scholar 限流较松，2s 间隔足够


def build_opener():
    if PROXY:
        proxy = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
        opener = urllib.request.build_opener(proxy)
    else:
        opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
    return opener


def fetch(opener, url, max_retries=4):
    for attempt in range(max_retries):
        try:
            return opener.open(url, timeout=40).read().decode("utf-8", "ignore")
        except Exception as e:
            print(f"    [retry {attempt + 1}] {e}")
            time.sleep(8 * (attempt + 1))
    return None


def get_papers(opener, arxiv_id, direction, offset=0, limit=50):
    url = (f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}"
           f"/{direction}?fields={FIELDS}&limit={limit}&offset={offset}")
    raw = fetch(opener, url)
    if raw is None:
        return []
    data = json.loads(raw)
    out = []
    for item in data.get("data", []):
        p = item["citedPaper"] if direction == "references" else item["citingPaper"]
        if p is None:
            continue
        aid = (p.get("externalIds") or {}).get("ArXiv")
        if not aid:
            continue
        out.append({
            "id": aid,
            "title": (p.get("title") or "").strip(),
            "year": p.get("year"),
            "abstract": (p.get("abstract") or ""),
        })
    return out


def matches(p, keywords):
    if not keywords:
        return True
    text = (p["title"] + " " + (p["abstract"] or "")).lower()
    return any(k.lower() in text for k in keywords)


def main():
    ap = argparse.ArgumentParser(description="Semantic Scholar citation graph")
    ap.add_argument("arxiv_id")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--direction", default="both", choices=["both", "references", "citations"])
    ap.add_argument("--filter", default="", help="逗号分隔关键词，命中任一才保留")
    args = ap.parse_args()
    keywords = [k.strip() for k in args.filter.split(",") if k.strip()]

    opener = build_opener()
    seen = {args.arxiv_id}

    for dir_name, label in [("references", "根源(向后)"), ("citations", "演进(向前)")]:
        if args.direction not in (dir_name, "both"):
            continue
        print(f"\n{'=' * 60}\n### {label}\n{'=' * 60}")
        frontier = [args.arxiv_id]
        for depth in range(1, args.depth + 1):
            nxt = []
            for pid in frontier:
                papers = get_papers(opener, pid, dir_name)
                for p in papers:
                    if p["id"] in seen:
                        continue
                    seen.add(p["id"])
                    nxt.append(p["id"])
                    if matches(p, keywords):
                        tag = f"[d{depth}]"
                        print(f"  {tag} {p['year'] or '----'} | {p['title'][:110]}")
                        if p["abstract"]:
                            print(f"         {re.sub(chr(10) + '+', ' ', p['abstract'])[:180]}")
                time.sleep(SLEEP)
            frontier = nxt
            if not nxt:
                print(f"    （深度 {depth} 无新节点，停止）")
                break
            time.sleep(1)

    print("\n提示：上面标记 [dN] = 距离锚点的引用层数。")
    print("下一步：把保留节点按年份排序成时间线，标注每篇'解决什么问题/新增什么'。")


if __name__ == "__main__":
    main()
