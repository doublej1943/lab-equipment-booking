# LabBooking PRD Validate Report

- **PRD:** `_bmad-output/planning-artifacts/prds/prd-LabBooking-2026-11-12/prd.md`
- **Product Brief:** `_bmad-output/planning-artifacts/briefs/brief-LabBooking-2026-11-11/product-brief.md`
- **Decision Log:** `_bmad-output/planning-artifacts/decision-log.md`
- **PRD memlog:** `_bmad-output/planning-artifacts/prds/prd-LabBooking-2026-11-12/.memlog.md`
- **Rubric:** `.agents/skills/bmad-prd/assets/prd-validation-checklist.md`
- **Run at:** 2026-11-14 (Asia/Shanghai)
- **Grade:** Fair (有条件通过；无 Critical，存在 High 门槛问题)
- **本轮一致性校正：** 原汇总曾列 Medium 4；复核发现 `review-rubric.md` 已有独立的 SM-03 Medium，而原 Markdown/HTML 汇总漏列该项。本轮将汇总统一为 Medium 5；这是报告聚合修正，不是重新运行 Validate，也不表示任何问题已解决。
- **过程时间线：** PR #1 merge commit `a3fee51` 先于本报告 2026-11-14 的 BMAD PRD Validate；本轮只做证据措辞和报告一致性修正。

## 1. 总体结果

按本地 `bmad-prd` v6.12.4 Validate 工作流，PRD 历史结果为 **有条件通过 / Fair**。本轮组长已选择课程 MVP 实施输入；组长报告 A/B/C 已同意当前课程 MVP 基线，但独立确认凭据待归档。这不构成重新运行 Validate；PRD 已形成可用于 Architecture 和 Epic/Story 规划的需求骨架，但不能标记为 final，也不能据此宣布已具备独立核实的正式团队批准或课程 M1 正式通过。

本次验证未运行业务代码、并发测试、性能测试或授权测试；所有验收场景和 NFR 结果均仍是待执行要求。

## 2. 质量维度判断

| 维度 | 判断 | 证据摘要 |
|---|---|---|
| Decision-readiness | thin | 开放问题诚实，但时段/时区、Brief 状态和 D-001 至 D-010 尚未冻结（PRD §9 298-307）。 |
| Substance over theater | strong | Vision 针对实验室预约；NFR-01/02 有实际阈值和测试口径；用户旅程适量。 |
| Strategic coherence | adequate | P0/P1/P2、Scope、FR-BOOK 和 SM-01/02 一致；SM-03 尚缺指标口径。 |
| Done-ness clarity | adequate | 15 条 FR 均有验收；下午结束边界和 NFR-03 配对矩阵仍待补足。 |
| Scope honesty | strong | Non-Goals、Out of Scope、Assumptions Index 明确，无未经批准的功能扩张。 |
| Downstream usability | adequate | 可拆至少 3 Epic/12 Story；NFR 直接追溯和 FR-ADM-03 编号说明需下游维护。 |
| Shape fit | strong | 内部工具采用 capability-first PRD，权限和设备/预约边界覆盖合理。 |

## 3. 重点质量结论（A-J）

- **A 愿景一致性：通过。** Brief §Executive Summary、Product Goals 36-39、MVP 43-54 与 PRD Vision 18-22 对齐；PRD 没有新增通知、支付、No-Show、跨实验室等功能。
- **B MVP 范围：通过。** Brief Out of Scope 56-66 与 PRD Non-Goals/MVP Scope 266-290 一致；未发现未经批准扩张。
- **C FR：基本通过。** 15 条 FR（AUTH 2、DEV 3、BOOK 7、ADM 3）独立编号、可实现且有场景；`FR-ADM-03` 是 Decision Log 记录的有意删除，不是悬空引用。
- **D NFR：基本通过。** NFR-01 248-252、NFR-02 256-258 已提供样本、计时、P95 和失败标准；NFR-03 260-264 有禁止/合法配对原则，但仍需测试矩阵。全部未执行，规模与阈值仍为假设。
- **E 验收场景：基本通过。** 正常、异常、权限和并发场景覆盖良好；时间开始边界完整，但下午结束边界仍缺验收场景。
- **F 核心一致性：通过。** Vision 20、FR-BOOK-02 142、FR-BOOK-03 152-160、NFR-01 246-252 共同规定同设备/日期/半天至多一条 `Confirmed`，取消释放时段且并发须恰好一成功。
- **G 状态规则：基本通过。** FR-DEV-03 116-122、FR-BOOK-04/05/06 164-196 明确停用不自动取消、仅 `Confirmed`/`Cancelled` 持久化、本人且未开始才可取消；停用设备上的本人取消场景应在测试阶段显式覆盖。
- **H ASSUMPTION：通过（保留状态）。** 时段、`Asia/Shanghai`、NFR-01/NFR-02 规模和半天粒度均在正文与 §10 311-315 保留，未被改写为 VERIFIED。
- **I 追溯：基本通过。** §11 323-339 覆盖每条 FR 和 NFR 后续工件；NFR-02/NFR-03 到 Brief、Decision Log、SM 的直接映射不完整。
- **J 下游拆分：具备条件。** 身份授权、设备管理、预约/管理员协调至少可形成 3 个 Epic，15 条 FR 足以拆分至少 12 个 Story；Architecture 需先承接未决假设。

## 4. Findings by severity

### Critical (0)

未发现会使 PRD 完全不可用的 Critical 问题。

### High (3)

**[Decision-readiness] 课程实施值已选定但正式确认证据未闭环（PRD 126、132-136；Decision Log D-002/D-008）**

组长已选择 08:00–12:00、13:30–17:30 和 `Asia/Shanghai` 作为课程 MVP 输入；组长报告 A/B/C 已同意，但独立确认凭据、真实实验室适用性和边界测试仍缺失。这会影响 Architecture 的时间计算和测试的预期结果。13:30 是下午创建/取消截止，17:30 主要用于查询、计算展示和“已结束”判断，不作为取消边界。

Fix：保留这些值为组长选定实施输入，由团队/实际使用者补充确认和验证证据；未完成前继续标记为 assumption，不改写为 VERIFIED。

**[Decision-readiness] Product Brief/PRD 状态仍为 draft（Brief 3；PRD 3、10、14；Decision Log D-001-D-010）**

仓库证据只表明文档版本和修订，不表明需求已最终批准。

Fix：由组长记录正式团队确认或明确保留 draft；不要把合并提交当作审批替代物。

**[Team gate] GitHub 审核证据待归档（Decision Log 140-148；PRD memlog 12、19-22）**

记录了 A/B/C 的实际反馈和接受的修改；组长报告 A/B/C 已同意当前课程 MVP 实施基线，但准确评论链接仍待补充，仓库中没有可独立核实的 Review/Approve 或教师批准记录。`a3fee51` 只证明 PR #1 已合并。

Fix：补充可访问的 GitHub 评论/Review/Approve 链接和 reviewer 身份；在补齐前标记“组长报告已同意，独立确认凭据待归档”，不声称已有可核实的正式 Approve 或教师批准。

### Medium (5)

**[Strategic coherence] SM-03 可测量性不足（PRD §8 296；Product Brief 89-91）**

“正常和冲突预约由系统自动判定的目标完成率 100%”尚未定义场景集合、分母、样本数和观察窗口，不能直接形成可复现指标。

Fix：在后续测试/评估计划中定义场景清单、样本数、观察窗口和失败判定；人工协调节省量继续保留为待验证收益。

**[Done-ness] 下午结束边界缺失（PRD 136）**

未明确 17:29:59/17:30:00（或等价规则）的查询、状态展示和“已结束”判断验收；13:30 已是下午时段创建和取消的截止边界，不将下午结束时刻写成取消边界。

Fix：时段确认后补充下午结束的查询/状态展示场景，保持 13:30 创建和取消截止规则，并保持服务端重检验。

**[NFR] NFR-01/NFR-02 规模和统计参数仍未由测试负责人确认（PRD 248、252、256-258；D-010）**

组长已选择 20 请求/50 轮、100 台设备/1000 条历史预约/20 并发读取/1000 正式请求/P95 ≤ 1000ms 作为课程测试计划暂定目标；组长报告 C 的既有评审覆盖这些指标，但独立确认凭据、环境、工具、统计和执行方案仍待归档，且尚无测试结果。

Fix：测试负责人 C 与团队在测试计划阶段确认规模、工具、环境和统计口径；执行后保存逐轮和正式样本证据，不能把组长选择写成测试通过。

**[NFR-03] 未形成禁止/合法场景逐项证据矩阵（PRD 260-264）**

原则已明确，但每个禁止场景的合法配对、数据和结果格式尚未固定。

Fix：在 QA 计划中建立配对矩阵；无需提前规定 HTTP 状态码或实现技术。

**[Traceability] NFR-02/NFR-03 直接追溯不足（PRD 321-339）**

NFR-01 有 SM-01 关联，NFR-02/NFR-03 未在追溯表中直接列明对应 Brief/Decision/SM。

Fix：后续追溯维护补充直接映射，不改业务规则。

### Low (1)

**[Mechanical] FR-ADM-03 编号空缺（PRD 214-240；Decision Log 121）**

已记录为删除项且当前无悬空引用；生成 Epic/Story 时保留该解释即可。

## 5. M1 阶段门槛

| 状态 | 判断 | 说明 |
|---|---|---|
| 文档质量验证通过 | **有条件通过** | PRD 结构和需求内容足以进入后续设计；需处理 High/Medium 项，尤其时间规则。 |
| 团队需求审核确认 | **组长报告已同意，独立确认凭据待归档** | A/B/C 反馈闭环有记录，组长报告三位队友已同意当前课程 MVP 基线；缺准确 GitHub Review/Approve 证据，不能写成正式 Approve。 |
| 课程 M1 正式通过 | **正式验收结论待核实** | 当前没有教师或课程验收记录；文档仍为 draft，且关键业务/NFR 假设与 Pitch 完成证据仍待核对。 |

### 必须在 M1 前解决

1. 组长确认 Product Brief 与 PRD 的正式状态，以及 D-001 至 D-010 中哪些已获团队确认；当前仅有组长报告 A/B/C 已同意，独立确认凭据待归档。
2. 补充 A/B/C 的可读取 GitHub Review/评论证据；如无法取得，明确写为独立凭据待归档，不虚构 Approve。
3. 确认上午/下午时段边界、实验室业务时区和当天规则，并将其作为决策记录而非 VERIFIED 测试结果。
4. 若课程 M1 要求 NFR 冻结，需由测试负责人 C 和团队补齐独立确认凭据，并确认 NFR-01/NFR-02 环境、工具、统计口径和 NFR-03 配对矩阵要求；否则可以带入 Architecture/测试计划，但必须标为待验证。
5. 核对 M1 选题 Pitch 的完成记录，并取得课程教师或课程系统的 M1 正式验收证据。

## 6. 可带入 Architecture 的待验证假设

- 半天边界暂为 08:00-12:00、13:30-17:30；由组长与实际使用者确认。
- 业务时区暂为 `Asia/Shanghai`；由组长/实际实验室确认。
- NFR-01 暂为 20 请求、50 轮；NFR-02 暂为 100 台设备、1000 条历史预约、20 并发读取、1000 正式样本、P95 <= 1000ms；由 C 与团队确认。
- 半天粒度和 Brief 中的设备数量/痛点为待验证产品假设；由产品负责人在用户验证或课程演示阶段负责。
- 锁、事务、幂等、HTTP 状态码、权限框架和测试工具没有被 PRD 锁定，应由 Architecture/API/测试阶段决定。

## 7. 完整性与追溯

FR：15 条标题和 ID 唯一，均有规则/结果/验收；依赖关系通过引用明确。NFR：3 条均有测量或通过标准，但 NFR-03 需测试矩阵，NFR-01/NFR-02 参数已获组长报告的团队认可为课程暂定指标基线，环境、工具、执行和结果仍待完成。Decision Log：D-001 至 D-010 和 PR #1 影响记录存在，保留了 AI 建议、人工决定、状态、证据和未决事项；A/B/C 的同意来自组长报告，独立确认凭据和评审链接仍待归档。

## 8. 团队审核证据

可核实证据包括：PRD memlog 中 A/B/C 反馈及接受修改的记录；Decision Log 140-148 对 A/B/C 和 C 的 GitHub 用户 `znz776625` 有明确但不带链接的记录；Git commits `2664635`、`10fe501`、`a3fee51` 证明文件修订和合并。组长报告 A/B/C 已同意当前课程 MVP 基线，但独立 GitHub Review/Approve 状态、A/B 的 GitHub 身份、教师批准以及 M1 选题 Pitch 完成状态仍不可核实。因此仍需补充相应证据。

## 9. Architecture readiness

**具备条件但不是无条件就绪。** PRD 已足以开始 Architecture 的决策范围和约束识别，尤其是预约唯一性、状态模型、权限边界和非功能验收；Architecture 必须把时段/时区/NFR 规模标为输入假设，并在需求冻结后回填验证状态。不得据此创建本轮未要求的 ADR、Epic、Story 或业务代码。

## 10. M1 正式验收仍缺少的课程证据

- 课程指定的 M1 验收标准或教师签字/评语/系统记录。
- Product Brief 与 PRD 的正式批准状态证据。
- M1 选题 Pitch 的完成记录、提交链接或课程系统状态。
- A、B、C 可读取的 GitHub Review/评论/Approve 链接和身份对应关系。
- 时间边界、业务时区、当天预约规则的实际使用者或团队确认记录。
- C/团队对 NFR 测试规模、环境、工具、统计和通过标准的确认记录。
- 业务测试、并发测试、性能测试和授权测试的实际执行证据（这些不是本轮 Validate 已执行的内容）。

## Reviewer files

- `review-rubric.md`
- `validation-report.md`
- `validation-report.html`
