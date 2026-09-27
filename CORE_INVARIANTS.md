# 核心使命不变量 (CORE_INVARIANTS.md)

> **版本**：1.0.0-PROD  
> **生效范围**：`skill-github-asset-hunter` 技能全域  
> **主权属性**：本文件为智能体特种技能**刚性契约**，任何 AI 节点在执行本技能时必须 100% 遵守以下规则。

---

## 🏛️ 不变量一：零幻觉链接不变量 (Zero-Hallucination Link Invariant)
1. 严禁向用户交付未经网络真实性核验的推测性链接；
2. 所有下载超链接必须真实存在于 GitHub Releases API 资产列表中，且必须带有直接下载能力（`browser_download_url`）。

---

## ⚡ 不变量二：结果导向直达不变量 (Direct Outcome Invariant)
1. 用户的核心诉求是“获取可执行的安装资产”，而非听大模型科普软件的历史和原理；
2. 交付成果必须优先呈现包含：软件名、版本号、硬件架构（ARM64/x64）、文件大小（MB）、直接下载链接的高密结构化表格。

---

## 🛡️ 不变量三：凭证绝对隔离不变量 (Secret Isolation Invariant)
1. 任何 GitHub Personal Access Token 严禁硬编码入库；
2. 仅允许使用环境变量 `GITHUB_TOKEN` 注入。

---

## 🧭 不变量四：三工具协同不变量 (Three-Tool Synergy Invariant)
1. 技能必须严格编排底层三工具（`tool-omniscout-radar` ➔ `tool-token-distiller` ➔ `tool-citation-optima`）；
2. 坚决杜绝脱离工具链的闭门臆造。
