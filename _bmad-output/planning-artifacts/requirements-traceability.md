---
title: LabBooking 需求到 Story / AC 追溯
status: draft
owner: B
created: 2026-11-22
updated: 2026-11-25
baselineCommit: b97ec56d6d4d832abcdbcdbd4c987082ed750725
reviewStatus: pending
---

# LabBooking 需求到 Story / AC 追溯

源需求：[PRD](prds/prd-LabBooking-2026-11-12/prd.md)第4/5节，共15 FR＋3 NFR；设计来源：[Architecture](architecture/architecture-LabBooking-2026-11-16/architecture.md)、[Spine](architecture/architecture-LabBooking-2026-11-16/ARCHITECTURE-SPINE.md)、[Context](project-context.md)。Story/AC定义见[epics.md](epics.md)。保留全部原始编号，不新增FR-ADM-03或将架构附加要求计入分母。

覆盖指已有开发范围和可判定AC；**18/18设计映射不等于需求、实现、测试或系统验收通过**。下表每行的执行证据状态均为“待建立/待验证”。B落实，C验证，需求负责人审业务覆盖，A审设计一致性。

## FR 逐项矩阵

| 需求 | 主Story及AC | 必须保留的断言及交叉验证 | 架构依据 | 验证/证据责任 |
| --- | --- | --- | --- | --- |
| FR-AUTH-01 | [1.2](epics.md#s-1-2) AC1～4；[1.3](epics.md#s-1-3) AC1/2/5；[1.4](epics.md#s-1-4) AC1/2 | 预设两角色、规范化账号、统一scrypt；有效建立身份、无效不登录；加载故障非凭据错误、绝对两小时不续期；1.5-AC1完成登录到设备页 | AD-2/5；ADR-007；D-024/027/028 | B初始化/认证；C正确/错误凭据、会话和复现证据 |
| FR-AUTH-02 | [1.3](epics.md#s-1-3) AC3/4；[3.4](epics.md#s-3-4) AC3；[3.5](epics.md#s-3-5) AC3；[4.4](epics.md#s-4-4) AC1～5 | 可信Actor，伪造user_id/role无效；每个Service独立授权，跨用户读/取消拒绝且不泄露、不改数据；全部受保护入口合法配对 | AD-1/2/5；ADR-006/007；D-012/022 | B各入口实现；C有效CSRF下身份/角色/所有权矩阵 |
| FR-DEV-01 | [1.5](epics.md#s-1-5) AC1～4 | user/admin可读Available/Disabled及明确停用提示，空结果可识别；未认证引导，故障不伪装空；4.5正式性能 | D-025/028；AD-1/2；R-61 | B列表；C两状态、空结果、认证、无隐式SQL |
| FR-DEV-02 | [2.1](epics.md#s-2-1) AC1～4；[2.2](epics.md#s-2-2) AC1～4 | 五字段/唯一code；相同code拒绝不覆盖，大小写不同允许；首尾空白不改写；只改name/location，篡改code或夹带status整体拒绝；3.4-AC4/3.6-AC6历史显示当前资料 | AD-1/3/6；D-025/029；R-63 | B设备维护；C字段边界/并发同code/普通用户拒绝及admin合法配对 |
| FR-DEV-03 | [2.3](epics.md#s-2-3) AC1～4；[3.3](epics.md#s-3-3) AC1/4；[3.6](epics.md#s-3-6) AC1/6/8 | 启停转换/重复无变更、停用拒绝新预约、重新启用恢复合法资格；两种竞争顺序和回滚；原预约、关联、快照保留；4.2识别未来影响 | AD-3/6；ADR-004；D-005/029 | B条件状态更新/创建；C真实PG竞争及历史对比 |
| FR-BOOK-01 | [3.1](epics.md#s-3-1) AC4；[3.2](epics.md#s-3-2) AC2/3；[3.3](epics.md#s-3-3) AC1/4；[3.6](epics.md#s-3-6) AC4/9 | 固定AM/PM与Asia/Shanghai；07:30/07:59:59 AM允许、08:00拒绝；12:00/13:29:59 PM允许、13:30拒绝；锁后新鲜取时、等待跨界拒绝，已满足时间资格时不另加提交截止 | AD-3/6；D-013/014/019；ADR-004 | B时间/快照/创建；C可控边界与独立PG锁后取时分别留证 |
| FR-BOOK-02 | [3.3](epics.md#s-3-3) AC1～6；[3.6](epics.md#s-3-6) AC1/4；[3.7](epics.md#s-3-7) AC1/2 | user、Available、合法空槽只建一Confirmed；旧页面/伪造身份不能绕过实际检查；确认提交才成功、确定失败无部分行，未知不误报 | AD-4/5/6；ADR-003/004 | B创建事务；C合法/停用/过时/失败/未知与终态 |
| FR-BOOK-03 | [3.1](epics.md#s-3-1) AC3；[3.3](epics.md#s-3-3) AC2/3/5；[3.6](epics.md#s-3-6) AC2/5；[3.8](epics.md#s-3-8) AC1～5 | 同设备/日期/slot第二Confirmed含重复提交拒绝；允许Service冲突预检查，数据库目标唯一索引仍为最终保障且仅其具体违反转换预约冲突；同用户跨设备允许、取消提交后可重订，提示不泄露身份，真实并发1/19/1 | AD-4/6；D-015；ADR-004/005 | B索引/原因分类；C预检查/数据库异常分别验证、跨设备正向及NFR-01证据 |
| FR-BOOK-04 | [3.4](epics.md#s-3-4) AC1～5 | 本人两状态和已结束全保留，Confirmed筛选不抹掉已结束；他人安全404；稳定分页，当前设备资料/停用提示，结束只计算 | AD-2/3/4；D-014/023/025/026；R-51/62/70 | B本人列表/详情；C隔离、历史、分页、结束与停用场景 |
| FR-BOOK-05 | [3.5](epics.md#s-3-5) AC1～5；[3.6](epics.md#s-3-6) AC3～5/9；[3.7](epics.md#s-3-7) AC1/3 | 本人Confirmed且锁后取时严格早于开始；等号/以后、重复、越权拒绝；不锁Device，已满足时间资格不另加提交截止；取消仅改八字段中的status，提交释放/回滚占位，未知时经本人详情核实 | AD-4/5/7；D-021；ADR-005 | B取消；C边界、双请求/旧ORM、跨开始提交正向及确认丢失 |
| FR-BOOK-06 | [3.1](epics.md#s-3-1) AC1/5；[3.4](epics.md#s-3-4) AC1/4/5；[3.5](epics.md#s-3-5) AC4；[3.6](epics.md#s-3-6) AC6 | 仅Confirmed/Cancelled，只有合法创建/本人取消改变状态；无Completed/恢复/删除，时间经过/查询/启停不改原预约；七字段及快照不变 | AD-3/7/8；D-007/014/026 | B状态/白名单/无删除边界；C库前后逐字段/关系/ORM检查 |
| FR-BOOK-07 | [3.2](epics.md#s-3-2) AC1～4；[3.3](epics.md#s-3-3) AC2 | 认证AM/PM分别显示可用/占用/不可预约；Cancelled不占位，AM过期不影响PM；Disabled可查询但不能预约；非法日期400；查询不保证创建且无他人资料 | AD-2/3/4/6；D-013/015/022/028 | B可用性/创建重检；C时段组合、日期、停用、未登录及查询后竞争 |
| FR-ADM-01 | [4.1](epics.md#s-4-1) AC1～4；[4.3](epics.md#s-4-3) AC1～4 | admin全状态/组合筛选/稳定分页，必要username；默认列表无phone，user拒绝；具体协调详情才读当前关联号码，不能成为任意User查询 | AD-1/2/4；D-023/028；R-51/52/62/70 | B管理查询；C筛选/授权/字段投影与无副作用 |
| FR-ADM-02 | [4.2](epics.md#s-4-2) AC1～3；[4.3](epics.md#s-4-3) AC1～4 | Disabled且未来start_at>查询时刻且Confirmed，仅这些受影响；Cancelled/过去/开始等号排除，ASC稳定分页，状态不变，列表无phone且详情受限 | AD-2/3/4；D-005/023；R-52/62 | B受影响/协调查询；C条件组合、未来边界、号码及历史不变 |
| FR-ADM-04 | [3.5](epics.md#s-3-5) AC3；[4.4](epics.md#s-4-4) AC1/2；[4.3](epics.md#s-4-3) AC4 | admin代取消拒绝、状态不变，不能借协调详情获得取消/创建权限；配对普通用户本人合法取消成功 | AD-2/7；D-009/021；ADR-005/006 | B角色/取消边界；Cadmin拒绝与user合法成功配对 |

## NFR 逐项矩阵

| 需求 | 实现与正式验收Story/AC | 不可省略的判定 | 准备/架构与责任 |
| --- | --- | --- | --- |
| NFR-01 | 3.1-AC3、3.3-AC1/3/5/6、3.5-AC4；3.6-AC1～9、3.7-AC1～5；正式[3.8](epics.md#s-3-8) AC1～5 | 20独立有效请求×50轮、真实PG竞争、逐轮预检与1成功/19正常预约冲突/最终1Confirmed、无部分行；错误/超时/未知/未完成任一失败，所有在途收敛才隔离清理、历史不变，另有不同设备/slot正向证据 | DP-07/09/10；AD-4～8、ADR-004/005、R-67/69；B实现/环境，C冻结计划并执行 |
| NFR-02 | 1.5-AC1/2/4实现基础；正式[4.5](epics.md#s-4-5) AC1～5 | 100设备/1000历史/20并发/≥1000正式完整HTTP样本、全部正确且P95≤1000ms；登录/初始化/预热排除，计时/连接/统计预先冻结、全样本和失败留存，不删失败、不用平均代P95 | DP-01/06/09/10；AD-1/8、D-030、R-61/69；B环境/查询，C计划/数据/执行/统计 |
| NFR-03 | 1.3-AC3/4、1.4-AC1～4及各功能拒绝/合法配对；正式[4.4](epics.md#s-4-4) AC1～5 | 全部身份/角色/所有权禁止场景拒绝、数据不变且不泄露，每项合法配对成功；有效CSRF下测授权，全部POST另测CSRF，不能全量拒绝当通过 | DP-02/06/10；AD-1/2/5、ADR-006/007、R-69；B各Service/投影，C逐项矩阵/执行 |

## 架构附加约束的落点

这些是18条需求的落实设计，非新增产品FR/NFR。

| 已批准补充 | Story/AC落点 | 审核重点 |
| --- | --- | --- |
| 分层/所有权/普通数据/create_app | 1.1-AC4、1.3-AC3、1.5-AC2/4及各Service范围 | 无Route查库、Service互调、Admin Service、模板SQL或跨模块写 |
| 本人username/完整phone只读区域 | 1.5-AC2；1.4-AC2/4 | Auth准备，Devices不读User，无/account、编辑、phone入Session/Actor |
| 管理员受限协调详情 | 4.3-AC1～4 | 只读具体Booking关联User，无凭据、任意用户查询或列表phone |
| User/Device/Booking字段及ORM/RESTRICT | 1.2-AC1/2、1.5-AC3、3.1-AC1/2/5 | 不增字段/资料快照/级联删除；实际维护权限和保护范围分开 |
| 锁后时钟、旧ORM、提交/未知分类 | 3.3-AC1～6、3.5-AC1～5、3.6-AC1～5、3.7-AC1～5 | SHARE创建、FOR UPDATE取消、clock_timestamp()、无重试/额外提交截止 |
| 分页与日期契约 | 3.4-AC2、4.1-AC2/3、4.2-AC1/2；DP-08 | R-70已有page/page_size边界，空串/重复为B拟定细节，供审核 |
| 固定会话、全局CSRF和HTTP语义 | 1.3-AC1～5、1.4-AC1～4、4.4-AC2～4 | 2小时不续期，全部POST覆盖，303只用于确认成功/已批准无变更 |
| 工程复现、运行资源和迁移历史 | 1.1-AC1～4、3.1-AC1/2、3.8-AC1/5、4.5-AC1/5；DP-01/05/09 | 精确版本待落实，不用系列表/迁移版本号/线程默认值充通过 |

## 既定 Route 的 Story 归属（18项）

| 方法与路径 | 实现Story | 权限/验证落点 |
| --- | --- | --- |
| GET /login | 1.3 | 未登录表单/已有登录状态，1.4期限 |
| POST /login | 1.3 | 全局CSRF、正误凭据；4.4回归 |
| POST /logout | 1.3 | 全局CSRF、当前浏览器退出；4.4回归 |
| GET /devices | 1.5 | user/admin、仅本人区域；4.4/4.5 |
| GET `/devices/<id>/availability` | 3.2 | user/admin，无他人信息；4.4 |
| POST /bookings | 3.3 | 仅user；3.8、4.4 |
| GET /bookings | 3.4 | 仅user本人；4.4 |
| GET `/bookings/<id>` | 3.4 | 仅user本人，他人404；4.4 |
| POST `/bookings/<id>/cancel` | 3.5 | 仅本人user及资格；3.6/3.7/4.4 |
| GET /admin/devices/new | 2.1 | admin，user403；4.4 |
| POST /admin/devices | 2.1 | admin；4.4 |
| GET `/admin/devices/<id>/edit` | 2.2 | admin；4.4 |
| POST `/admin/devices/<id>/edit` | 2.2 | admin/白名单；4.4 |
| POST `/admin/devices/<id>/enable` | 2.3 | admin；3.6/4.4 |
| POST `/admin/devices/<id>/disable` | 2.3 | admin；3.6/4.4 |
| GET /admin/bookings | 4.1 | admin；4.4 |
| GET `/admin/devices/<id>/affected-bookings` | 4.2 | admin；4.4 |
| GET `/admin/bookings/<id>/coordination` | 4.3 | admin及具体目标授权；4.4 |

路径中的devices不把availability/affected-bookings归给Devices Service；两者属Bookings。全部写入及login/logout都用POST全局CSRF；GET无业务写入，无平行JSON API或独立取消资格接口。

## NFR-03 最低配对执行表

此表为C执行矩阵的最低内容，尚无执行记录；每组应细化到原始请求、身份、目标、CSRF、预期/实际HTTP、前后状态及安全投影。

| 禁止请求组 | 应验证的拒绝 | 对应合法成功组 |
| --- | --- | --- |
| 未登录设备列表/半天可用性 | GET302、无业务/他人数据 | 已登录user/admin GET200，两状态/AM/PM正确 |
| 未登录本人列表/详情 | GET302 | 本人user GET200且只含本人 |
| user A伪造user_id/URL/ID读取B记录 | 列表保持A范围；他人详情404、不泄露B存在/信息 | B本人详情200，A本人记录正常 |
| 未登录创建（有效CSRF） | POST401、不创建 | user合法创建303且Confirmed |
| admin创建（有效CSRF） | POST403、不创建 | user合法创建303 |
| 未登录取消（有效CSRF） | POST401、不变 | 本人user合格取消303且Cancelled |
| A取消B（有效CSRF） | POST404、不变、无B信息 | B本人合格取消303 |
| admin代取消（有效CSRF） | POST403、原预约不变 | 预约本人user合格取消303 |
| user新增/编辑/启用/停用设备 | 管理GET/POST403，各项分别检查不变 | admin对应GET200/合法POST303及正确变更 |
| 未登录设备维护（POST有效CSRF） | GET302/POST401，各入口分别检查不变 | admin对应合法读取/修改成功 |
| user或未登录全部/受影响/协调查询 | user403/未登录302，无他人号码/标识 | admin授权读取200，列表无phone、具体详情有对应phone |
| admin访问user本人入口 | 角色403，无普通用户个人列表/详情 | user本人200；admin使用管理查询200 |
| 所有POST缺失/无效CSRF | 400、无业务写入；不能替代上述授权结论 | 有效CSRF继续验证对应合法/禁止业务分支 |

## 审核检查点

需求负责人逐行检查AC是否承接完整业务规则，A核对AD/ADR与附加约束，C确认每个场景可由实际请求/DB状态/证据判定。发现遗漏时更新具体Story/AC及本表；测试文件创建后补实际路径和报告链接，不预填不存在的测试或“通过”状态。

<a id="journeys-and-metrics"></a>

## 用户旅程与成功指标追溯（2026-11-25评审修订）

依据PRD第2.3/8节以及需求负责人/C的PR #4意见补齐，不新增FR、NFR或Story。以下E2E编号为现有Story/AC的跨步骤验收场景，**均待C冻结细化与执行**；由4.4-AC5汇总，产品指标、授权和性能各自判定，不相互替代。

| 用户旅程 | 现有Story/AC | 端到端场景与判定 |
| --- | --- | --- |
| UJ-1 学生身份user预约空闲设备 | 1.3-AC1、1.5-AC1/2、3.2-AC1/2、3.3-AC1/4/5、3.4-AC1；4.4-AC5汇总 | E2E-01：登录→设备查询→选日期/AM或PM→可用性→创建→本人记录可见Confirmed，所有者/设备/日期/slot正确 |
| UJ-2 研究人员身份user取消本人未开始预约 | 3.4-AC1/3、3.5-AC1～4、3.6-AC5；4.4-AC5汇总 | E2E-02：本人记录→符合资格取消→显示Cancelled且历史保留→同槽新的合法预约可竞争，其他七字段不变 |
| UJ-3 冲突或重复提交 | 3.3-AC2/3/5、3.1-AC3、3.8-AC1～5；4.4-AC5汇总 | E2E-03：重复/同槽竞争拒绝第二Confirmed，安全提示只含设备/日期/slot；另验同用户跨设备合法；并发正式结论另按NFR-01 |
| UJ-4 admin停用设备并识别影响 | 2.3-AC1/2、3.3-AC4、3.4-AC4、3.6-AC1/6、4.2-AC1～3、4.3-AC1/4 | E2E-04：停用→仍可见且禁止新预约→既有Confirmed不变→仅未来Confirmed受影响→授权具体详情供线下协调，无代取消 |

| 成功指标 | 现有Story/AC与场景 | 目标与记录口径 |
| --- | --- | --- |
| SM-01 并发预约一致性 | 3.3-AC3/5、3.6-AC2/5、3.8-AC1～5；E2E-03 | NFR-01的50轮逐轮1成功/19正常预约冲突/最终1Confirmed，双重有效预约0且无其他错误，隔离清理不改历史；保留跨设备/时段正向证据 |
| SM-02 核心预约流程完整性 | 1.3、1.5、3.2～3.5的上述AC及4.4-AC1～5；E2E-01/02/03/06 | C在执行前冻结覆盖登录、查询、选槽、创建、本人查看、合格取消、冲突拒绝与越权禁止的全部核心细化场景；通过数/冻结场景总数目标100%。漏测、未执行或失败不能从分母剔除；设备列表P95通过不证明本指标通过 |
| SM-03 自动判定覆盖 | 3.3-AC1/2/3、3.8-AC2/3、4.4-AC5；E2E-01/03 | C预先冻结正常与冲突预约的请求/场景集合及分母，记录系统正确自动判定完成数/该集合总数，目标100%，无需admin逐条审批。技术错误/未知不算正确完成，不事后删样本；不据此声称实际节省多少人工协调时间 |

<a id="e2e-core-cases"></a>

## 现有Story内的端到端验收场景

共同前提：批准时段/Asia/Shanghai、隔离PG及符合约束的合成账号/设备；同一案例记录使用的提交、身份/CSRF、原请求/响应、关联数据及独立终态。写操作用原POST结果与提交状态判定，不能只看最终重定向页。每个边界案例独立初始化；故障或并发用例另保留同步/注入证据。

| 场景 | Given / When | Then与现有AC落点 |
| --- | --- | --- |
| E2E-01 合法预约闭环 | Given user、Available、尚未开始空槽；When 登录、查设备和日期AM/PM、创建并打开本人记录 | Then 登录身份可信、查询正确、原POST303且一条本人Confirmed，设备/日期/slot/快照正确；1.3-AC1、1.5-AC1/2、3.2-AC1、3.3-AC1、3.4-AC1 |
| E2E-02 本人取消与重新竞争 | Given本人未开始Confirmed；When 本人列表/详情取消并查询，再合法创建同槽 | Then 取消原POST303、旧行Cancelled、其余七字段不变且历史保留，新请求按原协议可竞争；3.4-AC1、3.5-AC1/4、3.6-AC5 |
| E2E-03 冲突与重复提交 | Given已有Confirmed或重复提交；When 同槽请求及同用户跨设备正向请求 | Then 正常预约冲突拒绝且无第二Confirmed/他人信息，跨设备合法成功；3.3-AC2/3/5、3.8-AC1～5；NFR-01正式判定保持独立 |
| E2E-04 停用影响与受限协调 | Given未来Confirmed/Cancelled及过去记录；When admin停用、user查看/尝试新建、admin查受影响与协调详情 | Then Disabled可见、新创建拒绝、原预约保留，仅未来Confirmed列为受影响，列表无phone、授权详情为正确关联号码且无自动取消；2.3-AC1、3.3-AC4、3.4-AC4、4.2-AC1～3、4.3-AC1/4 |
| E2E-05 未知结果后查询核实 | Given创建/取消已提交但确认丢失；When 页面503并通过现有本人列表/详情GET核实 | Then 明确尚未确认且不自动重发POST，查询分别反映Confirmed/Cancelled，独立PG核查一致；3.7-AC2/3/5；模拟与真实故障证据分开，未执行真实场景不能关闭AC |
| E2E-06 越权禁止与合法配对 | Given两名user和admin；When 按18个Route逐入口直构未认证/伪造身份/跨用户/角色越权请求，并执行对应合法请求 | Then 授权拒绝、数据不变、无泄露、合法配对成功；1.3-AC3/4、3.4-AC3、3.5-AC3、4.4-AC1～5；有效CSRF下测授权，缺失/无效令牌另测 |

执行计划须把上述组合场景拆成可逐项判定的细化用例，不能以一个“E2E通过”掩盖登录/取消/冲突/越权或任一受保护入口漏测。UJ-4和故障回归单列结果，不擅自改写SM-02/03的预冻结集合；追溯与本轮修订依据记入[Decision Log](decision-log.md#epics-review-2026-11-25)。
