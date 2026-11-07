# -*- coding: utf-8 -*-
"""Seedance 首尾帧视频生成：提交 / 轮询 / 下载，只用标准库。

用法：
  python seedance.py --prompt 03-prompts/shot01.txt \
      --first 02-frames/shot01_first.png --last 02-frames/shot01_last.png \
      --duration 5 --resolution 720p --out 04-videos

  # 已有任务 ID，查询状态：
  python seedance.py --task <task_id>

环境变量：ARK_API_KEY（必填，不要打印到日志）
模型：doubao-seedance-2-0-mini-260615（约 ¥0.5/秒）默认
      doubao-seedance-2-5-260628（约 ¥1.5/秒）用 --model 切换
"""
import argparse
import base64
import json
import mimetypes
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

BASE = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"


def api_key():
    key = os.environ.get("ARK_API_KEY", "")
    if not key:
        sys.exit("ARK_API_KEY 未设置")
    return key


def request(method, url, payload=None, timeout=60):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + api_key())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit("HTTP %s: %s" % (e.code, body))


def image_content(path_or_url):
    """http(s) 地址直接用；本地文件转 base64 data URL。"""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return {"type": "image_url", "image_url": {"url": path_or_url}}
    p = pathlib.Path(path_or_url)
    if not p.exists():
        sys.exit("图片不存在: %s" % p)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": "data:%s;base64,%s" % (mime, b64)}}


def load_prompt(text):
    p = pathlib.Path(text)
    return p.read_text(encoding="utf-8") if p.exists() else text


def submit(args):
    prompt = load_prompt(args.prompt)
    payload = {
        "model": args.model,
        "content": [
            {"type": "text", "text": prompt},
            image_content(args.first),
            image_content(args.last),
        ],
        "parameters": {
            "resolution": args.resolution,
            "ratio": args.ratio,
            "duration": str(args.duration),
            "watermark": False,
        },
    }
    if args.seed is not None:
        payload["parameters"]["seed"] = args.seed
    resp = request("POST", BASE, payload)
    task_id = resp.get("id")
    print("已提交: %s" % task_id)
    print("参考花费: %s 约 ¥%.1f/秒 x %ss = ¥%.1f" % (
        args.model,
        1.5 if "2-5" in args.model else 0.5,
        args.duration,
        (1.5 if "2-5" in args.model else 0.5) * args.duration,
    ))
    return task_id


def poll(task_id, interval=10, timeout=1800):
    url = "%s/%s" % (BASE, task_id)
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = request("GET", url)
        status = resp.get("status")
        print("状态: %s" % status)
        if status == "succeeded":
            return resp
        if status == "failed":
            sys.exit("生成失败: %s" % json.dumps(resp.get("error"), ensure_ascii=False))
        time.sleep(interval)
    sys.exit("轮询超时（%ss），任务 %s 还在跑，稍后用 --task 查询" % (timeout, task_id))


def download(task_id, resp, out_dir):
    video_url = None
    content = resp.get("content") or {}
    if isinstance(content, dict):
        video_url = content.get("video_url")
    if not video_url:
        sys.exit("任务完成但没拿到 video_url: %s" % json.dumps(resp, ensure_ascii=False)[:500])
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / ("%s.mp4" % task_id)
    urllib.request.urlretrieve(video_url, dest)
    print("已下载: %s" % dest.resolve())
    return dest


def main():
    ap = argparse.ArgumentParser(description="Seedance 首尾帧视频生成")
    ap.add_argument("--prompt", help="提示词文件路径或直接文本")
    ap.add_argument("--first", help="首帧图片（本地路径或 URL）")
    ap.add_argument("--last", help="尾帧图片（本地路径或 URL）")
    ap.add_argument("--duration", type=int, default=5, help="秒数，默认 5")
    ap.add_argument("--resolution", default="720p", choices=["480p", "720p", "1080p"])
    ap.add_argument("--ratio", default="16:9")
    ap.add_argument("--model", default="doubao-seedance-2-0-mini-260615")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default="04-videos", help="下载目录")
    ap.add_argument("--task", help="已有任务 ID：只查询/下载")
    ap.add_argument("--interval", type=int, default=10)
    args = ap.parse_args()

    if args.task:
        resp = poll(args.task, args.interval)
        download(args.task, resp, args.out)
        return
    if not (args.prompt and args.first and args.last):
        sys.exit("需要 --prompt --first --last，或用 --task 查询已有任务")
    task_id = submit(args)
    resp = poll(task_id, args.interval)
    download(task_id, resp, args.out)


if __name__ == "__main__":
    main()
