# 工具使用

下列命令从本 skill 目录运行。其他工作目录调用时，把脚本和输入路径写成绝对路径。

## 安装与自检

```bash
npm ci
python -m pip install -r requirements.txt
npm run doctor
```

需要 Node.js 20.18+、Python 3.10+。已有 PyMuPDF 时无需重复安装。可通过 `PYTHON` 环境变量指定自检和演示使用的 Python 可执行文件。

## 创建阅读目录

```bash
node scripts/init-study.cjs --out paper-readings/my-paper --title "论文名称" --paper "paper.pdf"
```

生成十节结构的 `reading.md`、`assets/` 与空 `notes.json`；这是待填写的草稿，不会自动读论文。已存在的目录不会覆盖。

## 提取全文与页面

```bash
python scripts/pdf_tools.py extract paper.pdf --out paper-readings/my-paper/source
python scripts/pdf_tools.py extract paper.pdf --out paper-readings/my-paper/selected --pages 1,3-5 --render --images
```

输出 `text.md`、`source.json`，可选输出完整页面 PNG 和嵌入图片。页码从1开始；JSON保留页码、页面大小、文字块位置与PDF哈希。

`--images` 仅导出PDF里的嵌入图片，不能完整还原矢量图或由多张图拼成的版面。阅读公式、表格和复杂图时用 `--render` 看原页，或裁剪区域。扫描件可能无文字层，本工具会提示稀疏页面，不自带OCR。

## 裁剪原图或表格

```bash
python scripts/pdf_tools.py crop paper.pdf --page 3 --rect 70 80 540 350 --out paper-readings/my-paper/assets/fig1.png
```

坐标单位是PDF point，顺序为左、上、右、下，必须根据实际页面定位。当前坐标裁剪要求页面自身rotation为0；不要猜矩形。查看 `source.json` 中页面大小、文字块及页面PNG辅助定位。

## 生成HTML

按 [content-format.md](content-format.md) 填写阅读稿后运行：

```bash
node scripts/render-reading.cjs paper-readings/my-paper/reading.md paper-readings/my-paper/reading.html
```

图片和公式字体嵌入单个HTML，支持目录、四种配色、公式、流程卡片、折叠解释与原文位置开关。HTML文件名已存在时拒绝覆盖，请选新文件名或自行管理旧版本。

公式讲义也使用相同Markdown头部与渲染命令，可独立生成 `equations.md` / `equations.html`。本版没有独立的讲义转PDF命令。

## 中文PDF批注

先写 `notes.json`：

```json
{
  "annotations": [
    {
      "page": 4,
      "quote": "A short unique quote from the actual page.",
      "kind": "explain",
      "comment": "这一句的中文解释，讲清具体操作与作用。"
    }
  ]
}
```

`kind` 可以是 `explain`（黄色解释）、`notice`（蓝色注意）或 `question`（红色疑问）。`quote` 必须在指定页找到，默认只接受唯一短句；重复短句可以提供 `occurrence: 2` 指定第二处。重复的跨行短句应改成更长的唯一短句，或使用明确坐标。

需要坐标定位时，用 `"rect": [70, 100, 500, 140]` 替代 `quote`，不要同时提供两者。坐标批注要求页面rotation为0。

```bash
python scripts/pdf_tools.py annotate paper.pdf --notes paper-readings/my-paper/notes.json --out paper-readings/my-paper/annotated.pdf
```

生成高亮及弹窗批注，并默认追加可直接阅读的中文说明页；另输出 `annotated.annotations.json` 对应记录。所有短句先校验，找不到或有歧义就报出具体问题，不把批注随意放到页边。原始PDF保留。

只要弹窗高亮、不要追加说明页时加 `--no-notes-pages`。弹窗显示取决于PDF阅读器，说明页内容不依赖弹窗支持。

## 运行完整演示

```bash
npm run demo
```

在 `outputs/demo/` 生成离线阅读页、虚构教学PDF、带中文批注PDF和预览PNG。演示讲解“物体位移与关节动作的区别”，不冒充真实论文实验。重复运行时选择新目录：

```bash
npm run demo -- --out outputs/demo-2
```

## 打包

```bash
npm run pack:skill
```

输出 `dist/ai-paper-study/`、逐文件SHA-256清单，系统有tar时同时生成 `.tar.gz`。安装包包含运行工具、示例和来源许可，不含node_modules、测试、用户论文或阅读产物。复制到另一台机器后安装依赖再运行 `npm run doctor`。`npm test` 和打包命令用于源码仓库。
