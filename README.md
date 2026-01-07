# garmin-to-notion-CN
# Garmin to Notion Sync (CN Enhanced Ver.) 🇨🇳

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Notion](https://img.shields.io/badge/Notion-API-black) ![License](https://img.shields.io/badge/License-MIT-green)

本项目是一个全自动化的健康数据看板后端，能够将你的 **Garmin (佳明)** 运动手表数据实时同步到 **Notion** 数据库中。

> ⚠️ **致谢 / Credits**
>
> 本项目基于 **[chloevoyer/garmin-to-notion](https://github.com/chloevoyer/garmin-to-notion)** 原版开发。
> 在原作者优秀工作的基础上，我进行了**全中文汉化**、**中国区服务器适配**以及**核心功能的增强**。

---

## ✨ 主要特性 (Features)

### 1. 全中文适配 🇨🇳
- **属性汉化**：所有 Notion 数据库字段（如步数、睡眠、配速、功率等）均已适配为中文，无需再对照英文词典。
- **运动类型汉化**：自动将 `Running` 转换为 `跑步`，`Cycling` 转换为 `骑行` 等，更符合中文直觉。
- **中国区加速**：针对 Garmin 中国区服务器（CN）进行了连接优化，解决数据同步不稳定的问题。

### 2. 独家功能：历史数据“时光机” (Manual Backfill) 🚀
**这是本项目独有的增强功能。**
不同于原版仅支持“当日同步”，本项目内置了一个**手动回填脚本**。
- **拒绝空白**：刚配置好不再是空荡荡的看板，一键拉取过去 **30天至1年** 的历史数据。
- **智能补全**：自动抓取过去的睡眠记录、每日步数以及最近的 **1200条** 运动记录。
- **手动开关**：通过 GitHub Actions 手动触发，安全可控，不影响日常自动更新。

### 3. 自动化零感同步
- 配置完成后，每天凌晨自动运行，当你醒来时，昨天的健康数据已经安静地躺在 Notion 里了。

---

## 🛠 使用指南 (Quick Start)

*(详细的图文配置教程，请参考随附的 Notion 模板说明文档)*

### 简要步骤：
1. **Fork 本仓库**：点击右上角的 Fork 按钮。
2. **配置 Secrets**：在仓库的 `Settings` -> `Secrets` 中填入你的 Garmin 账号密码及 Notion Token。
3. **一键初始化**：
   - 进入 `Actions` 页面。
   - 选择 **Manual History Backfill (手动回填历史)**。
   - 点击 `Run workflow`，等待片刻，你的 Notion 将被填满历史数据。
4. **享受自动同步**：此后，`Sync Garmin to Notion` 脚本将每天自动为你更新数据。

---

## 📝 环境变量说明

| Secret Name | 描述 |
| --- | --- |
| `GARMIN_EMAIL` | 佳明账号邮箱 |
| `GARMIN_PASSWORD` | 佳明账号密码 |
| `NOTION_TOKEN` | Notion Integration Token |
| `NOTION_CN_DB_ID` | 运动记录数据库 ID |
| `NOTION_CN_STEPS_DB_ID` | 每日步数数据库 ID |
| `NOTION_CN_SLEEP_DB_ID` | 睡眠监测数据库 ID |
| `NOTION_CN_PR_DB_ID` | 个人最佳纪录 (PR) 数据库 ID |

---

## ⚖️ 许可证 (License)

本项目遵循 **MIT License** 开源协议。
Original work Copyright (c) 2024 chloevoyer.
Modified work Copyright (c) 2026 [perinchiang]p.
