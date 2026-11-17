---
name: LabBooking
type: architecture-spine
purpose: build-substrate
altitude: feature
scope: LabBooking 系统级架构约束
status: draft
created: 2026-11-16
updated: 2026-11-17
binds: [Auth, Devices, Bookings]
sources:
  - ../../briefs/brief-LabBooking-2026-11-11/product-brief.md
  - ../../prds/prd-LabBooking-2026-11-12/prd.md
  - ../../decision-log.md
companions:
  - architecture.md
  - ../../project-context.md
---

# Architecture Spine — LabBooking

当前已批准契约；非团队评审或实现验证通过。专题一～五批准的补充已归入AD-1～8，保留原编号和职责，不新增架构决策；“来源”用于溯源，不是继续等待后文覆盖。历史过程保留Decision Log及memlog。AD为稳定约束引用，ADR为取舍记录，不互换。

## Design Paradigm

轻量分层单体：Flask/Jinja2 SSR；Route调用Service，Service访问SQLAlchemy模型/查询和PostgreSQL。Auth、Devices、Bookings按业务归属划分，不按管理员角色复制业务规则。来源 D-011/012。

整体组织方式的正式取舍见[Architecture](architecture.md) ADR-008，来源D-011/012；只补充决策索引，不增加AD或改变规则。Auth/Devices/Bookings共享应用及数据库，不能独立部署/扩缩容；分层不自动保证并发，具体保障仍引用D-015、ADR-004/005。

## Invariants & Rules

### AD-1 — 分层与数据写入归属 [ADOPTED]

- Binds：全部模块，FR-AUTH-02、FR-DEV、FR-BOOK、FR-ADM。
- Prevents：路由绕过服务、跨模块重复写入及循环依赖。
- Rule：Route不访问数据库，Template不查询或隐式加载；Service不互调其他业务Service。Auth拥有身份，Devices独占设备资料/启停写入，Bookings独占预约及管理员预约查询；Bookings可只读Device。模型不导入Route/Service，公共身份契约和数据库设施不反向依赖业务。来源 D-011/012。

来源：专题一：系统整体架构——模块约束；仅合并已批准内容。

- 数据所有权：Auth拥有User/身份/角色，Devices拥有Device，Bookings拥有Booking。身份请求只读，预设账号由初始化流程维护。
- Bookings只读Device必要字段，创建遵守ADR-004；user_id关联User，不赋予任意User读取权；管理员仅必要预约人标识。
- 管理员设备Route归Devices、预约Route归Bookings，无Admin业务模块/Service。
- 少量中立文件定义Actor、数据库扩展、公共时间及错误；不反向依赖业务。返回契约见专题一请求与返回部分，HTTP契约已见Architecture专题三；异常类代码组织由B落实。
- Route调用所属Service，Service不互调，Model不依赖Route/Service，Template不查询，禁止循环导入。模型关系不强迫双向Python导入。
- create_app统一装配配置/扩展/三个模块路由/错误处理，支持测试配置；业务不反向依赖装配入口。
- 不引入Repository基类、Unit of Work、消息队列、微服务或依赖注入容器；出现真实复杂度/明确需求再评估。

### AD-2 — 服务端身份与取消授权 [ADOPTED]

- Binds：Auth、Devices、Bookings，FR-AUTH-01/02、NFR-03、FR-ADM-04。
- Prevents：伪造身份、仅前端授权和管理员代取消。
- Rule：已验证服务端会话生成可信Actor，不信任请求user_id/role；Service检查角色及资源所有权。管理员入口只调用对应服务，不产生代取消权限；查询按PRD最小信息范围。来源 D-009/012/018、D-021。

来源：专题二：数据库设计——D-023联系方式补充约束；仅合并已批准内容。

- Rule：Auth拥有User.phone及本人只读查询；仅中国大陆手机号，预设账号必填/NOT NULL/无默认/非唯一。无应用内用户或管理员修改入口，需求负责人供数据，初始化写入、指定维护人员变更。Bookings仅在具体预约协调详情验证管理员及预约权限后，按该预约user_id只读对应username/phone；不读凭据、不写User、不调Auth Service。普通列表/可用性/冲突及未授权响应无手机号，授权详情直接完整展示，无掩码或二次展开。手机号不进Actor、不复制到Booking，Template仅收授权普通数据。初始化失败无部分账号；真实号码不进公开仓库、日志或测试证据，自动化测试用合成数据。

来源：专题三：认证、安全与SSR接口补充（D-028）；仅合并已批准内容。

- Rule：Flask-Login保持；登录成功绝对2小时，服务端验证截止，活动及Cookie刷新不延长，无Remember-me。Flask原生签名Cookie非加密，不存phone/hash；登出POST只清理当前浏览器，不承诺旧副本即时全局撤销。全局CSRFProtect覆盖所有POST，不为强制401改顺序；缺令牌先400可接受，之后未认证修改拒绝不重放。Werkzeug scrypt；HttpOnly、Lax、HTTPS Secure和私有环境密钥。Auth加载可信User生成Actor，Service继续授权且不依赖current_user。
- Rule：按Architecture Route/权限/HTTP表实现SSR，不建平行JSON API；管理员无创建/取消预约权限。无独立/account页，本人读取按下文当前账号区域；联系方式不进列表/Actor/Booking。200/303成功、302登录引导、400/401/403/404/409拒绝、503暂时技术失败或独立未知结果、500其他内部错误；未知不自动重试或断言回滚。Service事务及ADR-004/005不变。

来源：专题三最终收口（ADR-007及A最终确认）；仅合并已批准内容。

- Rule：继承D-027/028安全方案，独立取舍见architecture.md ADR-007，不改变AD-1～AD-8及原事务/并发。本人username/phone只读放现有已登录业务页，优先/devices的独立当前账号区域，不用/login或/account；Auth在HTTP认证入口准备普通展示数据，不经Devices Service跨调、不进Actor/Session/Cookie、不混列表条目，模板无ORM查询，D-023边界不变。

### AD-3 — 固定时段、状态与历史 [ADOPTED]

- Binds：Bookings、Devices，FR-BOOK-01/04/05/06、FR-DEV-03。
- Prevents：新增生命周期状态、停用隐式取消和规则变更改写历史。
- Rule：slot仅AM/PM；预约仅Confirmed/Cancelled持久化；结束为计算展示。创建统一生成booking_date/slot/start_at/end_at，起止TIMESTAMPTZ；Asia/Shanghai解释业务时间，时间快照普通业务不可变。取消仅改状态，停用不取消/改约既有预约；无动态时段配置或时段版本表。来源 D-002/005/007/008/013/014；时段和时区为课程基线。

来源：专题二：数据库设计——D-024 User字段补充约束；仅合并已批准内容。

- Rule：A确认User五字段。id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY；Booking.user_id同为INTEGER。username VARCHAR(64)/NOT NULL/UNIQUE/无默认，登录去首尾空白并小写，库内规范小写，初始化一致且规范化重名拒绝。password_hash TEXT/NOT NULL/非空白/无默认/非唯一，完整哈希非明文；role VARCHAR(16)/NOT NULL/无默认，CHECK仅user/admin，无角色表。phone VARCHAR(11)，继承D-023非空/非唯一/无默认及访问/维护，应用和数据库基本格式校验，无手机号索引；无+86/空格/连字符。不改变所有权及预约协议。

来源：专题二：数据库设计——D-025 Device字段补充约束；仅合并已批准内容。

- Rule：Device仅id/code/name/location/status。id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY，Booking.device_id同为INTEGER。code VARCHAR(64)/NOT NULL/全表UNIQUE/无默认，大小写敏感精确唯一、保留原大小写，创建后不可改，不用大小写不敏感唯一索引。name/location均VARCHAR(128)/NOT NULL/无默认/非唯一，可由管理员更新；三项业务文本拒绝空串/纯空白。status VARCHAR(16)/NOT NULL/无默认，CHECK仅Available/Disabled。不物理删除，停用不释放code、不改历史Booking；历史关联原设备并展示当前名称/位置/状态，无资料快照或Location表。Devices独占写入，Bookings仅既有只读；ADR-004/005不变。仅主键及code唯一约束所需索引。

来源：专题二：数据库设计——Booking字段技术细化；仅合并已批准内容。

- Rule：Booking仅八字段：id INTEGER ALWAYS Identity PK；user_id/device_id INTEGER；booking_date DATE；slot VARCHAR(2) CHECK AM/PM；status VARCHAR(16) CHECK Confirmed/Cancelled；start_at/end_at TIMESTAMPTZ(6)。八列非空，除id外无默认，创建Service显式Confirmed；CHECK start_at < end_at，D-015 Confirmed部分唯一索引保持。可信Actor确定user_id，关联有效。Service统一生成/校验业务时区快照，旧快照不重算、不用now()默认、不把当前具体时刻写死CHECK。普通业务七字段不可改，取消白名单仅status且仅Confirmed→Cancelled；无改约/转让/恢复，无不可变触发器，不宣称保护任意特权SQL。User/Device及所有并发协议不变，无额外字段或资料副本。

来源：专题二：数据库设计——D-026关系与历史完整性；仅合并已批准内容。

- Rule：两个INTEGER NOT NULL正式外键Booking.user_id→User.id、device_id→Device.id，ON DELETE RESTRICT，非延迟检查，无ON UPDATE CASCADE；Service仍授权/检查状态。三实体主键普通业务不可改，无三实体业务删除入口或管理员删除权限。ORM不启用delete/delete-orphan及包含delete的all；父删除/集合移除不误删历史，可能被NOT NULL/RESTRICT拒绝后回滚，加载/未加载场景必须验证。User无is_active/注册/停用/自行删除，退出失效不在MVP；不删账号/清空字段/转移所有者替代。历史关联及各状态保留，设备展示当前资料、快照不重算、号码不复制。无新增查询索引，D-015与ADR-004/005不变。
- Limits：RESTRICT只保护被引用父记录，不禁止无引用父记录或Booking直接SQL删除；数据库维护权限及清理流程未落实，不宣称全面防删。普通业务主键保护由Service承担，外键只防破坏引用的父键更新。账号不再使用不会自动失效。

### AD-4 — 数据库最终唯一性 [ADOPTED]

- Binds：Bookings，FR-BOOK-03/05、NFR-01。
- Prevents：先查后写竞争和取消历史占位。
- Rule：(device_id,booking_date,slot)仅status='Confirmed'部分唯一；device_id/booking_date/slot/status非空，slot/status数据库合法值限制。仅目标索引唯一违反转预约冲突；取消提交才释放，回滚继续占位。来源 D-015。

来源：专题二：数据库设计——查询契约与设计收口；仅合并已批准内容。

- Rule：本人查询只限本人，管理员按既有授权；历史/Confirmed/管理员全部及筛选start_at DESC,id DESC，受影响未来预约start_at ASC,id ASC。LIMIT/OFFSET，无游标；并列稳定不等于跨页同一快照。管理员仅booking_date日期范围、device_id、status可选AND筛选；无条件含Confirmed/Cancelled，已结束Confirmed不自动排除，未来另要求start_at>查询时刻。JOIN不扩大User读取、列表无phone，联系方式只在D-023授权详情获取。
- Indexes：保留已有主键、唯一约束和D-015，无新增I-1～I-4；其他查询索引留实现测试按真实查询/执行计划评估，原完整性与并发协议不变。

- Rule：LIMIT/OFFSET默认20、最大100，缺省默认，非法/超限400；原排序与状态保留。管理员booking_date日期闭区间含两端，允许单端，两端缺省不限，逆序400；设备/状态仍AND。

### AD-5 — Session与事务拥有者 [ADOPTED]

- Binds：全部数据库业务，FR-AUTH-02、FR-BOOK-02/05。
- Prevents：多次独立提交、认证副作用及请求间Session共享。
- Rule：Flask-SQLAlchemy集成；Auth只读、不提交，可自动开启事务；一个修改请求原则上一个入口Service负责提交/失败立即回滚，Route/辅助查询不自行结束事务，请求结束扩展清理。短请求适用，长请求/后台/流式/认证写入需重评估。来源 D-017/018、ADR-003。

来源：专题一：系统整体架构——请求与返回约束；仅合并已批准内容。

- 统一HTTP保护入口调用Auth只读生成可信Actor；业务Service不互调、仍负责具体授权。
- 未认证GET引导登录，修改拒绝、不重放；认证数据库故障是技术错误。
- Route格式/类型，Service业务/权限/状态/并发资格；返回普通数据或BusinessError，不耦合Flask Response/模板/HTTP码。
- 业务事务由Service结束；HTTP错误处理只转换/诊断，不接管事务、不重试；业务拒绝、目标唯一冲突、技术失败、提交未知遵循共用原则。
- GET渲染、修改成功PRG；拒绝和未知不假成功，Template无数据库/隐式ORM加载。

### AD-6 — 创建设备状态与时间保护 [ADOPTED]

- Binds：Bookings、Devices，FR-DEV-03、FR-BOOK-01/02、NFR-01。
- Prevents：停用/创建竞争、旧ORM状态及事务旧时间。
- Rule：READ COMMITTED在Auth首次查询前配置；创建Device FOR SHARE取返回字段，持锁至事务结束且不写Device；锁后单独clock_timestamp()严格早于start_at。停用Available→Disabled条件UPDATE RETURNING，无返回补查分类，不循环。具体协议见ADR-004及共用异常原则。来源 D-019最终确认。

来源：专题四：业务流程边界补充（D-029）；仅合并已批准内容。

- Rule：code首尾空白显式拒绝、不静默trim；保留大小写敏感精确唯一与创建后不可改，不增字符白名单。已有设备编辑仅name/location，已有status只走启停入口，新增显式合法status；尝试改code整体拒绝无部分修改，夹带status不能绕过入口。
- Rule：重复启停目标已满足返回正常无变更、明确当前状态，不声称本次转换；既有成功页面303机制，不改历史、不自动重试。实际转换仍须提交成功；补查再次变化不当成功，不自动循环，继承ADR-004事务/协调。

### AD-7 — 取消锁后资格 [ADOPTED]

- Binds：Bookings，FR-BOOK-05/06、FR-AUTH-02、NFR-01/03。
- Prevents：重复成功、等待跨开始时间仍取消、扩大设备锁范围。
- Rule：Booking FOR UPDATE直接读必要字段，检查本人/角色及Confirmed，再单独clock_timestamp()；>=start_at拒绝，否则改Cancelled，提交成功才报告。已取消返回本次未执行；不锁Device，不改快照。本次Confirmed取消回滚保留占位，拒绝保持既存状态。来源 D-021、ADR-005。

### AD-8 — 结构迁移与验证边界 [ADOPTED]

- Binds：全部持久化及测试，FR-BOOK-03/04/05、NFR-01。
- Prevents：环境结构漂移、Mock替代并发证据及失败误报成功。
- Rule：开发集成测试统一PostgreSQL；Alembic单链人工审查，无Flask-Migrate/额外封装。验证空库和V1→V2历史保留；真实PostgreSQL独立Session受控测试。错误分类、未知提交及清理见architecture.md共用原则；所有结果待执行。来源 D-016/020、ADR-001/002/004/005。

来源：专题五：工程、运行与NFR（D-030）；仅合并已批准内容。

- Rule：Stack Seed系列与同步驱动统一，精确版本/兼容由B记录C验证；Windows/Conda、独立本地PG、开发/测试库隔离，Waitress用于课程HTTP验收。无强制Docker/Redis/云设施，Windows非唯一产品OS；HTTPS/Secure Cookie不归Waitress终止能力。
- Rule：SQLAlchemy单一有界池及有限等待，总预算计入进程/线程/PG额度；连接/池/锁/SQL/HTTP超时分清、数值校准留证，不改原事务异常语义或自动重试。验收证明实际并发而非线程/池排队串行；Windows IANA时区可用，建议tzdata。
- Rule：私有配置及安全日志，排除凭据/密码/hash/Cookie/CSRF/完整phone；运行与迁移最小权限分离，ADR-001人工审查及迁移保留历史不变。所有部署保护待实现验证。
- Verification：严格PRD NFR-01～03的前置/规模/阈值/失败判定，真实PG、独立有效身份及CSRF、并发证据、完整性能样本和授权正反配对；技术失败/超时/未知不得充业务冲突，不改变阈值或添加写入性能目标。详见Architecture专题五矩阵，均待执行。

## Scope & Conventions

继承D-001～D-010业务基线：自动确认、不逐条审批；无No-Show处罚、不物理删除设备；预设账号、服务端权限；同用户不同设备同半天不构成冲突；设备/时段查询需登录。其余FR按PRD执行，不新增功能或把历史暂定改成已验证。

课程时段08:00–12:00、13:30–17:30，业务时区Asia/Shanghai；20并发请求/50轮、列表P95≤1000ms及完整规模口径按PRD，均非测试结果。实验A保留；实验B按团队范围不开展。

## Stack Seed

Python 3.13；Flask/Flask-SQLAlchemy 3.1；SQLAlchemy 2.0；PostgreSQL 17；Psycopg 3同步；Alembic、Flask-Login/Flask-WTF/Werkzeug、Jinja2 SSR、pytest，保留Tailwind CSS/Lucide。Windows/Conda labbooking、规划environment.yml，Waitress课程HTTP验收。数字为批准系列，具体补丁/其他库版本及安装兼容待B/C落实验证；Windows IANA数据需可用，建议tzdata。来源D-030。

## Deferred & Verification Status

本文件已把后续批准内容归入AD-1～8，保留稳定编号/标题，不新增决策。详细字段表、Route、HTTP和18项需求责任见[Architecture](architecture.md#requirements-map)，过程见[Decision Log](../../decision-log.md)，编码规则见[Context](../../project-context.md)。每个AD内“来源”是批准溯源，不是重新开启专题。

- 实际账号清单仍缺，username ASCII CHECK未批准；phone正则^1[3-9][0-9]{9}$是候选，具体PG表达/约束名称待落实，不证明真实归属。code首尾空白已由D-029收口为显式拒绝，其精确比较/非空白约束表达与编号兼容仍待核查，不自行增加字符白名单或触发器。
- B/C待落实精确版本、兼容与环境复现、ORM加载/删除行为、迁移命名、维护权限/流程、HTTPS接入、运行容量/超时、哈希参数及NFR测量与执行证据。版本系列批准不是安装兼容通过，Service不可变不保护任意特权SQL。
- 课程交接保留实验A准备、真实否决证据、路径例外和团队确认待闭环，实验B不开展；不补造历史。
- 前轮只读lint及独立审查已经执行；本轮整理后机械检查结果记入memlog，完整Reviewer Gate及团队批准尚未完成。status保持draft，不宣称final或测试通过。

## 稳定AD引用索引

| AD | 归并范围与当前依据 |
| --- | --- |
| AD-1 | 分层/所有权/模块/装配；D-011/012、ADR-008、R-15～20 |
| AD-2 | 身份/授权/手机号/浏览器安全；D-023/027/028、ADR-007、R-27～35/53～62 |
| AD-3 | User/Device/Booking字段、外键/删除/历史；D-013/014/024～026、R-32～50 |
| AD-4 | 唯一性/查询/分页；D-015、查询最终确认、R-51/52/62 |
| AD-5 | 数据库Session/请求/异常；D-018/022、ADR-003/006、R-21～26/59 |
| AD-6 | 创建/设备协调及维护边界；D-019/029、ADR-004、R-63/64 |
| AD-7 | 取消锁后资格与释放；D-021、ADR-005、R-11～14 |
| AD-8 | 迁移/运行/NFR；D-016/020/030、ADR-001/002、R-65～69 |
