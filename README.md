# AI Paper Study · AI 论文研读

一个面向 Codex 的 AI 论文阅读 skill。用充分详细、通俗易懂的中文，把研究问题、方法、关键公式和实验讲清楚。

先抓住论文主线，再跟着一个具体例子走完方法。适合想读懂论文、准备交流、比较方法或寻找可借鉴设计的读者。

**当前版本：0.2.0。** 包含可执行的 PDF 提取、图表裁剪、中文批注、离线 HTML 渲染、阅读初始化与打包工具。HTML 渲染部分基于 [paper-reading-skill](https://github.com/xiaofengShi/paper-reading-skill)，保留来源与 MIT 许可；阅读风格、PDF 工具及工作流在本项目扩展。

已有可打开的[教学阅读页](examples/demo/reading.html)，也可以查看对应的[Markdown源稿](examples/demo/reading.md)。这个例子专门演示讲解与排版，不冒充真实论文实验。

## 它会怎样讲论文

- 用三句话说清：作者遇到什么问题、具体改了什么、结果怎样。
- 围绕“困难 → 处理 → 为什么可能有效 → 代价”解释核心设计。
- 用一个例子追踪输入、中间表示和输出，分清训练与推理。
- 先解释公式在算什么，再展开变量、计算和结果用途。
- 结合关键图表解释实验，把重要结论定位回原文。
- 直接回应追问；读不懂时换例子、换路径，不强制答题测验。

## 阅读笔记包含什么

完整阅读按十项组织：

1. 问题定义：输入、输出、约束和评价指标。
2. 核心假设：方法有效需要哪些条件。
3. 贡献拆解：作者声称的贡献及对应证据。
4. 方法框架：模块、数据流、关键公式和完整例子。
5. 实验审查：数据、基线、指标和主要比较条件。
6. 主结果与消融：哪个改动有效，证据是否充分。
7. 局限与失败模式：作者承认的和根据方法推断的分开说明。
8. 最弱环节：最值得进一步追问的问题。
9. 可复现清单：原文提供的代码、数据、超参和成本信息。
10. 对用户任务的建议：结合具体任务给出下一步。

每节最多五个主要条目，但不压缩必要的解释。单个公式或章节的追问只回答相关内容，不重复整篇报告。

## 支持哪些输出

| 输出 | 用途 | 默认行为 |
|---|---|---|
| Markdown 阅读笔记 | 编辑、检索、后续讨论 | 完整阅读生成 |
| HTML 阅读页 | 连贯阅读，展开推导和补充解释 | 完整阅读生成 |
| 方法流程图 | 看清模块、数据流、训练与推理 | 按需要嵌入笔记和 HTML |
| 批注 PDF | 贴着原文看解释、公式和疑问 | 按用户要求生成副本 |
| 公式推导讲义 | 跟着中间步骤和数值例子理解数学 | 按用户要求独立导出 |

所有输出都围绕同一份解释组织，避免生成多份重复材料。具体要求见 [SKILL.md](SKILL.md)。

## 安装

### 下载后放入 skills 目录

1. 下载并解压本仓库。
2. 将包含 `SKILL.md` 和 `agents/` 的目录命名为 `ai-paper-study`。
3. 将该目录放入自己的 Codex skills 目录。

默认位置示例：

```text
Windows: C:\Users\你的用户名\.codex\skills\ai-paper-study\
macOS / Linux: ~/.codex/skills/ai-paper-study/
```

使用自定义 `CODEX_HOME` 时，放在该目录的 `skills/ai-paper-study/` 下。安装完成后在新的 Codex 会话里调用。

### 使用 Git

仓库发布后，把下面的 `YOUR_GITHUB_USERNAME` 替换为实际仓库所有者。

Windows PowerShell：

```powershell
git clone https://github.com/YOUR_GITHUB_USERNAME/ai-paper-study.git "$env:USERPROFILE\.codex\skills\ai-paper-study"
```

macOS / Linux：

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/ai-paper-study.git ~/.codex/skills/ai-paper-study
```

已有同名安装时，在现有目录更新，或先选择一个不同位置查看；上述 clone 适用于目标目录尚不存在的情况。

### 安装运行依赖

进入 `ai-paper-study` 目录后运行：

```bash
npm ci
python -m pip install -r requirements.txt
npm run doctor
```

需要 Node.js 20.18+ 和 Python 3.10+。已安装 PyMuPDF 的环境可以直接使用；macOS/Linux 的Python命令可能是 `python3`。自检/演示默认查找本机Python，也可设置 `PYTHON` 环境变量指定解释器。

## 怎么使用

把 PDF、章节文本或论文链接提供给 Codex，然后调用：

```text
$ai-paper-study 帮我详细读懂这篇论文。重点把方法讲清楚，先用一个例子走完整个流程，再解释公式和实验。
```

只看方法：

```text
$ai-paper-study 只解释这篇论文的方法。讲清每个模块接收什么、做了什么、交给下一步什么，并区分训练和推理。
```

批注原论文：

```text
$ai-paper-study 阅读这篇论文，并生成带中文批注的 PDF 副本，重点解释核心设计、公式和实验结论。
```

公式讲义：

```text
$ai-paper-study 把这篇论文的核心公式整理成推导讲义。补出必要中间步骤，配一个小数值例子，不要只列符号定义。
```

比较论文：

```text
$ai-paper-study 比较这两篇论文：分别解决什么问题，方法在哪些地方不同，各自什么条件下值得借鉴？
```

## 先运行一个完整演示

```bash
npm run demo
```

在 `outputs/demo/` 生成离线HTML、教学PDF、带中文批注PDF和逐页PNG预览。PDF里既有原文高亮和弹窗说明，也有直接可读的中文说明页。已有该目录时用新路径：

```bash
npm run demo -- --out outputs/demo-2
```

## 实际工具命令

以下命令从本项目目录执行，输入与输出路径按自己的文件位置修改。

```bash
# 创建十项结构的待填写阅读稿
node scripts/init-study.cjs --out paper-readings/my-paper --title "论文名称" --paper paper.pdf

# 提取带页码的全文、页面位置与源文件哈希
python scripts/pdf_tools.py extract paper.pdf --out paper-readings/my-paper/source

# 只渲染指定页，便于检查公式和图表
python scripts/pdf_tools.py extract paper.pdf --out paper-readings/my-paper/pages --pages 1,3-5 --render

# 将已写好的阅读稿生成离线HTML
node scripts/render-reading.cjs paper-readings/my-paper/reading.md paper-readings/my-paper/reading.html

# 根据 notes.json 中的页码、原文短句和中文解释生成批注副本
python scripts/pdf_tools.py annotate paper.pdf --notes paper-readings/my-paper/notes.json --out paper-readings/my-paper/annotated.pdf
```

裁图坐标、批注JSON示例和输出约定见[工具指南](references/tool-guide.md)。页面内容格式见[格式说明](references/content-format.md)。工具不会自己写论文解读：AI依据原文完成内容，脚本处理提取、定位、排版与导出。

提取脚本支持文字层和嵌入图片，不自带OCR；矢量图可通过页面渲染/裁剪获取。短句批注遇到找不到或重复文本时会提示定位问题。公式讲义可用相同渲染器输出独立HTML，本版没有专用讲义转PDF命令。

## 项目结构

```text
ai-paper-study/
├── SKILL.md           阅读方式、十项结构及输出要求
├── agents/
│   └── openai.yaml    显示名称、简介和默认调用提示
├── scripts/           HTML、PDF、自检、示例与打包命令
├── assets/            页面样式
├── templates/         十项阅读结构模板
├── references/        工具用法与内容格式
├── examples/demo/     教学阅读稿、流程图和离线页面
├── tests/             实际文件处理测试
├── licenses/          上游许可证与复用文件记录
├── THIRD_PARTY_NOTICES.md
├── package.json
├── package-lock.json
├── requirements.txt
├── LICENSE
├── README.md          项目介绍、安装与示例
└── .gitignore         本地文件和阅读产物的忽略规则
```

## 测试和打包

在源码仓库安装依赖后：

```bash
npm test
npm run pack:skill
```

测试覆盖离线渲染、公式与图片、初始化、打包校验，以及PDF页码提取、短句定位、中文批注、长说明分页和原文件保留。

打包到 `dist/ai-paper-study/`，系统可用tar时同时生成压缩包。安装包不带node_modules、用户论文、生成结果和开发测试；换机器后安装依赖即可运行。支持运行时的自检和演示，测试与打包命令属于源码仓库。

## 复用与许可

项目使用 MIT 许可。复用的上游渲染器、解析模块和样式保留原始版权及许可，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。依赖库保留各自许可证。

## 反馈

欢迎通过 GitHub Issues 反馈实际使用中哪一段没有讲清楚，并附上使用的提示词、输出片段及希望改进的解释方式。可分别提出公式解释、流程图、实验解读或输出格式方面的建议。
