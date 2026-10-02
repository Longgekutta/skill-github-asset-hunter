# skill-github-asset-hunter
### 智能体全网开源软件与直接安装资产（APK/EXE/DMG）极速嗅探直达特种技能
**AI Agent Specialized Capability for Instant Open-Source Release Discovery & Direct Asset Extraction**

[![Type: Agent Skill](https://img.shields.io/badge/Type-Agent%20Skill-blueviolet.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Host: Antigravity / Claude Code](https://img.shields.io/badge/Host-Antigravity%20%7C%20Claude%20Code-orange.svg)](#)
[![Zero-Hallucination: Guaranteed](https://img.shields.io/badge/Zero--Hallucination-100%25%20Verified-brightgreen.svg)](#)

---

## 💡 什么是 Agent Skill？它在 GitHub 上的生态位是什么？

在现代 AI Agent 架构体系中，**Skill（智能体技能）并不是一个常规意义上的独立桌面应用程序，而是 AI 智能体的“特种作战作业规程与工具编排范式”**：

* **传统 Project（项目）的痛点**：如果仅写一段 Python 代码把几个工具拼起来，缺少了 AI 的意图理解与泛化能力，面对千变万化的口语化搜索诉求就会极其死板；
* **Skill 的降维威力**：它以 Git 仓库为载体，在根目录定义 `SKILL.md`（包含机器可读的 YAML Frontmatter 与人类可读的严格 SOP），并配备执行脚本（`scripts/`）。当宿主 AI 识别到相关意图时，**自动将这套技能加载进注意力上下文，直接掌握全网寻优与直链生成的专业操作法**！

---

## 🏛️ 技术思想溯源与全球对标矩阵 (World-Class Heritage & Prior Art)

本项目秉承第一性原理与零幻觉工程原则，严格站在全球工业标杆与开源先验的肩膀上演进构建。

完整权威源流矩阵（收录 3 项基础标杆工具链）、深度机制对标、吸收借鉴点与取舍论证详见专精档案：
👉 **[完整先验对标与权威引用档案 (references/prior_art.md)](references/prior_art.md)**

*(注：机器可读元数据与规范引用已同步至 `.provenance.json` 与 `CITATION.cff`)*

---

## 🚫 明确不做的事 (Non-Goals)

1. **坚决不做独立重型套壳 CLI**：本项目定位于 Agent 的专精工作法（Skill），拒绝为了做项目而做项目；
2. **坚决不输出任何推测性或死链**：所有交付链接必须通过 `scripts/asset_extractor.py` 进行物理探活；
3. **坚决不返回无下载意义的纯代码仓库**：若候选仓库未发布任何 Binary/Asset，直接在初筛阶段淘汰。

---

## 🚀 技能安装与配置指南 (Installation)

### 方式 A：在 Antigravity 全局技能库中加载（推荐）
直接克隆或复制本仓库到您的全局配置目录：
```powershell
# 复制到全局自定义技能目录
mkdir C:\Users\28461\.gemini\config\skills\skill-github-asset-hunter -Force
Copy-Item D:\github\skill-github-asset-hunter\* C:\Users\28461\.gemini\config\skills\skill-github-asset-hunter\ -Recurse -Force
```
安装后，AI 智能体将在启动时自动发现并注册 `skill-github-asset-hunter`。

### 方式 B：作为项目级局部技能
直接将本仓库作为子模块检入任何项目的 `.agents/skills/skill-github-asset-hunter/` 目录下。

---

## ⚡ 触发与使用示例 (Usage Examples)

用户只需在对话中用自然语言提出诉求，AI 自动调动本技能：

* **Query 1**：“给我找一个安卓上好用的 SSH 客户端 APK”
* **Query 2**：“Windows 上有什么好用的开源串口调试工具？直接给我下载地址”
* **Query 3**：“Mac M系列芯片有什么开源剪贴板增强软件？要 arm64 架构”

AI 将跳过所有概念套话，直接交付经过架构评分的**软件名 + 版本号 + 文件大小 + 架构标识 + 点击直接下载真实超链接**。

---

## 📄 规范附录
* 核心操作 SOP 详见：`SKILL.md`
* 核心不变量声明详见：`CORE_INVARIANTS.md`
* 机器可读元数据与技术审计详见：`.provenance.json`
