---
title: LabBooking Epics / Stories 初稿
status: draft
owner: B
created: 2026-11-22
updated: 2026-11-22
baselineCommit: b97ec56d6d4d832abcdbcdbd4c987082ed750725
stepsCompleted: [1, 2, 3, 4]
reviewStatus: pending
workflowMode: 用户授权连续完成初稿；阶段产物供 A、需求负责人、C 审核，不视为批准
inputDocuments:
  - prds/prd-LabBooking-2026-11-12/prd.md
  - prds/prd-LabBooking-2026-11-12/m1-closeout-summary.md
  - architecture/architecture-LabBooking-2026-11-16/architecture.md
  - architecture/architecture-LabBooking-2026-11-16/ARCHITECTURE-SPINE.md
  - project-context.md
  - decision-log.md
---

# LabBooking — Epics / Stories 初稿

## 基线与使用方式

以 [PRD](prds/prd-LabBooking-2026-11-12/prd.md)、[Architecture](architecture/architecture-LabBooking-2026-11-16/architecture.md)、[Spine](architecture/architecture-LabBooking-2026-11-16/ARCHITECTURE-SPINE.md)、[Project Context](project-context.md) 和 [Decision Log](decision-log.md) 为输入；仓库基线为 main 的 `b97ec56d6d4d832abcdbcdbd4c987082ed750725`（[PR #3](https://github.com/doublej1943/lab-equipment-booking/pull/3)）。日期采用 Asia/Shanghai。

本稿由 B 编制，供需求负责人检查需求与业务验收、A 检查架构一致性、C 检查测试及证据可执行性。用户已要求一次完成初稿，工作流的中间讨论留在审核清单，不将其记为三方已批准。源文件历史 draft、未实测及课程假设标记保留；不修改已批准方案或源文档。

## 需求清单

### 功能需求（保留 PRD 原编号，共 15 条）

| 编号 | 需要交付的能力与边界 |
| --- | --- |
| FR-AUTH-01 | 预设账号登录，识别 user/admin；有效凭据建立身份，无效凭据安全拒绝。 |
| FR-AUTH-02 | 服务端身份、角色及所有权检查；篡改 URL/标识/参数不能越权，拒绝后数据不变。 |
| FR-DEV-01 | 已认证查询 Available/Disabled 设备；停用仍显示，空结果可识别。 |
| FR-DEV-02 | admin 新增设备、编辑名称/位置；code 唯一且创建后不可改，非法请求无部分修改。 |
| FR-DEV-03 | admin 启停；Disabled 拒绝新预约，既有预约及历史保留，重新启用恢复合法预约资格。 |
| FR-BOOK-01 | 日期与 AM/PM 半天选择；创建时服务端检查严格早于开始，过去、已开始或结束拒绝。 |
| FR-BOOK-02 | user 为 Available、合法且空闲的时段创建一条 Confirmed；实际处理重检，无部分记录。 |
| FR-BOOK-03 | 同设备/日期/slot 第二条 Confirmed（含重复提交）拒绝；取消释放后可重订；同用户跨设备允许，冲突不泄露他人身份。 |
| FR-BOOK-04 | 仅本人历史/详情；保留 Confirmed/Cancelled/已结束记录，停用提示，已结束为计算展示。 |
| FR-BOOK-05 | 仅本人 Confirmed 且尚未开始可取消；服务端实际处理重检，成功变 Cancelled 并保留历史；越权、重复及已开始拒绝。 |
| FR-BOOK-06 | 持久化状态仅 Confirmed/Cancelled；时间经过、查询、设备停用不隐式改状态，无 Completed。 |
| FR-BOOK-07 | 认证后分别查询 AM/PM 可用/占用/不可预约；Cancelled 不占位，停用仍可查，非法日期拒绝，查询不保证创建成功。 |
| FR-ADM-01 | admin 全部预约及必要预约人标识；默认列表无联系方式，普通用户拒绝。 |
| FR-ADM-02 | admin 识别 Disabled 设备未来 Confirmed；排除 Cancelled 与已开始/过去记录，不改状态，不默认给联系方式。 |
| FR-ADM-04 | 禁止 admin 代取消；管理员不继承 user 创建/取消能力。保留原编号，不补建 FR-ADM-03。 |

### 非功能需求（共 3 条）

- **NFR-01**：真实 PostgreSQL；20 个独立、有效、已认证请求同步竞争同设备/日期/slot，重复 50 轮。逐轮预检 Available、合法未来时段且无 Confirmed；每轮恰好 1 成功、19 正常预约冲突、最终 1 Confirmed，无部分记录。技术错误、认证/CSRF失败、超时、未知结果或未完成均失败，不能计冲突；全部在途结束且不再写入后才清理本轮隔离数据，确认空闲再下一轮，保留其他历史。另验不同设备/时段不被错误阻塞。
- **NFR-02**：100 台设备、1000 条历史、20 个并发读取用户，至少 1000 个正式完整设备列表 HTTP 请求；所有内容正确且 P95 ≤ 1000ms。登录/初始化/预热排除；预先冻结身份、参数/分页、数据生成、环境/工具、并发及计时/连接建立口径、超时和 P95 方法，保留全部正式样本。失败、内容错、超时、认证异常等均失败，不能删样本或用平均数代替 P95。
- **NFR-03**：覆盖 PRD 所列未认证操作、跨用户读/取消、普通用户设备维护与管理查询、管理员代取消以及其他受保护入口；每组禁止请求拒绝、数据不变、无受保护信息泄露，并配对成功的合法请求。有效 CSRF 下验证授权，全部 POST 的 CSRF 另测；不能因所有请求被拒绝判通过。

以上时段、Asia/Shanghai 及 NFR 数值继承课程实施基线，仍不代表真实使用者验证或测试已通过；C 在正式执行前冻结计划，不能擅自降低阈值。

### 架构附加要求

1. Flask/Jinja2 SSR 轻量分层单体；Auth/Devices/Bookings 分别拥有 User/Device/Booking 写入，无第四个 Admin Service。Route 不查库、Service 不互调、模板不隐式 SQL，使用普通展示数据（AD-1、ADR-006/008）。
2. create_app、请求级 Flask-SQLAlchemy Session；Auth 只读生成可信 Actor，业务 Service 单一提交/失败回滚，HTTP 错误处理不接管事务（AD-5、ADR-003/006）。
3. PostgreSQL 17、单一 Alembic 链；批准的三实体字段、非空/CHECK/RESTRICT 外键、禁止 ORM 删除级联、历史与快照保留；仅 Confirmed 的三列部分唯一索引（AD-3/4/8）。
4. READ COMMITTED 先于首次 Auth 查询；创建 Device FOR SHARE 字段查询，锁后单独 clock_timestamp() 严格早于 start_at；停用条件 UPDATE RETURNING（AD-6、ADR-004）。
5. 取消 Booking FOR UPDATE 字段查询，锁后本人/Confirmed/新鲜取时检查，仅改 status，不锁 Device；提交释放、回滚占位，重复取消不再次成功（AD-7、ADR-005）。
6. Flask-Login、原生签名 Cookie、登录起算绝对两小时、无 Remember-me；全部 POST 全局 CSRF；Werkzeug scrypt，精确参数及环境配置由 B 落实（AD-2、ADR-007）。
7. 本人完整 phone 仅在 /devices 独立当前账号区域由 Auth 准备；admin 仅在具体预约协调详情读取关联 username/phone；列表条目/可用性/冲突不含 phone，Actor/Session/Booking 无 phone（D-023、R-61）。
8. 既定 SSR Route/HTTP 表，成功写入确认后 303；业务拒绝/技术故障/提交未知分开，只有目标唯一索引违反转预约冲突，无自动重试（R-59）。
9. LIMIT/OFFSET；预约列表 start_at DESC,id DESC，受影响未来 ASC；page 默认1、page_size 默认20/最大100，非法400、合法越界空200；管理员日期闭区间、设备、状态 AND（R-51/52/62/70）。
10. Windows/Conda labbooking、独立 PG 开发/测试库、Waitress、单一有界连接池、分项超时和资源预算、私有密钥及迁移/运行权限分离；B 准备、C 复现和验证（R-65～69）。

### UX 输入

基线中未发现独立 DESIGN.md / EXPERIENCE.md 或 UX 设计稿。遵守现有 SSR 入口、状态提示、隐私与表单行为；页面布局由 B 落实，保留 Tailwind CSS/Lucide 选择，不虚构新设计系统或新增产品功能。

## Epic 列表与覆盖

按用户成果组织四个 Epic；不按数据库/API/页面拆成独立 Epic。同一 Bookings 模块的创建、历史、取消与一致性集中到 E3，减少跨 Epic 反复修改核心协议。技术准备作为首批支撑 Story，后续按首次需要引入实体，首个 Story 不预建全库。

| Epic | 用户成果 | 主要覆盖 | 先决 Epic |
| --- | --- | --- | --- |
| E1：可信登录并查看设备 | user/admin 可登录并安全查看设备和本人信息，形成可演示的只读入口 | FR-AUTH-01/02、FR-DEV-01；NFR-03 基础机制 | 无 |
| E2：管理员维护设备可用性 | admin 可新增、编辑、启停设备，用户查看结果 | FR-DEV-02/03；NFR-03 设备权限 | E1 |
| E3：用户完成可靠预约与本人取消 | user 查询时段、创建、查看及取消；冲突、时间和历史规则可验证 | FR-BOOK-01～07、FR-AUTH-02、FR-ADM-04；NFR-01 | E1；启停竞争验证使用 E2 |
| E4：管理员识别预约影响并受限协调 | admin 查询全部及受影响预约、读取授权联系方式；收束全系统授权及列表性能验收 | FR-ADM-01/02/04；NFR-02/03 | E2、E3 |

各 Epic 可在其前置完成后交付自己的用户成果，不依赖后续 Epic 才能运行。E1/E2 使用合成初始化数据；E3 最小成功响应直接显示设备/日期/slot，不等待 E4。E4 的最后两条为全系统验收 Story，复用先前实现，不重复开发功能。

| 需求 | 归属与主要 Story（详述见下文） |
| --- | --- |
| FR-AUTH-01 | E1：1.2、1.3、1.4 |
| FR-AUTH-02 | E1：1.3、1.4；E3：3.4、3.5；E4：4.4 |
| FR-DEV-01 | E1：1.5 |
| FR-DEV-02 | E2：2.1、2.2 |
| FR-DEV-03 | E2：2.3；E3：3.3、3.6 |
| FR-BOOK-01 | E3：3.1、3.2、3.3、3.6 |
| FR-BOOK-02 | E3：3.3、3.6、3.7 |
| FR-BOOK-03 | E3：3.1、3.3、3.6、3.8 |
| FR-BOOK-04 | E3：3.4 |
| FR-BOOK-05 | E3：3.5、3.6、3.7 |
| FR-BOOK-06 | E3：3.1、3.4、3.5、3.6 |
| FR-BOOK-07 | E3：3.2、3.3 |
| FR-ADM-01 | E4：4.1、4.3 |
| FR-ADM-02 | E4：4.2、4.3 |
| FR-ADM-04 | E3：3.5；E4：4.4 |
| NFR-01 | E3：3.1、3.3、3.5～3.8；正式判定在3.8 |
| NFR-02 | E1：1.5；E4：4.5 正式判定 |
| NFR-03 | 全部受保护功能逐 Story 验证；E4：4.4 完整配对矩阵正式判定 |

本表为设计覆盖，测试文件和执行结果尚未产生；详细 AC 追溯单独维护于 [requirements-traceability.md](requirements-traceability.md)。

## Story 共用约定

所有 Story 初始状态均为 **draft / 未开发 / 未执行验收**。B 主责实现、C 验证；3.8、4.4、4.5 由 C 主责测试计划、执行与证据，B 提供实现和环境支持。A 审核设计一致性，需求负责人审核业务覆盖；二者不被记为代码实现人。

- AC 编号如 `1.3-AC1` 可直接用于测试和审核定位。以下每条以 Given/When/Then 表达；“允许”仍以身份、资源及其他业务资格均满足为前提。
- 受保护写请求的业务/授权测试默认带有效 CSRF；缺失或无效 CSRF 单独验证400。认证入口不替代 Service 授权。共用拒绝标准：数据不变、响应/模板/日志不泄露受保护信息。
- 每条功能 Story 包含所属 Route、Service、Model/Query（按需）、SSR 页面、必要迁移与有意义的正反验证，避免分成无法单独交付的前后端半成品。未列出的新字段、入口、功能不在范围。
- 每条 Story 完成须满足本条 AC、适用共用约定、真实 PG 的相关集成验证及代码审核。正式 NFR 验收另由对应 Story 判定；局部通过不代表整项 FR/NFR 或系统验收通过。
- `依赖`只列直接硬依赖，传递关系不重复列；`DP-*`是[开发准备清单](development-readiness.md)的门槛，详细启动条件见该清单。只有前置产物存在且适用门槛关闭才可实施相应工作。全部状态当前待审核，尚无 Sprint 承诺。

## Epic 1：可信登录并查看设备

用户成果：预设 user/admin 能从统一登录入口进入认证设备列表，并只读取本人的账号资料。

<a id="s-1-1"></a>

### Story 1.1：复现可运行的应用与隔离环境

**As a** 开发及测试成员，**I want** 在干净环境启动同一应用并隔离测试数据，**So that** 后续用户功能建立在可复现基线上。

**需求/架构**：FR-AUTH-01、FR-DEV-01 支撑；NFR-01/02/03 支撑；AD-1/5/8、ADR-001/002/003/008、R-65～68。

**依赖**：无；开始前关闭 DP-01 的版本选择部分，完成时关闭其复现部分。

**开发范围**：精确依赖清单、environment.yml及必要锁定文件、create_app、配置/扩展/三个模块装配、测试配置、Alembic基础连接、Waitress启动说明。无业务表集中预建，无新架构层或公共健康检查产品入口。

**Acceptance Criteria:**

- **1.1-AC1** — **Given** 锁定清单和空 Conda 环境，**When** C 按说明安装启动，**Then** 实际解释器/直接及传递依赖与记录一致，应用可由 Waitress 启动，精确版本与日志留证；不能仅提供版本系列或安装者口述。
- **1.1-AC2** — **Given** 开发和测试配置，**When** 初始化连接，**Then** 连接不同的 PostgreSQL 数据库、同一批准系列，测试配置误指开发库时拒绝破坏性初始化；不以 SQLite 替代。
- **1.1-AC3** — **Given** 新连接及池复用连接，**When** 首次身份/业务查询前检查，**Then** READ COMMITTED 已生效，使用一个 SQLAlchemy 有界池；请求结束清理 Session，不跨请求共享事务。
- **1.1-AC4** — **Given** 缺少必要私有配置或测试启动，**When** 装配应用，**Then** 缺失配置有安全明确错误，密钥/凭据不输出；create_app 可注入测试配置且业务模块不反向导入装配入口，尚未实现的页面不伪装可用。

<a id="s-1-2"></a>

### Story 1.2：安全初始化预设账号

**As a** 指定系统维护人员，**I want** 一次性校验并初始化预设账号，**So that** 用户用已知身份登录且账号资料一致。

**需求/架构**：FR-AUTH-01/02、NFR-03；D-023/024、AD-2/3/8、ADR-001/007。

**依赖**：1.1；实现前关闭 DP-02 的哈希配置与 DP-04 的 User 约束落实；真实名单导入前关闭 DP-03。

**开发范围**：仅 User 五字段模型/迁移、初始化命令、username规范化、scrypt生成/核验支持；合成测试账号。真实账号资料由需求负责人私下提供；没有资料时工具和合成验证可交付，真实导入状态必须仍为待办。无注册、用户管理或手机号修改接口。

**Acceptance Criteria:**

- **1.2-AC1** — **Given** 合法预设输入，**When** 执行初始化，**Then** 仅写 id/username/password_hash/role/phone，id为INTEGER ALWAYS Identity；按批准类型、长度、非空/唯一/合法role约束迁移。username去首尾空白及小写后唯一，phone必填非唯一，同号码允许。
- **1.2-AC2** — **Given** 规范化重名、非法role、缺失/非法phone或空白哈希等输入，**When** 校验或写入失败，**Then** 整批无部分账号、不覆盖既有账号，报告安全错误；不擅加未经批准的username ASCII CHECK或生成真实账号/号码。
- **1.2-AC3** — **Given** DP-02 固定的 Werkzeug scrypt 配置，**When** 生成并核验哈希，**Then** 正确密码通过、错误密码失败、完整哈希存TEXT，初始化与认证使用相容配置；不同盐生成结果可不同，不要求哈希字符串相等，不存明文或在登录时写入升级哈希。
- **1.2-AC4** — **Given** 初始化及干净环境复现记录，**When** 检查公开文件和日志，**Then** 无真实密码、哈希、完整手机号或凭据；格式合格不被描述为真实号码/归属认证，合成数据明确标识。

<a id="s-1-3"></a>

### Story 1.3：登录、登出并传递可信身份

**As a** 预设普通用户或管理员，**I want** 使用有效凭据进入授权功能并退出，**So that** 后续请求使用我的真实身份。

**需求/架构**：FR-AUTH-01/02、NFR-03；AD-1/2/5、ADR-006/007、R-21～26/53/57～59。

**依赖**：1.2；DP-02。

**开发范围**：GET/POST /login、POST /logout、Flask-Login适配、全局CSRFProtect、Auth只读身份加载、可信Actor与统一HTTP映射基础。GET /login已有登录状态的处理是既定Route，可在设备页交付前独立承接成功登录，显示安全身份状态而非设备数据；业务入口按各自Story逐步接入，不新增临时入口或JSON API。

**Acceptance Criteria:**

- **1.3-AC1** — **Given** user/admin有效凭据及有效CSRF，**When** POST登录，**Then** 按初始化相同username规范与scrypt核验，清理旧登录状态并建立新身份，303到已交付的授权页面；本Story可使用GET /login的已有登录状态分支完成可访问闭环，显示本人安全身份状态、不展示phone，不依赖未来Story才能验证成功。
- **1.3-AC2** — **Given** 错账号或错密码，**When** 登录，**Then** 统一安全提示401且无已认证会话；身份数据库故障按技术错误处理，不伪装无效凭据/未登录。
- **1.3-AC3** — **Given** 已认证请求且客户端伪造user_id/role，**When** HTTP保护入口生成Actor并调用业务Service，**Then** 身份/角色来自数据库可信User，Auth只读不提交；Service显式接收Actor、不依赖current_user或调用其他Service，模板只收普通数据。
- **1.3-AC4** — **Given** 全局CSRF及登录/登出表单，**When** POST缺失/无效令牌，**Then** 返回400；有效令牌但未认证的受保护修改返回401，不重放；受保护GET未认证302到登录。业务POST后续注册同样受全局保护，无豁免。
- **1.3-AC5** — **Given** 有效当前浏览器会话及CSRF，**When** POST /logout，**Then** 清理当前登录状态303到登录，不改User/Booking，不接受任意外部next，不承诺复制旧Cookie立即全局撤销。

<a id="s-1-4"></a>

### Story 1.4：固定会话期限与浏览器安全配置

**As a** 已登录用户，**I want** 身份在明确期限内有效且资料受保护，**So that** 浏览器活动不会悄悄扩大登录权限。

**需求/架构**：FR-AUTH-01/02、NFR-03；AD-2、ADR-007、R-56/57/68。

**依赖**：1.3；DP-02、DP-06。

**开发范围**：登录起算/截止与逐请求检查、Cookie/密钥、隐私页面缓存控制、安全日志配置及验证；本地HTTP和外部HTTPS配置区分。无服务端会话表、集中撤销或Remember-me。

**Acceptance Criteria:**

- **1.4-AC1** — **Given** 登录时刻t0，**When** 受保护请求分别在t0+2h之前和恰好达到/超过截止到达，**Then** 前者可继续授权，后者失效需重新登录；活动、flash、Cookie重签发均不延长原截止。
- **1.4-AC2** — **Given** 签名Cookie，**When** 解码检查或篡改后请求，**Then** 仅必要身份/计时/框架安全状态，无phone、password_hash、密码或个人展示资料；篡改拒绝，角色仍可信加载，无Remember-me状态。
- **1.4-AC3** — **Given** 开发HTTP和外部HTTPS配置，**When** 检查响应Cookie，**Then** HttpOnly、SameSite=Lax生效，HTTPS启用Secure，本地例外有单独配置且不会成为部署默认；TLS终止不归Waitress承诺。
- **1.4-AC4** — **Given** 包含本人/协调信息的响应及错误路径，**When** 按DP-06检查缓存策略、日志与错误页，**Then** 私有信息不进入共享缓存或诊断输出，日志无密码/hash/Cookie/CSRF/完整phone/连接凭据；错误页不泄露SQL。

<a id="s-1-5"></a>

### Story 1.5：认证设备查询与本人账号区域

**As a** 普通用户或管理员，**I want** 查看设备状态及自己的账号资料，**So that** 可以识别设备并确认当前身份。

**需求/架构**：FR-DEV-01、FR-AUTH-02；NFR-02实现基础、NFR-03；AD-1/2/3、D-025、R-61。

**依赖**：1.4；DP-04 的Device约束部分。

**开发范围**：Device五字段模型/迁移及GET /devices，Available/Disabled展示、空结果；Auth在HTTP入口准备独立本人username/phone区；固定前端资源版本/引入方式。无独立/account页或匿名查询。

**Acceptance Criteria:**

- **1.5-AC1** — **Given** 已登录user/admin及两状态设备，**When** GET /devices，**Then** 200且两状态均可见、Disabled明确“设备已停用”；无设备时200可识别空结果，不伪造可用设备；未认证302登录。本Story将成功登录落点接入已实现的/devices，完成登录到设备页的实际用户流程。
- **1.5-AC2** — **Given** User A/B分别登录，**When** 查看页面，**Then** 独立当前账号区只展示当前本人username和完整phone，数据由Auth准备；Devices Service不读User或调用Auth，设备条目不带phone。
- **1.5-AC3** — **Given** Device迁移，**When** 检查结构和展示数据，**Then** 只有id/code/name/location/status，遵守批准字段及大小写敏感全表code唯一性，无Location表/描述/型号/停用原因，所有展示数据为普通值。
- **1.5-AC4** — **Given** 模板渲染阶段及设备/本人查询故障，**When** 渲染或处理错误，**Then** 模板不发SQL/隐式加载；查询故障为技术错误，不伪装空设备列表或公开他人资料。正式NFR-02由4.5验证。

## Epic 2：管理员维护设备可用性

用户成果：admin 能通过既定表单新增、编辑、启停设备；只写Device，不需要未来Epic提供写入能力。预约出现后的跨模块保留/竞争回归由3.6补齐。

<a id="s-2-1"></a>

### Story 2.1：新增唯一标识的设备

**As a** 管理员，**I want** 录入合法且编号唯一的设备，**So that** 用户可以查询并选择它。

**需求/架构**：FR-DEV-02、FR-AUTH-02、NFR-03；D-025/029、AD-1/3/5、R-63。

**依赖**：1.5；DP-04。

**开发范围**：GET /admin/devices/new、POST /admin/devices，Devices Service五字段校验及创建、表单/结果提示、code唯一异常分类；不增加扩展字段、删除或导入功能。

**Acceptance Criteria:**

- **2.1-AC1** — **Given** 已认证admin和合法code/name/location/显式status，**When** 提交新增，**Then** 提交成功后303、GET可见同一新设备；status仅Available/Disabled，缺失或非法字段400且无部分记录。
- **2.1-AC2** — **Given** code首尾空白、空串/纯空白业务文本或超长值，**When** 请求新增，**Then** 按输入错误拒绝，code不静默trim或变更大小写，不增加未经批准字符白名单。
- **2.1-AC3** — **Given** 已存在相同code（包括Disabled设备），**When** 再次创建或两个请求竞争相同code，**Then** 唯一违反独立设备冲突409，原记录不覆盖，最多一条设备；仅大小写不同的code允许，同名/同位置允许，不误计D-015预约冲突。
- **2.1-AC4** — **Given** 未认证/普通用户及合法表单数据，**When** 直接访问管理入口或POST，**Then** 未认证GET302、有效CSRF未认证POST401、user403且库不变；合法admin配对成功。

<a id="s-2-2"></a>

### Story 2.2：只编辑名称与位置并保留设备身份

**As a** 管理员，**I want** 更新设备名称和位置，**So that** 当前资料准确且历史关联稳定。

**需求/架构**：FR-DEV-02、FR-AUTH-02；FR-BOOK-04/06历史支撑、NFR-03；D-025/029、AD-1/3、R-63。

**依赖**：2.1。

**开发范围**：GET/POST `/admin/devices/<id>/edit`，白名单name/location、原code只读、整体拒绝篡改；不通过编辑入口更改status或设备id。

**Acceptance Criteria:**

- **2.2-AC1** — **Given** admin及既有设备，**When** 合法修改name/location，**Then** 同一id/code/status保留、仅资料更新、提交成功303、不新建Device；空白/超长等非法值400且库不变。
- **2.2-AC2** — **Given** 请求更改code并同时提交合法name/location，或编辑夹带status，**When** 提交，**Then** 整体拒绝且所有字段不变，无先保存部分资料；启停仍走专门入口。
- **2.2-AC3** — **Given** 不存在设备或普通用户，**When** GET/POST编辑，**Then** 分别按404或角色403处理，未认证遵循通用保护；合法admin配对成功，模板无隐式SQL，写入由Devices Service完成。
- **2.2-AC4** — **Given** 设备资料编辑代码及数据，**When** 审核写入范围，**Then** 不改Device.id、不写其他模块或创建资料快照；预约功能引入后在3.4/3.6验证历史显示当前资料、Booking自身及时间快照不变。

<a id="s-2-3"></a>

### Story 2.3：条件启停设备并区分重复操作

**As a** 管理员，**I want** 启用或停用设备并知道是否发生变更，**So that** 可以控制后续预约资格。

**需求/架构**：FR-DEV-03、FR-AUTH-02、NFR-03；ADR-004、AD-3/5/6、R-05/63/64。

**依赖**：2.1。

**开发范围**：POST `/admin/devices/<id>/enable`、/disable，条件UPDATE RETURNING与无返回补查、无变更提示、单一Service事务；不修改Booking。此处先完成设备端行为，3.3消费状态、3.6完成真实预约联动回归，不构成运行依赖。

**Acceptance Criteria:**

- **2.3-AC1** — **Given** admin及Available设备，**When** 停用，**Then** 执行Available→Disabled条件UPDATE RETURNING，提交成功才303并报告转换；反向启用用Disabled→Available条件更新，设备资料和id/code不变。
- **2.3-AC2** — **Given** 已在目标状态、设备不存在或补查发现再次变化，**When** 条件更新无返回，**Then** 区分当前目标已满足（正常无变更303且不声称本次转换）、不存在404及再次变化（安全业务409）；不自动循环或重试。
- **2.3-AC3** — **Given** 普通用户/未认证请求和合法admin请求，**When** 直接启停，**Then** 前者按角色/身份拒绝且无变化，后者可转换；缺失CSRF另验400，不以其代替角色验证。
- **2.3-AC4** — **Given** 更新或提交确定失败，**When** Service处理，**Then** 回滚且不报成功；技术异常和提交未知按统一契约分开，无Booking更新/取消/改约调用、无额外预约锁或重试设施。真实创建竞争和历史保留在3.6验证。

## Epic 3：用户完成可靠预约与本人取消

用户成果：user 可查询半天可用性、创建合法预约、查看本人记录并取消；同槽唯一、设备状态与锁后时间边界有真实PG证据。Bookings写入只属于本模块。

<a id="s-3-1"></a>

### Story 3.1：落实预约字段、时段快照与最终唯一性

**As a** 预约用户，**I want** 预约按固定半天规则保存且有效占位唯一，**So that** 我的预约和历史不被错误覆盖。

**需求/架构**：FR-BOOK-01/03/06、NFR-01；D-013/014/015/026、AD-3/4/8、ADR-001/002。

**依赖**：1.5；DP-04、DP-05 的迁移命名/审查规则。

**开发范围**：Booking八字段模型/迁移、统一AM/PM与业务时区快照生成、FK与ORM关系、部分唯一索引及准确异常识别支持。不建时段表、不预增查询索引或不可变触发器。

**Acceptance Criteria:**

- **3.1-AC1** — **Given** 空库及含前置User/Device数据的库，**When** 沿单一Alembic链升级，**Then** Booking仅id/user_id/device_id/booking_date/slot/status/start_at/end_at；批准类型精度、八列非空、除Identity id外无默认；slot/status合法值及start_at<end_at CHECK生效。前置数据保留，不以create_all替代迁移。
- **3.1-AC2** — **Given** 真实PG中的有效/无效关联，**When** 写入或尝试父删除，**Then** 两个INTEGER NOT NULL外键为RESTRICT、非延迟、无ON UPDATE CASCADE；无孤立预约，ORM无delete/delete-orphan/all删除级联；加载/未加载关系及集合移除失败后历史保留，错误不当预约冲突。
- **3.1-AC3** — **Given** 相同device_id/booking_date/slot，**When** 写入两条Confirmed或多条Cancelled历史，**Then** 前者被命名的部分唯一索引拒绝，后者允许，Cancelled不占位；不同设备/日期/slot不错误受限，无用户同时段唯一约束。
- **3.1-AC4** — **Given** Asia/Shanghai业务日期与AM/PM，**When** 生成快照，**Then** 分别为08:00–12:00、13:30–17:30的时间点，TIMESTAMPTZ(6)保存，跨主机本地时区结果相同；非法日期/slot拒绝，旧快照不因规则重算，数据库不写死当前时刻的CHECK。
- **3.1-AC5** — **Given** 本人取消/资料编辑等后续业务的写入白名单，**When** 检查模型与接口约束，**Then** 预约七个身份/资源/时间字段普通业务不可改，仅允许Confirmed→Cancelled，不提供物理删除/改约/恢复；数据库约束检查与Service禁止分别留证，不宣称防止特权SQL任意改写。

<a id="s-3-2"></a>

### Story 3.2：分别展示上午和下午可用性

**As a** 已登录普通用户或管理员，**I want** 查询设备某天AM/PM的状态，**So that** 可以判断哪些时段可尝试预约。

**需求/架构**：FR-BOOK-01/07、FR-AUTH-02、NFR-03；AD-2/3/4、R-58、Architecture业务流程。

**依赖**：3.1。

**开发范围**：GET `/devices/<id>/availability`及日期选择/AM/PM展示，由Bookings Service只读Device及Confirmed占用；无占位、预锁或独立资格API。

**Acceptance Criteria:**

- **3.2-AC1** — **Given** Available设备、合法未来日期，AM有Confirmed而PM空闲，**When** user/admin查询，**Then** 200分别显示AM已占用、PM可预约；仅Cancelled时段视为空闲，不返回预约人标识或联系方式。
- **3.2-AC2** — **Given** 同日AM已开始/结束而PM尚未开始，**When** 查询，**Then** AM不可预约，PM独立按占用判定，不使整天失败；恰好08:00/13:30时目标时段不可预约，过去合法日期正常返回不可预约标记。
- **3.2-AC3** — **Given** Disabled设备或非法日期输入，**When** 查询，**Then** 停用设备仍200可见并提示、两半天均不可作为预约选项，非法日期400、设备不存在404；日期解析约定按DP-08，不把过期合法日期当格式错误。
- **3.2-AC4** — **Given** 未认证请求或数据库查询故障，**When** 查询，**Then** 未认证302登录，查询故障按技术错误，不能显示为空闲；模板不隐式查询，本查询无业务写入，不承诺随后创建必成功。

<a id="s-3-3"></a>

### Story 3.3：创建合法预约并安全拒绝冲突

**As a** 普通用户，**I want** 提交合法半天预约并得到准确结果，**So that** 空闲设备时段被可靠保留。

**需求/架构**：FR-BOOK-01/02/03/07、FR-AUTH-02、FR-DEV-03、NFR-01/03；AD-4/5/6、ADR-003/004/006。

**依赖**：3.2；DP-07 的错误原因和时间测试支持设计。

**开发范围**：POST /bookings，可信user授权、锁定字段查询/锁后时间、插入Confirmed、精确索引冲突转换、普通数据/SSR结果提示及提交后PRG。最小成功页可由既有availability GET展示普通安全提示，无需等待个人列表Story。无幂等表、自动重试或用户级互斥。

**Acceptance Criteria:**

- **3.3-AC1** — **Given** user、有效CSRF、Available设备及尚未开始空闲时段，**When** POST创建，**Then** 依次Device FOR SHARE读取必要返回字段检查状态、锁后单独clock_timestamp()严格小于start_at、显式插入Confirmed并由Service提交；持锁到事务结束且不写Device，原POST确认成功后303，展示设备/日期/slot。
- **3.3-AC2** — **Given** 页面旧可用性、客户端伪造user_id/role或旧ORM状态，**When** 创建，**Then** 所有者只取可信Actor，设备状态取锁查询返回字段，实际重新检查时间与唯一性；其他用户先占位时本次409冲突且无第二条Confirmed，不信任页面保证。
- **3.3-AC3** — **Given** 同槽已有Confirmed或同用户重复提交，**When** 请求创建，**Then** 仅D-015目标索引唯一违反在回滚后转换为预约冲突409，安全提示含设备标识/日期/slot，无他人姓名/phone；Device.code、FK、其他CHECK、超时/死锁等不被误归类。
- **3.3-AC4** — **Given** 合法独立初始状态，**When** 在07:30/07:59:59创建AM、12:00/13:29:59创建PM，**Then** 时间资格允许；在08:00:00/13:30:00及以后创建对应时段、过去日期、Disabled设备均拒绝，无部分预约。可控边界与真实PG锁后验证分层，后者见3.6。
- **3.3-AC5** — **Given** user已约设备A，设备B同日期/slot空闲，或同设备不同合法slot/日期，**When** 提交另一个预约，**Then** 可合法创建，不按用户/同设备全局互斥；admin有效CSRF创建403，未认证有效CSRF401，缺令牌400另测。
- **3.3-AC6** — **Given** 写入/提交确定失败或确认未知，**When** 返回HTTP结果，**Then** 确定失败及时回滚、不成功PRG；技术错误及未知按既定500/503分类，未知明确先查询、不断言成功或回滚、不自动重放。仅HTTP状态409不能作为NFR-01冲突证据。

<a id="s-3-4"></a>

### Story 3.4：查看本人完整历史与预约详情

**As a** 普通用户，**I want** 查看自己的预约和当前设备资料，**So that** 能区分有效、取消和已结束记录。

**需求/架构**：FR-BOOK-04/06、FR-AUTH-02、NFR-03；AD-2/3/4、D-023/025/026、R-51/62/70。

**依赖**：3.3；DP-08。

**开发范围**：GET /bookings、`/bookings/<id>`，本人范围、Confirmed可选筛选、稳定排序/分页、计算结束与取消提示、当前设备资料。详情提示不替代取消重检。

**Acceptance Criteria:**

- **3.4-AC1** — **Given** 本人Confirmed/Cancelled/已结束记录和他人记录，**When** 查询，**Then** 只返回本人完整两状态历史；Confirmed筛选仍含已结束但未取消记录，不把“结束”写成Completed或更新数据库。
- **3.4-AC2** — **Given** 相同start_at并列、缺省/边界/非法分页，**When** 查询列表，**Then** start_at DESC,id DESC、LIMIT/OFFSET，page=1/page_size=20默认、1～100合法、非正/非整数/超限400、合法越界200空；空串/重复按DP-08统一约定，不静默裁剪超限。
- **3.4-AC3** — **Given** 他人ID、伪造user_id/URL/参数、admin或未认证请求，**When** 获取本人列表/详情，**Then** 服务端维持本人过滤；他人详情与不存在同类404、admin角色403、未认证302，无他人资料；合法本人读取200配对。
- **3.4-AC4** — **Given** 设备更名/移位/停用，**When** 查看既有预约，**Then** 原device_id及预约快照不变，显示当前名称/位置/状态与停用提示，未取消记录仍Confirmed；列表条目/详情无他人phone，模板不发SQL。
- **3.4-AC5** — **Given** 独立边界场景，**When** 在11:59:59/12:00:00及17:29:59/17:30:00刷新，**Then** 到end_at起可显示已结束且库内状态不变；取消开始边界仍为08:00/13:30，不错用结束时刻。

<a id="s-3-5"></a>

### Story 3.5：锁后检查并取消本人预约

**As a** 普通用户，**I want** 取消本人尚未开始的有效预约，**So that** 保留历史并释放时段。

**需求/架构**：FR-BOOK-05/06、FR-AUTH-02、FR-ADM-04、NFR-01/03；AD-4/5/7、ADR-005/006。

**依赖**：3.4；DP-07。

**开发范围**：POST `/bookings/<id>/cancel`，Booking字段式FOR UPDATE、角色/所有者/状态/锁后新鲜取时、仅status更新、结果分类及原POST证据；无Device锁、改约或恢复。

**Acceptance Criteria:**

- **3.5-AC1** — **Given** 本人Confirmed尚未开始预约，**When** 带有效CSRF取消，**Then** FOR UPDATE锁Booking并读必要字段，核对角色/所有权/Confirmed后单独clock_timestamp()，check_time<start_at才改Cancelled；提交成功303、历史保留，不锁Device。
- **3.5-AC2** — **Given** 独立初始预约，**When** AM在07:59:59、PM在13:29:59检查，**Then** 可取消；在08:00:00、13:30:00及之后（含已结束）409且原状态不变，不用客户端时间/页面时间/事务开始时间。
- **3.5-AC3** — **Given** 已Cancelled、他人ID、不存在ID或admin请求，**When** 取消，**Then** 分别409“已取消，本次未执行”、安全404、404或角色403，无再次成功、无他人信息；未认证有效CSRF401，合法本人配对成功。
- **3.5-AC4** — **Given** 成功或拒绝/失败取消，**When** 对比前后记录，**Then** 七个身份/资源/时间字段逐项不变，只能Confirmed→Cancelled，无User/Device写入；确定回滚时本次Confirmed仍Confirmed并占位，成功提交后新的合法请求可竞争该槽。
- **3.5-AC5** — **Given** 数据库异常或提交确认丢失，**When** 处理，**Then** 无成功PRG或自动重试；Service处理事务，HTTP层只映射，未知与确定回滚分开，不承诺复制Cookie撤销或其他新增安全能力。

<a id="s-3-6"></a>

### Story 3.6：验证设备、创建和取消的真实竞争及时间边界

**As a** 预约用户及管理员，**I want** 相互竞争的操作仍遵守同一规则，**So that** 等待与并发不会产生错误成功或历史破坏。

**需求/架构**：FR-DEV-02/03、FR-BOOK-01/02/03/04/05/06、NFR-01；AD-3～8、ADR-004/005、共用异常与并发验证原则。

**依赖**：2.2、2.3、3.5；DP-05、DP-07。

**开发范围**：测试用同步屏障/可观察等待与独立连接支持、真实PG集成回归及必要缺陷修复，覆盖既定协议；不添加生产睡眠/特殊绕过路径或新锁策略。

**Acceptance Criteria:**

- **3.6-AC1** — **Given** 独立事务/连接和可控同步，**When** 创建先持Device共享锁、停用后到，以及停用先提交、创建后到，**Then** 前者停用等待创建结束且既有预约保留，后者创建读到Disabled拒绝；分别验证创建/停用回滚的后续重检，不用旧ORM状态。
- **3.6-AC2** — **Given** 一个创建事务持有共享设备锁，**When** 同设备另一个合法不同日期/slot的创建运行，**Then** 能在前者结束前完成相应创建，不被不必要排他设备锁串行化；同槽最终最多一Confirmed。
- **3.6-AC3** — **Given** 两个取消请求，**When** 第一取消提交/回滚后释放锁，**Then** 第二分别识别已取消、本次未执行，或重新核对后仍合法才成功；预载旧Confirmed时锁查询也必须看见已提交Cancelled。
- **3.6-AC4** — **Given** 创建/取消在必要行锁上真实等待，**When** 等待跨过start_at，**Then** 取得锁后单独clock_timestamp()重新判定并拒绝；记录取得锁、取时、写入顺序。另以可控时间覆盖小于/等于/大于，不用冻结Python时钟冒充数据库时钟，不只凭固定sleep推断。
- **3.6-AC5** — **Given** 已提交Confirmed，或取消已更新但未提交，**When** 创建竞争同槽，**Then** 前者可直接冲突、不承诺等待未来取消；后者若索引等待则取消提交后重检、回滚后仍占位，实际成功仍需其他资格满足，无自动重试或双Confirmed。
- **3.6-AC6** — **Given** Confirmed/Cancelled/已结束历史及设备编辑/启停，**When** 比较操作前后，**Then** 所有原预约归属、device_id、状态及时间快照依其合法变化保留，设备当前资料展示正确；不存在物理删除/隐式改约/Completed或Cancelled复活。
- **3.6-AC7** — **Given** 每个集成场景已结束，**When** 保存结果与清理，**Then** 记录同步/等待证据、原POST或Service结果和独立连接终态；在途结束且不再写入后才清理专用数据，保留其他历史，未复现真实等待的场景不得写通过。
- **3.6-AC8** — **Given** Disabled设备被admin重新启用且目标未来时段空闲，**When** user创建符合其他规则的预约，**Then** 可以成功Confirmed；已有Confirmed/Cancelled及其快照不被启用恢复或修改，证明启用恢复资格而非只改变状态展示。

<a id="s-3-7"></a>

### Story 3.7：区分确定失败与提交结果未知

**As a** 预约用户，**I want** 失败时得到准确而安全的结果说明，**So that** 不会因误报或自动重发产生错误操作。

**需求/架构**：FR-BOOK-02/03/05/06、NFR-01/03；AD-5/8、ADR-003～006、Architecture故障验证矩阵。

**依赖**：3.5；DP-07 的故障机制由B/C落实。

**开发范围**：故障注入测试支持、错误分类/未知结果表达及连接失效清理验证；实际确认丢失与应用模拟分别留证。不得用生产默认故障开关影响普通请求。

**Acceptance Criteria:**

- **3.7-AC1** — **Given** 创建/取消写入或提交确定失败且已回滚，**When** 请求结束后独立查库，**Then** 创建无本次新行、取消仍原Confirmed并占位、关联/快照/其他历史不变，不报告成功。
- **3.7-AC2** — **Given** 创建已提交但确认丢失，**When** 应用返回并独立核查，**Then** 原POST503明确结果未知/先查询，无自动重试，不断言失败回滚；已提交Confirmed及正确快照仍在。
- **3.7-AC3** — **Given** 取消已提交但确认丢失，**When** 应用返回并核查，**Then** 原POST503独立未知表达，库中Cancelled保留且占位释放，七个其他字段不变；本地rollback/清理不能证明远端未提交。
- **3.7-AC4** — **Given** 锁超时、死锁、池/连接等待超时、非目标唯一/FK/CHECK异常，**When** 分类及诊断，**Then** 按既有暂时技术503或其他内部500处理，不归正常预约冲突、不自动重试，日志无敏感信息；只有目标索引唯一违反回滚后转预约冲突409。
- **3.7-AC5** — **Given** 真实确认丢失和成功提交后人为抛异常两种方法，**When** 编制证据，**Then** 分别记录注入点、机制、原POST、提交证据及独立终态；仅后者不能替代前者。真实场景未完成则对应AC保持待验证，Story不能标全部通过，不阻止记录已有模拟结果。

<a id="s-3-8"></a>

### Story 3.8：正式验证 NFR-01 的逐轮并发一致性

**As a** 用户及验收人员，**I want** 在真实并发竞争下验证有效预约唯一且合法请求可成功，**So that** 不把全量拒绝误认为一致性达标。

**需求/架构**：NFR-01、FR-BOOK-03、SM-01；AD-4/6/8、R-67/69、Architecture NFR交接。

**依赖**：3.6、3.7；DP-09、DP-10。

**开发范围**：C冻结并执行20请求×50轮真实HTTP/PG验证，B配置资源与安全诊断；逐请求/逐轮原始证据与完整失败标准。不是新增写入性能目标。

**Acceptance Criteria:**

- **3.8-AC1** — **Given** 固定提交、精确环境与冻结测试计划，**When** 每轮启动，**Then** 预检Available、尚未开始合法slot且无Confirmed；20独立请求具有有效认证/CSRF并同步起跑，记录起止、轮次、关联信息，实际服务端/PG重叠和等待证明竞争，不能只凭客户端屏障或19个409。
- **3.8-AC2** — **Given** 每轮所有请求已完成，**When** 分类结果并查库，**Then** 恰好1次确认成功（保留原POST303）、19次正常预约冲突、最终1Confirmed，无部分记录；安全原因标识/关联诊断须区分其他409，保持现有HTTP与隐私边界。
- **3.8-AC3** — **Given** 任一轮存在全失败、多成功、非预约冲突、认证/CSRF错、技术错误、未知、超时/未完成或终态错误，**When** 判定，**Then** 该轮及本次50轮测试失败；不自动重试覆盖失败，不能只统计双重预约为0。
- **3.8-AC4** — **Given** 一轮完成或失败，**When** 清理并进入下一轮，**Then** 所有在途已结束/终止且不再写入，仅清本轮隔离数据、确认恢复空闲；其他历史不变。另有不同设备/slot合法请求未被错误阻塞的正向证据。
- **3.8-AC5** — **Given** 50轮原始请求/轮次与最终DB记录，**When** 出报告，**Then** 每轮均满足1/19/1才通过，附提交/机器/版本/线程池PG预算/时间口径/工具/清理记录；无实际结果则状态待执行，不写“并发已通过”。

## Epic 4：管理员识别预约影响并受限协调

用户成果：admin 查询全部预约和停用设备影响，在具体预约详情受限读取联系方式以线下协调；全系统授权与设备查询性能以正式证据验收。

<a id="s-4-1"></a>

### Story 4.1：筛选并分页查询全部预约

**As a** 管理员，**I want** 按已批准条件查询预约，**So that** 能识别记录和预约人并进行线下管理。

**需求/架构**：FR-ADM-01、FR-AUTH-02、NFR-03；AD-1/2/4、D-023、R-51/52/62/70。

**依赖**：3.4；DP-08。

**开发范围**：GET /admin/bookings、日期/设备/状态独立或AND筛选、排序/分页及SSR；Bookings Service所属入口。无新查询维度、通讯录、统计或审批。

**Acceptance Criteria:**

- **4.1-AC1** — **Given** admin及多用户两状态/已结束记录，**When** 无筛选查询，**Then** 200包含授权范围内全部状态及已结束Confirmed，展示设备/日期/slot/status/必要username，无phone或凭据；不把Confirmed等同未来。
- **4.1-AC2** — **Given** 日期起/止、设备id、合法status，**When** 独立或AND组合筛选，**Then** 日期依据booking_date且闭区间含两端，可单端、无两端不限；同日起止含当天、逆序或非法类型/状态400，不新增其他筛选。
- **4.1-AC3** — **Given** 并列start_at、末页不足一页、无数据和筛选后空页，**When** 分页，**Then** start_at DESC,id DESC及LIMIT/OFFSET；page默认1、page_size默认20/最大100，非法400、合法越界200空，行为与3.4相同，不宣称并发跨页同一快照。
- **4.1-AC4** — **Given** user/未认证请求或伪造角色，**When** 直访管理员列表，**Then** user403、未认证302，响应无他人数据；admin合法配对200，Service授权过滤、模板普通数据，数据库故障不伪装空列表。

<a id="s-4-2"></a>

### Story 4.2：识别停用设备未来受影响预约

**As a** 管理员，**I want** 查看停用设备尚未开始的有效预约，**So that** 能准确找到需要线下协调的预约。

**需求/架构**：FR-ADM-02、FR-DEV-03、FR-AUTH-02、NFR-03；AD-2/3/4、D-005/023、R-51/52/62/70。

**依赖**：2.3、4.1。

**开发范围**：GET `/admin/devices/<id>/affected-bookings`，Disabled＋Confirmed＋未来筛选、升序分页与统一停用提示；无预约状态写入/自动改约。

**Acceptance Criteria:**

- **4.2-AC1** — **Given** Disabled设备存在未来Confirmed、未来Cancelled、已开始/过去Confirmed，**When** admin查询，**Then** 仅返回start_at严格晚于查询时刻的Confirmed；恰好开始不算未来，不按booking_date单独推断未来。
- **4.2-AC2** — **Given** 上述结果，**When** 排序/分页及展示，**Then** start_at ASC,id ASC，沿用统一page/page_size边界；显示必要预约人标识、不含phone，不新建“待确认”状态。
- **4.2-AC3** — **Given** Available设备、无受影响记录、设备不存在或非admin请求，**When** 查询，**Then** 前两者200空结果、设备不存在404、user403/未认证302；合法admin场景配对，设备/预约状态与快照全不变。

<a id="s-4-3"></a>

### Story 4.3：受限读取具体预约协调详情

**As a** 管理员，**I want** 在授权的具体预约详情读取当前联系方式，**So that** 可以线下协调而无需扩大列表信息暴露。

**需求/架构**：FR-ADM-01/02、FR-AUTH-02、NFR-03；D-023、AD-1/2、R-29/30/58/61。

**依赖**：4.2；DP-06。

**开发范围**：GET `/admin/bookings/<id>/coordination`，Bookings Service先授权并核对目标预约，再只读其关联User.username/phone；SSR直接完整展示当前号码，不新增用户搜索、修改或取消能力。

**Acceptance Criteria:**

- **4.3-AC1** — **Given** admin和存在的可访问具体预约，**When** 进入协调详情，**Then** 200直接展示对应Booking.user_id的当前username和完整phone，无掩码/二次展开；仅查必要字段，不读password_hash、不写User、不调用Auth Service。
- **4.3-AC2** — **Given** 篡改user_id/他人标识参数、普通用户或未认证访问，**When** 请求详情，**Then** 不能改变Booking关联的读取对象，user403/未认证302、不存在预约404，无任意用户号码检索或越权泄露；admin合法读取配对成功。
- **4.3-AC3** — **Given** 全部/受影响列表、可用性或冲突响应，**When** 与协调详情对比，**Then** 前者均不夹带phone，/devices本人区域例外仅本人；phone不进Actor/Cookie/Session/Booking，模板无SQL，私有缓存策略和日志保护生效。
- **4.3-AC4** — **Given** 协调详情被查看，**When** 核查副作用，**Then** 无代取消、改约、手机号修改、自动通知/状态流转，所有预约数据不变；admin不因此继承user创建/取消权限。

<a id="s-4-4"></a>

### Story 4.4：完成 NFR-03 授权正反配对与 CSRF 验证

**As a** 用户及验收人员，**I want** 验证合法功能可用且直构请求无法越权，**So that** 权限保护不会以全量拒绝冒充成功。

**需求/架构**：NFR-03、FR-AUTH-01/02、FR-DEV-01/02/03、FR-BOOK-04/05/07、FR-ADM-01/02/04；AD-1/2/5、ADR-006/007。

**依赖**：2.2、3.5、4.3；DP-06、DP-10。

**开发范围**：C冻结并执行全部受保护Route的身份/角色/所有权配对矩阵；全部POST CSRF及会话/隐私回归，B支持修复。不是新权限体系。

**Acceptance Criteria:**

- **4.4-AC1** — **Given** 已交付Route表与两名user、一名admin的合成数据，**When** 建立矩阵，**Then** 覆盖未认证设备/时段/个人/管理查询及创建/取消/维护、跨用户URL/ID/参数读与取消、user新增/编辑/启停和管理员查询/协调、admin创建/代取消；每一禁止场景配对至少一个合法成功场景。
- **4.4-AC2** — **Given** 有效CSRF或GET请求，**When** 执行身份/角色/所有权攻击，**Then** 原HTTP响应按302/401/403/404等既定契约拒绝、业务数据不变、无受保护姓名/标识/联系方式；匹配合法请求正常200或修改成功303。不得以通用CSRF400代替授权结论。
- **4.4-AC3** — **Given** 所有POST（login/logout、bookings创建/取消、设备新增/编辑/enable/disable），**When** 分别缺失、无效及有效令牌，**Then** 前两者400且无写入，有效令牌继续身份/业务检查；无豁免、无POST重放，SameSite不替代CSRF。
- **4.4-AC4** — **Given** 绝对期限、活动刷新、Cookie篡改、缓存和日志场景，**When** 回归，**Then** 1.4边界保持；无敏感会话/日志/普通列表字段，只允许本人区域及授权协调详情展示对应号码，模板无隐式SQL；旧Cookie副本不能即时全局撤销的限制如实记录。
- **4.4-AC5** — **Given** 完整矩阵执行记录，**When** C判定，**Then** 所有禁止及合法配对均满足才通过，记录原POST/最终状态/前后数据与脱敏响应证据；漏测、合法失败或全部前置拒绝均不通过，未执行不写成安全已验收。

<a id="s-4-5"></a>

### Story 4.5：正式验证 NFR-02 完整设备列表性能

**As a** 用户及验收人员，**I want** 在约定课程负载下正确查询设备，**So that** 设备列表响应目标有可复核证据。

**需求/架构**：NFR-02、FR-DEV-01、SM-02；AD-1/8、R-61/65～69、Architecture NFR交接。

**依赖**：3.1、4.4；DP-09、DP-10。

**开发范围**：C冻结计划、生成隔离数据、20并发读取压测、正确性与全部样本统计；B提供运行参数和必要查询优化。查询索引只能按实际执行计划评估/审查，不预加、不改唯一性；若修改运行配置，重验受影响NFR。

**Acceptance Criteria:**

- **4.5-AC1** — **Given** 固定提交和精确环境，**When** 准备正式计划，**Then** 使用100台设备、1000条历史预约、20并发读取用户、至少1000正式GET /devices；冻结身份/认证、参数及分页行为、数据生成/预期设备内容、并发模型、工具/机器/线程池PG、预热/超时、计时及连接建立口径。/devices原契约未规定分页，不擅增接口；如没有分页则明确记录“未分页”。
- **4.5-AC2** — **Given** 已登录身份及预热完成，**When** 正式计时，**Then** 从客户端发起HTTP到完整响应体接收、统一毫秒和连接建立口径，包含批准/devices完整响应及本人账号区；登录、初始化、预热不入正式样本，使用合成号码。
- **4.5-AC3** — **Given** 全部正式请求，**When** 检查内容与状态，**Then** 每次为正确200/正确设备与状态及本人区域、无他人资料；超时、网络/认证/HTTP/服务端/内容错误任一出现即失败，全部原始样本保留，不能删失败后只算成功样本。
- **4.5-AC4** — **Given** 全部正确正式样本及预先固定的统计方法，**When** 计算P95，**Then** 建议采用Nearest-Rank升序第ceil(0.95×N)项（1000项取第950项），P95≤1000ms且所有正确才通过；不以平均值替代、不新增预约写入延迟目标，不在运行后换口径。
- **4.5-AC5** — **Given** 报告及优化变更，**When** 审核，**Then** 附完整样本/错误记录/正确性断言、配置及数据版本；需要优化时保留前后证据、审查真实SQL/EXPLAIN ANALYZE/必要迁移并回归功能/权限及受影响并发，不能仅凭本机感觉标通过。

## 依赖关系与建议实施顺序

下表即全部直接硬依赖，`—`表示没有Story依赖；DP门槛见各Story及清单。所有依赖均指向已在编号顺序中出现的Story，无环，无“先实现未来Story才能验收本Story”。

| Story | 直接依赖 | 建议阶段 | 主要交付 |
| --- | --- | --- | --- |
| 1.1 | — | 首批准备 | 锁定环境、装配与启动说明 |
| 1.2 | 1.1 | 首批准备 | User迁移、账号初始化及scrypt配置 |
| 1.3 | 1.2 | Sprint 1候选 | 登录/登出、可信身份及全局CSRF |
| 1.4 | 1.3 | Sprint 1候选 | 绝对期限、安全会话和私有配置 |
| 1.5 | 1.4 | Sprint 1候选 | Device迁移、设备列表及本人资料 |
| 2.1 | 1.5 | Sprint 1候选 | 新增设备 |
| 2.2 | 2.1 | Sprint 1候选 | 白名单编辑 |
| 2.3 | 2.1 | Sprint 1候选 | 条件启停及无变更结果 |
| 3.1 | 1.5 | Sprint 1候选 | Booking迁移、时段/快照和最终唯一性 |
| 3.2 | 3.1 | Sprint 1候选 | AM/PM可用性 |
| 3.3 | 3.2 | Sprint 1候选 | 最小创建闭环及安全冲突 |
| 3.4 | 3.3 | Sprint 2候选 | 本人完整历史/详情 |
| 3.5 | 3.4 | Sprint 2候选 | 本人锁后取消 |
| 3.6 | 2.2, 2.3, 3.5 | Sprint 2候选 | 跨操作PG竞争/边界/历史证据 |
| 3.7 | 3.5 | Sprint 2候选 | 故障注入与未知结果证据 |
| 3.8 | 3.6, 3.7 | 正式验收候选 | NFR-01逐轮证据 |
| 4.1 | 3.4 | Sprint 2候选 | 管理员全部/组合筛选 |
| 4.2 | 2.3, 4.1 | Sprint 2候选 | 受影响未来预约 |
| 4.3 | 4.2 | Sprint 2候选 | 受限协调详情 |
| 4.4 | 2.2, 3.5, 4.3 | 正式验收候选 | NFR-03配对与CSRF证据 |
| 4.5 | 3.1, 4.4 | 正式验收候选 | NFR-02完整样本与P95 |

建议先使E1、E2及3.1～3.3可演示，再完成本人取消与管理协调，最后在冻结版本执行正式NFR。C的计划和数据设计可提前进行，正式执行须等依赖与DP门槛关闭。B应尽早验证3.6/3.7的方法可行性，避免最后才发现真实竞争/确认丢失无法复现；不降低验收要求以赶进度。此处为顺序建议，不是已批准Sprint计划、估算或排期，团队须结合四周/两Sprint容量审核。

## 本阶段交付与审核入口

- [requirements-traceability.md](requirements-traceability.md)：18条需求逐项到Story/AC/架构/验证责任。
- [development-readiness.md](development-readiness.md)：DP-01～DP-11开发准备、配置记录、门槛与待审核实施选择。
- [epics-review-pack.md](epics-review-pack.md)：三方审核清单、反馈格式、文档检查与未完成事项。

本稿未创建业务代码、迁移、真实账号、依赖锁定文件或测试结果，所有功能/运行/NFR状态均待实际实施。21个Story及其覆盖设计的完成不等于21项开发任务已完成。
