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

## 🧭 不变量四：权责边界与零越权不变量 (Boundary & Zero-Overreach Invariant)
1. **负向清单约束**：本技能严守“只读探测与安装资产交付”边界，严禁在执行中创建、修改用户项目文件或执行任何越权写操作；
2. **红线之上绝对自主**：在零幻觉、零死链的负向红线之上，智能体拥有自主调度探测与提纯的最优自主权，坚决杜绝形式主义空转。
