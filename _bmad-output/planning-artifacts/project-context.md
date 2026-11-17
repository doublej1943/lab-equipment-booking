---
status: draft
updated: 2026-11-17
---

# LabBooking 项目上下文（部分草稿）

已同步专题一～五批准的规则及版本系列；精确补丁版本、兼容性和环境复现证据待B落实、C验证，不视为课程Context最终验收或测试通过。

## 技术基线

Python 3.13系列；Flask/Flask-SQLAlchemy 3.1系列；SQLAlchemy 2.0系列；PostgreSQL 17系列，Psycopg 3同步驱动；Alembic、Flask-Login、Flask-WTF、Werkzeug、Jinja2 SSR、pytest，保留Tailwind CSS/Lucide。Windows/Conda labbooking、规划environment.yml；Waitress用于课程HTTP验收。具体补丁及未指定库版本由B固定记录、C验证，均未声明已安装/兼容；Windows需可用Asia/Shanghai IANA数据，建议tzdata。来源D-030。

## 规则阅读与状态索引

以下规则按批准顺序保留历史原文。早期规则中的部分待定事项已由后续批准规则收口，当前实现按下表读取；仅表中列明的部分被细化，其他原始内容继续有效。不得仅凭编号较新就推断其覆盖整条旧规则。架构设计已确定不代表代码、迁移或测试已完成。

| 历史规则 | 已收口或细化的内容 | 当前有效依据 |
| --- | --- | --- |
| R-32 | Booking.user_id 的正式外键及删除动作已确定；User 字段契约保持。 | R-46：INTEGER、NOT NULL、ON DELETE RESTRICT、非延迟检查，不配置 ON UPDATE CASCADE。 |
| R-34 | 密码哈希算法已确定，具体参数仍待落实；字段及角色约束保持。 | R-57：Werkzeug scrypt，参数由 B 按官方规范落实。 |
| R-36 | Booking.device_id 的正式外键及删除动作已确定；Device 字段契约保持。 | R-46：INTEGER、NOT NULL、ON DELETE RESTRICT、非延迟检查，不配置 ON UPDATE CASCADE。 |
| R-37 | code 首尾空白策略已确定：拒绝，不自动 trim；原大小写敏感、不可修改规则保持，未新增字符白名单。 | R-63。 |
| R-40 | code 空白及编辑业务边界已明确；数据库约束具体表达、命名及额外不可变保护机制仍待落实或核查，不视为已批准新增机制。 | R-63；R-40 其余约束继续有效，查询索引按 R-52 留实现测试评估。 |
| R-45 | 正式外键与 ON DELETE 已确定；Actor、字段范围、隐私及验证责任保持。 | R-46。 |
| R-50 | 查询索引处理及最小权限原则已明确；具体权限配置、维护清理流程和索引验证仍待完成。 | R-52：保留已有索引，其余按真实查询及执行计划评估；R-68：应用运行与迁移权限最小分离。 |
| R-51 | 分页数量已确定；稳定排序、LIMIT/OFFSET 及跨页快照限制保持。 | R-62：默认每页 20、最大 100，非法或超限返回 400。 |
| R-52 | 日期范围端点已细化；AND 筛选、状态、授权、隐私及索引策略保持。 | R-62：booking_date 闭区间，可单端，无两端则不限日期，开始日晚于结束日返回 400。 |
| R-53 | 密码算法已确定，具体参数仍待落实；身份加载及 Actor／Service 授权边界保持。 | R-57：Werkzeug scrypt。 |
| R-54 | 已确定固定两小时的起算、刷新边界及 Cookie／密钥安全原则；数据库 Session 边界保持。 | R-56：登录成功起算绝对两小时，不随活动或 Cookie 刷新延期；R-57：Cookie 安全及私有密钥原则。 |
| R-55 | 安全架构、Route／HTTP 契约及版本系列已确定；精确版本、参数、部署配置和实际验证仍待落实。 | R-56～R-59：会话、安全、入口与错误映射；R-65：版本系列及复现责任。 |
| R-58 | 本人手机号只读展示位置已明确，不扩大联系方式权限或新增编辑功能。 | R-61：已登录业务页面优先 /devices 的当前账号区域，由 Auth 准备普通展示数据。 |
| R-60 | 分页数量及日期端点已确定；隐私、授权／CSRF 分开验证及待实现状态保持。 | R-62：默认 20、最大 100 及日期闭区间；R-61：本人信息展示边界；R-65：版本系列，精确版本和配置仍待落实。 |

R-46、R-56、R-62 是当前有效依据，不是过期规则。username ASCII 字符 CHECK、手机号数据库校验的具体表达及命名等未批准或待核查事项，不因本索引而自动确定。

## 已确认实现规则

- R-01：Engine 初始化固定 READ COMMITTED，早于 Auth 首次数据库查询；验证连接池复用。来源 ADR-004、D-019最终确认。
- R-02：Auth 只读生成可信 Actor，不信任请求 user_id/role；不提交。来源 D-012、D-018。
- R-03：一个修改请求原则上仅一个入口 Service 拥有提交/失败回滚；Route和查询辅助函数不自行结束事务，请求结束扩展清理。来源 ADR-003、D-018。
- R-04：创建按设备 ID FOR SHARE 直接读取字段，不用旧 ORM 属性，不写 Device，持锁至事务结束。来源 ADR-004。
- R-05：停用条件 UPDATE Available→Disabled RETURNING；无返回补查字段区分不存在、已停用、再次变化，不自动循环。来源 ADR-004。
- R-06：锁后独立 clock_timestamp()，严格早于 start_at；不用 now()/CURRENT_TIMESTAMP或缓存时间。Asia/Shanghai 生成解释快照，不增提交截止规则。来源 ADR-004、D-014。
- R-07：D-015 的 Confirmed 条件组合唯一索引、四列非空及slot/status合法值必须在数据库落实；只转换目标索引唯一违反。
- R-08：仅提交成功报告成功；锁超时、死锁和其他数据库错误回滚、不自动重试、不混同业务冲突；提交结果未知需明确，不断言回滚。来源 ADR-004。
- R-09：停用不取消或改约预约；取消只改状态不改时间快照，成功提交才释放占位。来源 D-005、D-014/015。
- R-10：C 用真实 PostgreSQL、独立 Session及受控屏障验证竞争；无实现/执行证据不得写通过。具体等待数值另议。来源 ADR-004。

## 引用

架构：[architecture.md](architecture/architecture-LabBooking-2026-11-16/architecture.md) ADR-003/004；日志：[decision-log.md](decision-log.md) D-012、D-014/015、D-018/019。版本基线和其余项目规则后续补齐。

ADR索引补充：整体轻量分层单体的选择与备选取舍见同一Architecture的ADR-008，引用D-011/012；继承ADR-003～007具体机制。本次只补索引，不追加R规则、不重做技术选择；团队评审、实现及测试仍待完成。

## 取消预约补充规则

保留 R-01～R-10；以下仅同步已批准的 D-021、ADR-005。

- R-11：取消使用 Booking SELECT FOR UPDATE直接返回 id/user_id/status/start_at；Service检查可信角色与本人、Confirmed，不使用旧 ORM属性，管理员不得代取消。
- R-12：取消锁后单独 clock_timestamp()；check_time >= start_at 含等号一律拒绝。仅通过后改 Cancelled，不锁 Device、不改时间快照。
- R-13：取消提交成功才报告成功；本次从 Confirmed尝试取消的事务回滚仍占位，其他拒绝保持已有状态。重复取消返回已取消、本次未执行，不计再次成功。
- R-14：提交确认丢失为结果未知，不等同确定回滚；异常与取消/创建竞争测试遵循 architecture.md“共用异常与并发验证原则”。

引用：D-021；ADR-005及共用原则。以上为确认设计，实现、测试与团队评审待完成，非依赖版本或HTTP契约批准。

## 专题一：系统整体架构——模块实现规则

A于2026-11-17确认，R-01～R-14保持不变。

- R-15：Auth拥有User/身份/角色，Devices拥有Device，Bookings拥有Booking；Auth请求身份加载只读，预设账号通过初始化流程维护，不新增账号管理功能。
- R-16：Bookings仅只读Device必要字段，创建遵守ADR-004；Booking以user_id关联User，管理员查询默认必要预约人标识，不开放任意个人信息读取。
- R-17：设备管理Route归Devices，预约管理Route归Bookings，不建Admin业务模块或Admin Service。
- R-18：Actor、数据库扩展、时间规则和公共错误定义使用少量中立文件，不依赖业务模块；返回契约见专题一请求与返回部分，具体继承与HTTP映射后续确定。
- R-19：Route调用所属Service；Service不互调；Model不反向依赖上层；禁止循环导入及业务反向导入应用装配入口。模型数据关系不要求双向类导入。
- R-20：create_app统一加载配置、初始化扩展、注册三个模块Route和错误处理，支持测试配置；不引入Repository基类、Unit of Work、消息队列、微服务或容器，真实需求出现再评估。

来源：architecture.md“专题一：系统整体架构”及A七项确认。实现/验证待完成；专题一请求与返回部分返回契约现已由D-022/ADR-006批准。

## 专题一：系统整体架构——请求与返回规则

R-01～R-20规则不变；R-18的契约待定说明已更新为本次批准状态。

- R-21：统一HTTP认证入口调用Auth只读加载身份生成Actor，显式传业务Service；业务Service不调用Auth或其他业务Service，仍检查具体授权。
- R-22：未认证受保护GET引导登录，修改拒绝不重放；身份查询数据库失败为技术错误，不伪装未认证。
- R-23：Route处理HTTP解析/格式/类型，Service负责业务/角色/所有权/资源状态/并发资格；格式合法不等于业务合法。
- R-24：正常返回普通数据，预期拒绝抛轻量BusinessError；不返回Flask Response、不在Service渲染或决定HTTP码，不增结果对象框架。
- R-25：Service结束业务事务；HTTP错误处理只映射及安全诊断，不接管事务或自动重试。精确识别D-015；技术失败与提交未知分别处理，未知非确定回滚。
- R-26：GET成功Route渲染Jinja2，修改提交成功才PRG；拒绝/技术失败/未知不伪装成功，模板不隐式查询。具体HTTP码/Route表/页面细节待后续。

来源：D-022、ADR-006及architecture.md专题一请求与返回部分；团队评审、实现与测试待完成。

六专题名称与未完成任务统一见 architecture.md 的“六专题规划与进度”；R-01～R-26技术含义不变。

## 专题二：数据库设计——User联系方式规则

A最终确认，来源D-023；R-01～R-26原文保留，以下追加限定边界。

- R-27：User.phone仅中国大陆手机号，预设账号必填、NOT NULL、无默认、不设UNIQUE，允许同号，不作登录凭据；无姓名/邮箱/短信验证。VARCHAR长度、正则和数据库CHECK仍待审查。
- R-28：Auth拥有User及本人手机号只读查询；普通用户只看本人完整号码，用户和管理员均无应用内修改功能。需求负责人提供初始化资料，指定维护人员变更；身份加载只读及D-018不变。
- R-29：Bookings仅在具体预约协调详情验证管理员及目标预约权限后，按Booking.user_id只读对应User.username/phone；不任意读取User、不读password_hash、不写User、不调用Auth Service，不扩大管理员权限。
- R-30：普通预约/设备列表、可用性、冲突及未授权响应不含手机号；授权协调详情直接完整展示，无掩码/二次展开。Template仅收授权普通数据、不查询；号码不进Actor或Booking。
- R-31：初始化全部校验，失败无部分账号，拒绝空串/非法格式/虚构占位；格式不证明真实或归属。真实号码不进公开Git、普通测试数据、错误日志和测试截图，自动化测试用合成数据。无手机号修改页/接口，不把密码重验或该修改接口CSRF列待办；通用安全设计另议。

完整字段/校验/约束、维护流程、Route/HTTP及通用安全配置待后续；团队评审、实现和测试待完成。参见architecture.md专题二User联系方式及Spine D-023补充约束。

## 专题二：数据库设计——User完整字段契约（D-024）

保留R-01～R-31原文；R-27和上段中字段类型尚待审查的历史状态由本次细化，权限和维护规则不变。A已确认；团队评审、实现和测试待完成。

- R-32：User仅id/username/password_hash/role/phone五字段。id为INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY；Booking.user_id同为INTEGER，正式外键及删除动作留关系专题，不擅自决定。
- R-33：username为VARCHAR(64)、NOT NULL、UNIQUE、无默认；登录输入去首尾空白并统一小写，存储规范小写账号，初始化遵循一致规范、重名拒绝并报告。仓库无实际账号清单，ASCII小写字母/数字/下划线CHECK未批准；不得擅自生成、改名或放宽规则。
- R-34：password_hash为TEXT、NOT NULL、非空白、无默认、不唯一，完整保存哈希而非明文，不截断/小写化哈希，算法另议；role为VARCHAR(16)、NOT NULL、无默认，CHECK仅user/admin，无独立角色表；角色来自可信服务端数据。
- R-35：phone为VARCHAR(11)，继承D-023非空/非唯一/无默认及权限；仅11位国内号码，无+86/空格/连字符；应用与数据库基本格式校验，不增手机号索引。^1[3-9][0-9]{9}$为候选，PostgreSQL正则表达、CHECK命名和迁移待核查，不能证明真实归属。

来源D-024及architecture.md的User完整字段契约；B落实、C在真实PostgreSQL核查结构和行为，均未执行。不改变ADR-001～006或R-01～R-31，不将本人手机号修改恢复为待办。

## 专题二：数据库设计——Device契约（D-025）

A正式确认；R-01～R-35原文保留，团队评审、实现与测试待完成。

- R-36：Device仅id/code/name/location/status。id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY；Booking.device_id同为INTEGER，正式外键及删除动作待关系专题。
- R-37：code VARCHAR(64)、NOT NULL、全表UNIQUE、无默认，拒绝空串/纯空白，创建后不可修改；保留原大小写，大小写敏感精确唯一，不转大小写、不用大小写不敏感唯一索引。首尾空白策略未定，不静默trim；实际编号清单/字符白名单未核查，不擅自改号。
- R-38：name/location均VARCHAR(128)、NOT NULL、无默认、不唯一，拒绝空串/纯空白，管理员可修改，不建Location表。历史Booking关联原Device.id，显示当前名称/位置/状态，不增资料快照。
- R-39：status VARCHAR(16)、NOT NULL、无默认，CHECK仅Available/Disabled；创建、停用及事务继续ADR-004，不以合法值约束代替并发协议。仅Devices写Device，Bookings受限只读。
- R-40：不物理删除设备，停用不释放code或改变历史预约；Service拒绝改code，唯一性不等于不可变数据库保护。仅主键/code唯一约束所需索引，无重复code索引，其他查询索引后议；无描述/型号/停用原因字段。精确比较实现、空白CHECK/命名及数据库不可变保护待核查，所有实现和测试待完成。

来源D-025、architecture.md Device完整字段契约及Spine补充；不改变User契约、D-015唯一索引、D-018事务或ADR-004/005。code首尾空白策略仍需明确后再落实。

## 专题二：数据库设计——Booking字段契约技术细化

A最终批准并要求集中写入Architecture，不新增D-log或D-026；继承D-013/014/015/018/019/021～025。R-01～R-40原文保留，团队评审、实现及测试待完成。

- R-41：Booking仅id/user_id/device_id/booking_date/slot/status/start_at/end_at。id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY；两个关联ID为INTEGER，booking_date DATE，slot VARCHAR(2)，status VARCHAR(16)，起止TIMESTAMPTZ(6)。八列NOT NULL，除id生成外均无数据库默认，创建Service显式写Confirmed。
- R-42：数据库CHECK仅允许slot AM/PM、status Confirmed/Cancelled，并要求start_at < end_at；保留D-015 Confirmed条件三列唯一索引，不能改为全表唯一或增加用户同时段唯一。索引错误精确分类及事务规则不变。
- R-43：Service按统一业务时区生成/校验日期、slot和起止快照，旧快照不因规则变化重算，不用now()默认，不将当前具体时刻永久写死CHECK；起止顺序不是完整一致性保证，保留ADR-004/005锁后新鲜取时。
- R-44：普通业务不得改id/user_id/device_id/booking_date/slot/start_at/end_at；取消白名单仅status，遵守Confirmed→Cancelled，不允许反向恢复；无编辑/改期/换设备/转让。MVP以Service和测试保护，不加不可变触发器，不宣称数据库已禁止特权SQL改快照。
- R-45：创建user_id来自可信Actor，关联必须有效；User/Device类型不改，正式外键及删除动作待关系专题，不批准任何ON DELETE。无created_at/cancelled_at或用户/设备资料副本，号码不入Actor/Booking；额外查询索引后议。B落实、C在真实PostgreSQL验证结构、非法值/组合、白名单、历史保留及既有并发协议，均待执行。

来源architecture.md Booking完整字段契约、Spine技术细化及本轮A确认（memlog）；Decision Log截至D-025不改。约束/索引命名、迁移表达及正式关系保护后续确定，不进入代码实现。

## 专题二：数据库设计——三实体关系与完整性（D-026）

A最终批准；R-01～R-45原文保留，先前外键待定说明由本条关系决定收口。“不创建D-026”为此前Booking字段轮次的历史，本次D-026仅记录关系/删除保护。团队评审、实现与测试待完成。

- R-46：Booking.user_id→User.id、device_id→Device.id为正式INTEGER NOT NULL外键，均ON DELETE RESTRICT、非延迟检查，不配置ON UPDATE CASCADE；每条Booking必须关联存在的User/Device。外键不替代Service授权、状态或时间检查。
- R-47：User.id/Device.id/Booking.id不通过普通业务修改，不通过换主键处理生命周期。数据库外键只限制破坏引用的父键更新，不宣称禁止所有ID变更；Service承担普通业务主键保护。
- R-48：MVP无User/Device/Booking物理删除页面、接口或管理员删除权限；所有Confirmed/Cancelled及已结束预约均保留。两条ORM关系不启用delete/delete-orphan或包含delete的all，不因父删除/集合移除误删Booking。无级联不保证操作成功，可能NULL化外键或删除父记录而被NOT NULL/RESTRICT拒绝，须回滚保留历史；覆盖加载/未加载关系验证。
- R-49：不新增User.is_active、注册、停用或自行删除，账号退出/失效不在MVP，不以删除/清空字段/改预约所有者替代；不宣称账号不再使用会自动失效。历史保留原关联，设备展示当前资料、起止快照不重算，手机号不复制。
- R-50：本轮不新增查询索引，按下一专题实际WHERE/ORDER BY/分页/规模及EXPLAIN ANALYZE集中设计，D-015保留不重复。B人工审查迁移及ORM配置，C真实PostgreSQL验证外键/删除/无更新级联/加载场景/迁移和原并发；外键错误不算D-015冲突。RESTRICT不保护无引用父记录或直接删Booking，直接SQL维护权限和清理流程仍待环境设计，不宣称已部署全面防删。

来源D-026、architecture.md三实体关系与完整性及Spine；不改变字段/快照/Session/并发协议，无新增ADR。数据库实现及功能测试未开展。

## 专题二：数据库设计——查询契约补充

保留R-01～R-50，追加此前未规定的排序/分页/筛选契约；不重复扩展既有权限。

- R-51：历史/Confirmed列表、管理员全部/筛选按start_at DESC,id DESC；受影响未来预约按start_at ASC,id ASC。start_at非创建时间，不加字段；LIMIT/OFFSET无游标，页大小/最大限制留接口设计。并列排序确定不保证并发跨页同一快照。
- R-52：管理员仅booking_date日期范围、device_id设备、status状态可选筛选，独立或AND组合；无筛选含Confirmed/Cancelled，已结束Confirmed不自动排除，未来另以start_at>查询时刻判断。本人范围与D-023不变，JOIN不扩phone读取、列表无phone。保留既有主键/唯一约束及D-015，其余索引留实现测试按真实查询和计划决定，不预增I-1～I-4。

来源A本轮确认、Architecture查询/收口章节及memlog；不新增D-log/ADR。专题二设计阶段完成，遗留核查仍见Architecture；团队评审、实现、迁移及性能/功能测试待完成，不将设计收口写成验证通过。

## 专题三：认证与浏览器会话第一轮（D-027）

保留R-01～R-52；A确认组件与时长，未批准其他启动候选；团队评审、实现和测试待完成。

- R-53：采用Flask-Login管理登录状态；Auth验证凭据、从数据库只读加载可信User，以现有password_hash核验，密码算法/参数另定。构建Actor显式传所属Service，角色/资源所有权/业务资格仍由Service检查，业务Service不依赖current_user；不因扩展接口新增User.is_active字段。
- R-54：浏览器登录Session有效期2小时、不启用Remember-me，不存phone/password_hash等敏感信息；固定/滑动、起算/刷新/过期计算和Cookie/密钥管理仍待确认，不以默认值或session.permanent擅自落实。不得将两小时套到SQLAlchemy事务/连接，D-018请求内Session及Service提交/回滚保持。
- R-55：Flask-Login接入须遵守D-022未认证GET引导/修改拒绝且不重放，认证数据库故障仍为技术错误；模板无隐式ORM加载、D-023手机号及Actor边界不变。Cookie、CSRF、Route/HTTP、密码算法/参数及版本未定，不因本次安装依赖或增加功能；B/C后续按确认计时方式验证时效，无实施/测试通过结论。

来源D-027、Architecture专题三认证章节及Spine；无新增ADR，原字段、事务与并发规则不变。

## 专题三：认证、权限与SSR接口收口（D-028）

保留R-01～R-55原文；本节收口R-54/55中的计时、安全组件和响应待定项，不改变旧轮次事实。A已批准，团队评审、实现与测试待完成。

- R-56：登录成功起算绝对2小时，服务端逐受保护请求验证截止，达到截止即失效；活动、flash或Cookie重签发不延期，无Remember-me。使用Flask原生签名Cookie，签名非加密，身份/计时/必要安全状态之外不放phone/hash或个人资料；从数据库构建可信Actor，角色不信客户端。登出POST清理当前浏览器，不宣称旧副本全局即时撤销，不新增会话表。
- R-57：Flask-WTF全局CSRFProtect覆盖全部POST含登录登出；不为固定未认证401调整执行顺序或豁免POST。缺失/无效令牌400，CSRF通过后未认证修改401且不重放。Werkzeug scrypt生成/核验现有password_hash，不存明文；HttpOnly、SameSite=Lax、HTTPS部署Secure、私有环境密钥，B按官方规范落实版本/参数和开发配置，不把本地HTTP例外用于部署。
- R-58：采用Architecture专题三Route表的SSR/Jinja2/表单POST，无平行JSON API；GET不改业务数据。user仅本人预约，admin不得创建/取消预约；设备管理归Devices，预约/可用性/协调归Bookings，业务Service只接Actor并授权，不依赖current_user。无独立/account页面；D-023本人完整手机号只读由Auth现有页面承载，布局交B，不增编辑功能。
- R-59：HTTP统一映射200读取、303修改成功、302未认证GET、400参数/CSRF、401无效凭据或通过CSRF后未认证修改、403角色拒绝、404不存在/他人个人预约、409业务状态或精确唯一冲突、503暂时技术失败/提交未知、500其他内部错误。未知有独立安全表达，不自动重试，不断言成功或回滚；Service无Response/HTTP决策，处理器不接管事务。原D-015冲突识别、D-018事务和ADR-004/005保持。
- R-60：Route/权限/错误以Architecture D-028补充为当前契约，旧“未定”按本节理解；列表无phone，协调详情受限，模板普通数据。C以有效CSRF分别验证未认证/角色/所有权，另验证全部POST CSRF，不能把前置拒绝当业务授权通过。分页数量/上限、日期端点仍待确认，不使用20/100等推荐数值作批准；算法参数/版本、配置和本人信息布局交B落实记录，均无测试通过结论。

来源：[Architecture](architecture/architecture-LabBooking-2026-11-16/architecture.md)专题三D-028补充；[Decision Log](decision-log.md) D-028。无新增ADR或字段，既有数据库与并发协议不变。

## 专题三最终收口补充

保留R-01～R-60历史原文；R-58中“Auth现有页面”及R-60未定项以A本轮确认的下列规则为准。认证取舍正式记录于Architecture ADR-007，来源D-027/028；本轮不新增D-log。

- R-61：在现有已登录业务页面优先/devices设置当前账号只读区域，仅本人username和完整phone；不使用GET /login展示、不新增/account或编辑功能。Auth通过统一HTTP认证入口准备独立普通展示数据，页面接收，不让Devices Service调用Auth Service或读取User；模板无ORM查询。phone不进Cookie/Session/Actor，不混入列表条目或可用性，D-023协调详情权限不变，布局由B落实。
- R-62：LIMIT/OFFSET默认每页20、最大100，缺省默认，非法或超限400；R-51/52排序、授权和状态语义不变。管理员booking_date范围为包含两端的闭区间，可单端、双端缺省不限制，开始日晚于结束日400，其他筛选仍AND。参数命名/正常配置交B，C验证边界及隐私，未执行。

专题三架构设计完成，团队评审、代码及验证待完成；版本/参数/配置落实不等于已批准执行结果。历史“认证未定/不新增ADR”是当时状态，当前以ADR-007及本节为准，不修改既有事务/并发协议。

## 专题四：业务流程与边界（D-029）

保留R-01～R-62；R-37/40中的code首尾空白待定由本节收口，原协议不变。

- R-63：新增Device.code有首尾空白即明确拒绝，不自动trim，拒绝空串/纯空白；原大小写敏感精确唯一、保留大小写、不可改不变，不额外引入字符白名单。已有设备普通编辑仅name/location，status只走专门启停入口；新增显式提供合法status。篡改code整体拒绝且无部分资料修改，编辑夹带status不得绕过入口或白名单，整体拒绝；具体输入校验由B落实。
- R-64：启停目标状态已满足时返回正常无变更结果，明确当前已启用/停用，不计本次状态转换；走既有303 PRG，不改历史、不自动重试。实际转换提交成功才报告，区分不存在、已在目标状态及补查再次变化，后者不能误报本次成功或自动循环；继承ADR-004及Service事务/异常边界，C验证重复/竞争/失败和无部分写入，均待执行。

来源：[Decision Log](decision-log.md) D-029；[Architecture](architecture/architecture-LabBooking-2026-11-16/architecture.md)专题四流程表。其余流程直接继承既有ADR/规则，不复制或新建协议。专题四架构设计完成，团队评审、实现与验证待完成，无新增ADR。

## 专题五：工程与运行约束（D-030）

保留R-01～R-64原文；版本系列按当前技术基线，精确版本/参数由B落实并记录，C复现验证，不将历史“版本待定”当作系列仍未批准。

- R-65：统一上述系列、Psycopg 3同步访问及Conda labbooking；环境复现使用规划environment.yml管理，B锁定具体依赖/版本，C干净环境验证。Windows必须能加载Asia/Shanghai IANA数据，建议tzdata，不依赖开发机本地时区；不因版本系列已批准声称安装或兼容通过。
- R-66：Windows/Conda为团队开发和课程验收基线，开发/测试PG数据库隔离且同一批准系列/迁移；Waitress运行HTTP验收，Flask开发服务器只调试。Windows非产品OS限制，不强制Docker/Redis/云；外部部署HTTPS及Secure Cookie按原规则，Waitress不承担HTTPS终止承诺。
- R-67：SQLAlchemy单一有界连接池、有限等待，不额外叠加驱动连接池；按进程数计算池及溢出总预算并考虑线程/PG额度。分别配置连接、取连接、锁、SQL和HTTP超时，数值由B/C在正式环境校准记录；保留READ COMMITTED/Service事务及原异常语义，不自动重试预约。验收须证明实际数据库竞争，不能以默认线程数或池瓶颈把20请求串行化后声称并发通过。
- R-68：私有环境提供密钥和DB凭据，无真实秘密入Git；日志不记录密码/hash/Cookie/CSRF Token/完整phone/连接凭据。应用运行账号与迁移权限最小分离，不以超级用户运行应用；B落实权限，C检查，未宣称已部署。迁移单链及人工审查继承ADR-001，B维护、A审查设计、C验证空库/升级保留数据，不以create_all替代迁移。
- R-69：NFR严格按PRD：01为20独立有效认证请求50轮、每轮1成功19预约冲突最终1Confirmed，真实同步竞争/隔离数据/完成后清理，错误超时未知不计冲突；02为100设备1000历史20并发读取至少1000正式请求P95≤1000ms且全部正确，固定环境/参数/计时/完整样本，登录初始化预热排除；03授权合法/禁止配对，另测CSRF。C记录原POST/最终状态及完整证据，参数和测量方法先固定，不改阈值，不新增写入性能目标，均待执行。

来源：[Architecture](architecture/architecture-LabBooking-2026-11-16/architecture.md)专题五及[Decision Log](decision-log.md) D-030。专题五架构设计完成，团队评审、环境/代码和NFR实际验证待完成，非整份Architecture验收通过。
