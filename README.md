# ai-video-workflow

用 Codex + Seedance 从一个想法做出完整 AI 视频的八步全流程（Finch Skill）。

方法源自 Eian 的实战文章：[Claude code/Codex+Seedance AI视频：从一个想法到成片的全流程](https://x.com/EianLu/article/2118317430665613741)。本仓库把总导演换成 Codex——写故事、写提示词、画设定图与首尾帧、写后期代码，一个入口全包，不依赖 Claude。

## 流程

想法 → 剧情（5 条标准 + 独立审核）→ 分镜（构图/机位/配色）→ 画风与设定图 → 首尾帧（8 项检查）→ 七段式视频提示词（提交前独立审核）→ Seedance 生成 → ffmpeg 后期 → 全片复核。

核心原则：**能把错误挡在花钱之前**——文字里能发现的错不留到图上，图上能发现的错不留到视频上。

## 目录

```
SKILL.md                 # 主文档：八步流程、分工、铁律
templates/00–09           # 10 个提示词模板，填方括号即发
references/
  pitfall-table.md        # 模型 20 条易错点对照表
  roles.md                # 分工表与四线程角色
scripts/
  env_check.py            # 环境自检：codex / ffmpeg / Python / ARK_API_KEY
  seedance.py             # Seedance 首尾帧生成：提交 / 轮询 / 下载（纯标准库）
```

## 使用

1. 安装为 Finch skill：把本目录放到 `<项目>/.finch/skills/ai-video-workflow/`
2. 环境准备：`codex`、`ffmpeg`、Python ≥3.9，环境变量 `ARK_API_KEY`（火山方舟控制台申请，**不要写进任何文件**）
3. 对 Finch 说"做 AI 视频"或"Seedance 流程"即可进入八步工作流

## 安全

- 仓库不含任何 API Key / Token；`ARK_API_KEY` 只从环境变量读取，脚本不打印
- 密钥申请后用 `setx ARK_API_KEY "你的key"` 写入本机环境，切勿提交到 git

## License

方法论版权归原作者 Eian；代码部分按本仓库原样使用。
