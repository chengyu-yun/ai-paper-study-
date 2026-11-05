# 复用来源

本项目借鉴并复用 [Xiaofeng Shi 的 paper-reading-skill](https://github.com/xiaofengShi/paper-reading-skill) 中的 HTML 渲染部分。

- 复用文件：`scripts/render-reading.cjs`、`scripts/lib/offline-assets.cjs`、`scripts/lib/reading-markdown.cjs`、`assets/reading.css`。
- 上游许可证为 MIT，原始版权与许可全文保留在 [licenses/paper-reading-MIT.txt](licenses/paper-reading-MIT.txt)。
- 复用快照来自本机已安装的上游副本；没有可用的 Git commit 信息。逐文件 SHA-256 记录在 [licenses/upstream-files.json](licenses/upstream-files.json)。后续本地适配会保留这份原始指纹。
- 本项目的讲解风格、十项阅读结构、PDF 提取/批注工具、项目初始化、命令文档和示例围绕 AI Paper Study 另行组织。

Node 依赖 `marked`、`katex` 与 Python 依赖 `PyMuPDF` 通过包管理器安装，没有将这些依赖源码打包进发布文件。各依赖使用其自身许可证。
