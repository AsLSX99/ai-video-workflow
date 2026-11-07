# -*- coding: utf-8 -*-
"""环境自检：codex / ffmpeg / Python / ARK_API_KEY。全过输出 PASS，有缺列出补齐方法。"""
import shutil
import subprocess
import sys

results = []


def check(name, ok, fix):
    results.append((name, ok, fix))


# Python
check("Python >= 3.9", sys.version_info >= (3, 9), "安装 Python 3.9+ 并加入 PATH")

# codex
codex = shutil.which("codex")
if codex:
    try:
        out = subprocess.run(["codex", "--version"], capture_output=True, text=True, timeout=30)
        ver = (out.stdout or out.stderr).strip().splitlines()[0]
    except Exception:
        ver = "版本未知"
    check("codex (%s)" % ver, True, "")
else:
    check("codex", False, "npm install -g @openai/codex 后 codex login")

# ffmpeg
ffmpeg = shutil.which("ffmpeg")
if ffmpeg:
    try:
        out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=30)
        ver = out.stdout.splitlines()[0].split()[2]
    except Exception:
        ver = "版本未知"
    check("ffmpeg (%s)" % ver, True, "")
else:
    check("ffmpeg", False, "winget install Gyan.FFmpeg 或把 ffmpeg 加入 PATH（后期拼接必需）")

# ARK_API_KEY
import os
key = os.environ.get("ARK_API_KEY", "")
check("ARK_API_KEY", bool(key), "注册火山引擎 → 火山方舟 → API Key → setx ARK_API_KEY \"你的key\"（重开终端生效）")

print("=" * 46)
for name, ok, fix in results:
    mark = "[OK]  " if ok else "[MISS]"
    line = "%s %s" % (mark, name)
    if not ok and fix:
        line += "  ->  " + fix
    print(line)
print("=" * 46)
all_ok = all(ok for _, ok, _ in results)
print("PASS，可以开工" if all_ok else "有缺项，先补齐再开工")
sys.exit(0 if all_ok else 1)
