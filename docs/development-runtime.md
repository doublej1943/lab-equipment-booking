# Windows 开发准备与独立复现（DP-01、DP-02）

本交付基于 PR #4 定稿提交 `f54d1a6`。从仓库根目录执行下述 PowerShell 命令。B 的验证覆盖运行依赖和密码策略，C 在另一套干净环境中复现后补上独立结论。

## 版本和来源

| 用途 | 精确版本 |
| --- | --- |
| Python / pip | 3.13.18 / 26.2.2 |
| Flask / Flask-SQLAlchemy / SQLAlchemy | 3.1.3 / 3.1.1 / 2.0.54 |
| PostgreSQL 服务端 | EDB Windows x64 17.12-2，服务端版本 17.12 |
| Psycopg / psycopg-c / libpq | 3.2.10 / 3.2.10 / 17.12，同步 `postgresql+psycopg` |
| Werkzeug / Flask-Login / Flask-WTF / Jinja2 | 3.1.9 / 0.6.3 / 1.3.0 / 3.1.6 |
| Alembic / Waitress / pytest | 1.20.1 / 3.0.2 / 9.2.0 |
| Windows IANA 数据 | Python 包 tzdata 2026.6（Conda 包名 python-tzdata），Conda tzdata 2026e |
| 前端构建 | Node.js 24.22.3，随包 npm 11.19.1，Tailwind CSS 和 CLI 均为 4.3.5，lucide-static 1.80.0 |

[environment.yml](../environment.yml) 记录直接依赖。[Windows 锁文件](../conda-win-64.lock) 记录 60 项 Conda 包的官方渠道地址、平台、构建及 SHA-256。[npm 锁文件](../package-lock.json) 固定前端包及其传递依赖和完整性校验值。Node 仅用于构建本地 CSS 和取得 SVG；页面运行时可直接引用生成的静态文件。数据库是独立的本机进程。

## 重建环境

在已初始化 Micromamba 的 Windows x64 PowerShell 中使用一个尚未占用的环境名。B 使用 Micromamba 2.10.0 完成复现。若本机已有 labbooking，请改用新的环境名并相应调整第二行。

```powershell
micromamba create -y -n labbooking -f conda-win-64.lock
micromamba activate labbooking
python -c "import sys; print(sys.executable, sys.version)"
python -m pip check
npm.cmd ci --no-audit --no-fund
npm.cmd ls --depth 0
```

C 若使用已安装的 Conda，可用 `conda create --yes --no-default-packages -n labbooking --file conda-win-64.lock`、`conda activate labbooking` 读取同一份锁。B 机器的 Windows 应用控制拦截了辅助 Conda 安装工具的原生扩展，该命令路径留给 C 验证。Micromamba 复现路径已逐项核对包构建及摘要。[Micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html) · [Conda 环境文档](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html)

从 PostgreSQL 官网列出的 EDB 发行渠道取得 17.12-2。下面的命令在当前用户目录解压启动临时服务所需的二进制、库与数据。已有同一发行包时可直接设置最后一行的路径。[PostgreSQL Windows 下载说明](https://www.postgresql.org/download/windows/) · [EDB 发布校验值](https://get.enterprisedb.com/postgresql/postgresql-17.12-2-windows-x64-binaries.zip.sha256)

```powershell
$pgRoot = Join-Path $env:LOCALAPPDATA 'LabBookingPrep\edb-verified'
$pgArchive = Join-Path $env:TEMP 'postgresql-17.12-2-windows-x64-binaries.zip'
curl.exe -fLsS --retry 2 -o $pgArchive https://get.enterprisedb.com/postgresql/postgresql-17.12-2-windows-x64-binaries.zip
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL download failed' }
if ((Get-FileHash $pgArchive -Algorithm SHA256).Hash -ne '520c8c6f19abb3b31fa83ec5e486e2f769eedd7593d94e60a7cda8a5bfb4df91') { throw 'PostgreSQL checksum mismatch' }
New-Item -ItemType Directory -Force $pgRoot | Out-Null
tar.exe -xf $pgArchive -C $pgRoot pgsql/bin pgsql/lib pgsql/share
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL extraction failed' }
$env:LABBOOKING_PG_BIN = Join-Path $pgRoot 'pgsql\bin'
```

## 验证

```powershell
git rev-parse HEAD
python -m tools.verify_runtime
if ($LASTEXITCODE -ne 0) { throw 'Runtime verification failed' }
$cssOutput = Join-Path $env:TEMP 'labbooking-dp01.css'
'@import "tailwindcss" source(none); @source inline("flex");' | .\node_modules\.bin\tailwindcss.cmd -i - -o $cssOutput
if ($LASTEXITCODE -ne 0 -or !(Select-String -LiteralPath $cssOutput -SimpleMatch '.flex' -Quiet)) { throw 'CSS probe failed' }
Get-Item node_modules/lucide-static/icons/calendar.svg -ErrorAction Stop
```

验证脚本逐项比对 60 个已安装构建的 URL 与 SHA-256，检查 Asia/Shanghai 时区数据，使用合成密码验证正反例与随机盐。它在临时目录初始化 PostgreSQL，使用回环地址、临时端口、UTF-8、C 排序规则、Asia/Shanghai 时区与一次性 SCRAM 凭据。建好普通验证角色后，通过独立 Waitress HTTP 请求两次查询 PostgreSQL 的事务隔离级别，验证 Flask/Jinja、同步驱动及单连接池复用，最后停止服务并清理临时库。测试进程的两个 Waitress 线程和一个池连接仅用于本次检查。正式库角色、迁移和并发预算分别由 DP-05、DP-09 落实。[Tailwind CLI](https://tailwindcss.com/docs/installation/tailwind-cli) · [Lucide Static](https://lucide.dev/guide/packages/lucide-static)

## 统一密码策略

初始化使用 [hash_password](../labbooking/auth/passwords.py)，显式传入 `scrypt:32768:8:3`（N=32768、r=8、p=3）和 24 字符随机盐。登录使用同模块的 `verify_password` 调用 Werkzeug，对完整的存储字符串核验。参数随哈希编码存储，核验函数只返回真假。该组合对应 OWASP 列出的约 32 MiB scrypt 工作区，适合先在课程 Windows 机器上验证内存开销。[Werkzeug 官方接口](https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash) · [OWASP scrypt 参数依据](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#scrypt)

B 在 Windows 11 x64（OS build 26200，约 16 GiB 内存）独立启动 Python 进程，用一次性合成密码测得一次生成 588.8 ms、一次正确核验 564.3 ms；同进程验证错误密码拒绝、相同密码使用新盐。外部按 100 ms 采样观察到进程峰值工作集约 96.9 MiB，包含解释器和导入的库。这些数据用于资源估算；正式登录实现及并发负载验证随对应 Story 执行。

## B 的本机复现结果（2026-11-25）

在另一个空环境目录从锁文件重新安装，60/60 项 Conda 构建及 SHA-256 匹配，`pip check` 通过。Alembic、Flask-Login、Flask-WTF、pytest 可导入。前端 `npm ci` 成功，CLI 实际生成了 `.flex` 规则，可以读取 Lucide 的 calendar.svg。

第一次使用 conda-forge 服务端时，Windows 应用控制拦截了 plpgsql.dll。采用上述官方校验值验证的独立 EDB 发行包后，临时库成功初始化。复现时查得服务端 17.12、时区 Asia/Shanghai、排序规则 C，应用使用普通角色 prep_reader。两次 HTTP 200 响应都报告 READ COMMITTED，数据库后端进程号相同。正确密码通过、错误密码拒绝，新盐检查通过。脚本退出码为 0，临时服务已停止。

本机可在仓库根目录重复执行以下两行。工具和环境位于当前用户的 LabBookingPrep 目录。

```powershell
$env:LABBOOKING_PG_BIN = Join-Path $env:LOCALAPPDATA 'LabBookingPrep\edb-verified\pgsql\bin'
& "$env:LOCALAPPDATA\LabBookingPrep\micromamba.exe" run -p "$env:LOCALAPPDATA\LabBookingPrep\win64-final\envs\labbooking" python -m tools.verify_runtime
```

## 交给 C 的记录

记录提交号、Windows 版本、解释器路径、环境名、锁文件比对结果、数据库版本/排序规则/时区、两次 HTTP 校验、CSS/SVG 和密码正反例结果。如实记录失败步骤及修复。将记录附在开发准备 PR 即可。真实密码、哈希、数据库口令均无需提交。

## 启动完整应用

从仓库根目录激活锁定环境。首次使用时，在 PostgreSQL 17.12 的 psql 管理会话中为开发、测试准备独立数据库并交互设置口令。

```sql
CREATE ROLE labbooking_app LOGIN;
CREATE ROLE labbooking_migrator LOGIN;
\password labbooking_app
\password labbooking_migrator
CREATE DATABASE labbooking_dev OWNER labbooking_migrator;
CREATE DATABASE labbooking_test OWNER labbooking_migrator;
```

连接串格式为 `postgresql+psycopg://用户名:编码后口令@127.0.0.1:5432/库名`。两个角色指向同一主机、端口和所选库。以下示例设置当前 PowerShell 会话，应用只需普通角色，迁移和初始化使用维护角色。

```powershell
function Read-DatabaseUrl($prompt) {
    [System.Net.NetworkCredential]::new('', (Read-Host $prompt -AsSecureString)).Password
}
$env:LABBOOKING_ENV = 'development'
$env:LABBOOKING_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
$env:LABBOOKING_DEV_DATABASE_URL = Read-DatabaseUrl '开发库普通角色连接串'
$env:LABBOOKING_MIGRATION_DATABASE_URL = Read-DatabaseUrl '同一开发库的维护角色连接串'
$env:LABBOOKING_TRANSPORT = 'local-http'
python -m alembic upgrade head
python -m alembic current
```

准备一个仅维护人员可读取的 UTF-8 JSON 文件，存放在仓库外。顶层为非空数组，每项有四个字符串字段：`username`、`password`、`phone`、`role`。角色可选 `user` 或 `admin`。用户名去首尾空白并转小写后须唯一。联系电话使用十一位手机号格式，可以重复。整批校验或写入失败时全部回滚。课程演示使用合成账号；真实名单通过需求负责人私下交付。

```powershell
$accountFile = Read-Host '输入私有账号 JSON 文件的完整路径'
python -m flask --app labbooking:create_app init-users "$accountFile"
if ($LASTEXITCODE -ne 0) { throw '账号初始化未完成，请核对后再启动' }
Remove-Item Env:LABBOOKING_MIGRATION_DATABASE_URL
python -m waitress --listen=127.0.0.1:8080 --call labbooking:create_app
```

打开 [本机登录页](http://127.0.0.1:8080/login)。管理员可在设备目录新增设备，普通用户可查询未来日期的上午或下午时段并提交预约。Ctrl+C 停止服务。私下保存部署密钥可让重启后的有效会话继续使用。

- 本机回环 HTTP 显式设置 `local-http`。外部服务在 HTTPS 终止后使用默认 `https` 配置。会话固定两小时，Cookie 使用 HttpOnly、SameSite=Lax，HTTPS 启用 Secure。
- 日常运行默认池上限 5，无额外连接，取连接最多等待 10 秒；数据库锁等待上限 10 秒，语句上限 30 秒。非功能验证使用单个 Waitress 进程、24 线程、`LABBOOKING_POOL_SIZE=24`、PostgreSQL 最大连接数 100。
- 手工操作测试库时保留开发连接用于名称隔离检查，将 `LABBOOKING_ENV` 改为 `test`，设置 `LABBOOKING_TEST_DATABASE_URL` 和指向同一测试库的维护连接。应用、迁移和账号初始化分别检查目标库与角色。
- 在已有库执行迁移前，由维护人员创建并验证 PostgreSQL 备份。版本 0002 仅授予业务所需表和列权限，回到 0001 会收回业务表权限并保留数据。0001 的回退使用已复核备份，在隔离库恢复并比对历史后再切换。

## 一次运行全部验证

设置上文的 `LABBOOKING_PG_BIN` 后执行。测试会自行启动和停止隔离的 PostgreSQL 实例，生成两个临时库、两种数据库角色及合成账号。

```powershell
git rev-parse HEAD
$env:LABBOOKING_EVIDENCE_DIR = Join-Path $env:TEMP ('labbooking-evidence-' + [guid]::NewGuid())
python -m tools.verify_runtime
if ($LASTEXITCODE -ne 0) { throw '运行环境验证失败' }
python -m pytest -q tests --tb=short
if ($LASTEXITCODE -ne 0) { throw '业务自测出现失败' }
Get-ChildItem -LiteralPath $env:LABBOOKING_EVIDENCE_DIR
```

PR 的 Windows 检查运行同一组命令，并在 `booking-evidence` 中保留请求样本和故障结果。[四个 Epic 的验收对照](acceptance.md)
