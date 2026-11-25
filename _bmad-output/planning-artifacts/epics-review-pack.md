---
title: LabBooking Epics / Stories 三方审核包
status: draft
owner: B
created: 2026-11-22
updated: 2026-11-25
baselineCommit: b97ec56d6d4d832abcdbcdbd4c987082ed750725
reviewStatus: pending
---

# LabBooking Epics / Stories 三方审核包

当前为**4个Epic、21个Story、98条AC、15 FR＋3 NFR的逐项设计追溯、11项开发准备清单**。三方已完成首轮文档评审，B于2026-11-25按意见修订并补Decision Log，修订待复核；未进入业务实现，不宣称依赖安装/环境复现/迁移/功能或NFR实测通过。

## 建议阅读顺序

1. [epics.md](epics.md)：先看基线、Epic列表和覆盖表，再读各Story范围/AC及依赖表。
2. [requirements-traceability.md](requirements-traceability.md)：18条需求到具体Story/AC、架构附加要求、18个既定Route与授权配对。
3. [development-readiness.md](development-readiness.md)：DP-01～11及版本/scrypt/运行配置登记、测试前门槛、B拟定输入规则。
4. [decision-log.md](decision-log.md#epics-review-2026-11-25)：本阶段D-039～D-045及证据、取舍与状态，原日志只追加。
5. 本文件：三方真实意见、逐项处理及文档检查结果。

## 基线与证据

- 仓库：doublej1943/lab-equipment-booking；main基线`b97ec56d6d4d832abcdbcdbd4c987082ed750725`，来自[已合并PR #3](https://github.com/doublej1943/lab-equipment-booking/pull/3)。首轮被审阅初稿为`3515fc14c4abef6b4dc50664209fc918ddf94bb4`。本轮不改PRD、Architecture/Spine/Context/memlog的批准设计，仅在既有Decision Log末尾追加阶段记录，不改旧决策/附录。
- [B最终复核](https://github.com/doublej1943/lab-equipment-booking/pull/3#issuecomment-6998315969)：支持Epic/Story拆分，环境、版本与资源配置留后续落实；不代表实现/NFR已通过。
- [C测试可行性结论](https://github.com/doublej1943/lab-equipment-booking/pull/3#issuecomment-6968206184)：支持拆分，时间/并发原因/未知结果故障/NFR-02配置/实验A执行准备纳入任务；原文及后续架构补充为本稿来源。
- 原PRD/Architecture历史draft及课程假设保留。按用户提供的Architecture已完成交接开展本稿，不据旧标记重新修改批准设计，也不把合并当作代码或实测验收。

## 审核分工与判定

| 审核者 | 要回答的问题 | 优先位置 | 本轮状态 |
| --- | --- | --- | --- |
| 需求负责人 | 15FR/3NFR覆盖、业务一致性、UJ/SM及合成资料边界 | 逐项追溯、Story AC、DP-03/08/10 | 已有条件认可拆分方向；本轮修订待复核 |
| A | 已批准架构的一致性，分页和异常分类歧义 | 3.3-AC3、3.4-AC2、3.7-AC4及原约束 | 已完成首轮架构审查、未发现需重设架构；两项修改待复核 |
| C | 测试/端到端可执行性、真实时间/故障及NFR证据 | 3.6～3.8、4.4/4.5、DP-05/07/09/10/11 | 已有条件认可并同意继续开发准备；本轮修订待复核 |
| B | 统一修订与决策补录，随后落实实现/环境/测试支持 | 五份文档及后续代码 | 文档修订已准备，实施待开展 |

上述结论按真实评论原文记录，GitHub正式Review记录为COMMENTED，不改写成APPROVED。修订待原审核者复核，行内线程不由本稿宣称已关闭；文档认可不替代开发、C执行结果或系统验收。

## PR #4 真实评审与逐项处理（2026-11-25）

三方意见发生于2026-11-23（Asia/Shanghai），本次补录不倒填为2026-11-22。以下“已修订”只指文档修改，不代表审核者已复核或对应测试已通过。

| 项目/来源 | B本轮处理与位置 | 状态/后续门槛 |
| --- | --- | --- |
| R-01：[需求负责人第1项](https://github.com/doublej1943/lab-equipment-booking/pull/4#issuecomment-7081800080)、[C追溯意见](https://github.com/doublej1943/lab-equipment-booking/pull/4#discussion_r4662609525) | 追溯表补UJ-1～4、SM-01～03及E2E-01～06；4.5删除把SM-02当性能指标的错误关联，4.4-AC5承接核心流程回归；D-042 | 已修订，待复核/执行计划冻结 |
| R-02：[需求负责人第2项](https://github.com/doublej1943/lab-equipment-booking/pull/4#issuecomment-7081800080)、[C未知结果意见](https://github.com/doublej1943/lab-equipment-booking/pull/4#discussion_r4662616250) | 3.7-AC2/3及DP-07明确“尚未确认”、现有本人列表/详情GET、实际已提交状态核查、禁止自动重发/引导重复操作；D-043 | 已修订，真实故障与UI验证待执行 |
| R-03：[需求负责人第3项](https://github.com/doublej1943/lab-equipment-booking/pull/4#issuecomment-7081800080) | 优先级建议改为先完成登录到本人取消的3.1～3.5核心闭环，管理/NFR/实验A保留容量，硬依赖和验收范围保持；D-039 | 已修订，Sprint容量/排期仍待Planning |
| R-04：[需求负责人第4项](https://github.com/doublej1943/lab-equipment-booking/pull/4#issuecomment-7081800080) | DP-03明确课程演示/一般开发/自动化可用符合约束的合成资料，仅真实导入需要私有真实资料；D-045 | 使用边界已澄清，合成数据/工具待实现 |
| R-05：[需求负责人第5项](https://github.com/doublej1943/lab-equipment-booking/pull/4#issuecomment-7081800080) | 3.5-AC4及DP-04明确Booking共八字段、取消只改status、其余七不变；核对既有字段契约，不新增独立架构决策 | 已修订，待复核 |
| R-06：[A第1项](https://github.com/doublej1943/lab-equipment-booking/pull/4#issuecomment-7092039611) | 3.4-AC2明确page无100上限、仅page_size为1～100；page=101仍是合法页；D-040 | 已修订，待A/C复核 |
| R-07：[A第2项](https://github.com/doublej1943/lab-equipment-booking/pull/4#issuecomment-7092039611) | 3.3-AC3、3.7-AC4和DP-07将D-015限定收窄为数据库异常转换，允许业务冲突预检查，最终唯一性不变；D-041 | 已修订，待A/C复核 |
| R-08：[C时间意见](https://github.com/doublej1943/lab-equipment-booking/pull/4#discussion_r4662618779) | 新增3.6-AC9正向验证时间资格已满足、后续提交跨开始不被新增截止拒绝；DP-07/追溯同步；D-044 | 已修订，两层时间/真实PG证据待执行 |
| R-09：[C性能口径意见](https://github.com/doublej1943/lab-equipment-booking/pull/4#discussion_r4662621179) | 保留4.5及DP-09/10正式前冻结、完整响应/本人区、全部样本/正确性、任一错误失败，不填未经实测数值 | 原要求保留，计划/环境/执行待落实 |
| R-10：[C逐入口授权意见](https://github.com/doublej1943/lab-equipment-booking/pull/4#discussion_r4662627373) | 4.4-AC5及DP-10逐入口列身份/目标/CSRF/HTTP/数据变化，保留合法配对和CSRF分测 | 已细化，实际矩阵/执行待C完成 |
| R-11：[C故障证据意见](https://github.com/doublej1943/lab-equipment-booking/pull/4#discussion_r4662629976) | 保留3.7-AC5真实与模拟证据分离；DP-07由B/C尽早落实注入机制，真实确认丢失未执行不关闭AC | 执行准备待落实，不以文档更新宣称通过 |
| R-12：[C总评第4～7项](https://github.com/doublej1943/lab-equipment-booking/pull/4#issuecomment-7093949538)、A其他事项 | 保留NFR-01逐请求/轮次/终态1/19/1、NFR-02/03、DP-05历史迁移及DP-11实验A；DP-08仍待确认，A/C在实验前确认方案 | 原门槛保留；未改数值、未虚构版本/迁移/实验结果 |

本轮D-039～D-045记录阶段取舍/人工作用及证据；原架构约束的重申与文本核对不重复计为新架构决定，课程AI否决/修改数量不因本表自动增加。

## 三方重点关注

1. **范围及粒度**：技术准备放在1.1/1.2/3.1支撑用户能力，实体按首次需要引入；完整预约流程放在E3，管理查询留E4，避免按前后端技术层拆Epic。21项是可分配工作单元，3.6/3.7/3.8等证据复杂度需B/C评估；如超出一次实现/验证的容量，可在同一Story下细分任务，保留AC和依赖，不拆散协议。
2. **独立可交付**：1.3可利用既定GET /login已有登录状态分支独立验证，1.5再把完整登录落点接入/devices；2.2/2.3先验证设备端，Booking引入后的联动验收归3.4/3.6。跨阶段回归不是前一Story运行的硬依赖；功能的整项FR以所有相关AC完成判定。
3. **实施细节建议**：DP-08给出page/page_size空串/重复、日期/筛选名称及格式等B拟定规则，供三方检查；这类事项已由架构委托B落实，不回写成A已批准的新业务要求。无新增字段/状态/模块、账号/设备字符白名单或对外JSON API。
4. **NFR资源与口径**：DP-09/10是正式执行门槛，不预填线程/池/超时值。NFR-01不是“没有双重预约即通过”；NFR-02不删除失败样本；NFR-03必须合法/禁止配对且CSRF单独测。保持课程既定规模与阈值。
5. **真实故障证据**：3.7保留创建/取消确定回滚与提交确认丢失四类场景。仅提交后抛应用异常不能充真实确认丢失；缺实际机制/证据时保持对应AC待验证。建议B/C尽早做方法可行性验证。
6. **资料及课程衔接**：课程演示和自动测试可使用符合约束的合成资料；只有按需真实导入的账号/phone/设备编号兼容检查受DP-03私有资料约束。实验A由C形成独立计划、A确认架构/BMAD边界、B支持，DP-11不冒充第19条产品需求，也不增加实验B。

## 开发与正式测试前仍须关闭的事项

精确补丁/传递依赖及前端资源版本、scrypt具体参数、干净Windows/Conda复现、User/Device/Booking约束表达与命名、权限与迁移恢复、时间/竞争/真实确认丢失方法、运行预算/分项超时及NFR测试计划均未完成。每项负责人、证据与对应Story门槛已放入DP清单，不阻断本次待审核初稿交付。

原仓库无业务代码或迁移，本稿不虚构既有V1/V2或测试文件。V1→V2的历史保留目标按实际后续revision验证；环境、迁移和NFR均应保留独立执行证据。

## 本轮文档检查记录

2026-11-22初稿校核为97条AC、65处本地链接/锚点、四份新增Markdown。2026-11-25修订新增3.6-AC9并补阶段日志，按源PRD/Architecture及旧日志基线重新校核；下表为修订后检查项目与结果。这些是文档检查，不是产品功能/NFR测试、BMAD独立Reviewer Gate或团队批准。

| 检查 | 实际结果 |
| --- | --- |
| 从PRD标题提取需求，与逐项追溯集合比较 | 15FR＋3NFR，18/18逐项对应，无重复/遗漏 |
| Epic/Story结构与必需字段 | 4个Epic、21个唯一Story；每条均有用户价值、范围、需求/架构、依赖与GWT验收 |
| AC编号/引用及GWT结构 | 98条唯一AC；显式引用有效，所有AC均含Given/When/Then |
| Story正文与依赖表一致性、前向引用及有向图 | 27条依赖；表/正文一致，无环，均指向前置Story |
| 与Architecture正式Route表逐项比较 | 18/18相同且均有Story归属 |
| 开发准备条目 | DP-01～11共11项，责任/门槛/当前未落实状态已列 |
| 用户旅程/成功指标/端到端追溯 | UJ-1～4、SM-01～03和E2E-01～06均有现有Story/AC落点 |
| 阶段日志编号与历史保护 | 新增D-039～D-045七项，D-001～D-038及原附录按原文保留 |
| 本地文件链接及显式锚点 | 四份规划文档与日志新增部分共78处有效；9条评审评论永久链接与已读取PR证据对应 |
| UTF-8、隐藏/替换字符、模板残留、代码围栏 | 未发现异常；Route中的id占位使用代码格式避免被当HTML |
| Git差异范围及空白 | 相对首轮仅修订四份规划文件并追加Decision Log；PRD及其余架构文件未修改，diff空白检查通过 |

本稿按仓库bmad-create-epics-and-stories的提取→Epic→Story→校核顺序组织。依用户一次完成“待审核初稿”的要求，中间菜单未另行打断用户；未将其视为需求/Epic/Story已获批准，frontmatter保持draft和reviewStatus: pending，stepsCompleted只表示编制/文档校核步骤完成。

## 审核反馈模板

```text
审核角色：A / 需求负责人 / C
审阅分支与提交：
已审阅文件/章节：
结论：通过 / 有条件通过 / 需修改
问题位置：Story编号-AC编号 / FR或NFR / DP编号
问题与影响：
建议的最小修改：
是否阻断对应Story或正式测试，及关闭证据：
```

三方首轮反馈已收集并按上表修订；修订复核及适用DP门槛满足后再确定Sprint排期。保留draft/pending状态，不将首轮评论中的有条件认可当作修订已通过或实现已开始。

## 本轮交付位置

交付分支为`docs/epics-stories-draft`，PR #4现交付四份规划Markdown及更新后的Decision Log；审阅以PR最新head为准。需求及架构基线仍为b97ec56，首轮被审阅版本3515fc1用于保留修改前证据。

初次远程发布遇到GitHub连接403“Resource not accessible by integration”及本机Git缺少凭据。本次已由用户完成Git Credential Manager授权，本机认证账号确认为YANJIE-C，仓库API的push权限为true，具备推送权限。该连接限制不代表YANJIE-C缺少仓库写权限。

本地文件可直接审核；此前ZIP是初稿生成时的快照，后续审核以分支/PR中五份文件为准。版本/参数/环境和正式验证仍按DP清单待办，不因登录或推送成功而变更其状态。
