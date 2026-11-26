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

## Story 1.1 应用启动与验收

在仓库根目录激活上述锁定环境。应用通过 `labbooking:create_app` 装配 Auth、Devices、Bookings，按所选环境建立 Flask-SQLAlchemy 扩展。当前访问 `/login` 返回 404；登录页面由 Story 1.3 实现。

### 配置开发和测试数据库

在本机 PostgreSQL 17.12 服务中准备两个不同名称的数据库，例如 `labbooking_dev` 与 `labbooking_test`。应用使用普通登录角色，迁移使用单独的角色。新服务可用管理账号在 psql 中运行以下初始化示例；密码通过 psql 的交互提示设置。下列命令面向新库，仅执行一次。

```sql
CREATE ROLE labbooking_app LOGIN;
CREATE ROLE labbooking_migrator LOGIN;
\password labbooking_app
\password labbooking_migrator
CREATE DATABASE labbooking_dev OWNER labbooking_migrator;
CREATE DATABASE labbooking_test OWNER labbooking_migrator;
```

连接串格式为 `postgresql+psycopg://用户名:编码后的口令@127.0.0.1:5432/库名`。口令里的特殊字符需按 URL 编码。下面使用当前 PowerShell 进程的私有环境变量，输入连接串时隐藏回显。开发库和测试库的名称用于隔离校验，切换测试环境时保留开发库配置作比对。

```powershell
function Read-DatabaseUrl($prompt) {
    [System.Net.NetworkCredential]::new('', (Read-Host $prompt -AsSecureString)).Password
}
$env:LABBOOKING_ENV = 'development'
$env:LABBOOKING_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
$env:LABBOOKING_DEV_DATABASE_URL = Read-DatabaseUrl '开发库应用角色连接串'
python -m waitress --listen=127.0.0.1:8080 --call labbooking:create_app
```

用 Ctrl+C 停止。保留同一会话的密钥可供重复启动使用。切换到测试库并检查迁移连接：

```powershell
$env:LABBOOKING_ENV = 'test'
$env:LABBOOKING_TEST_DATABASE_URL = Read-DatabaseUrl '测试库应用角色连接串'
$env:LABBOOKING_MIGRATION_DATABASE_URL = Read-DatabaseUrl '同一测试库的迁移角色连接串'
python -m alembic current
python -m alembic heads
```

应用按需打开数据库连接，建立物理连接时核对数据库名称、角色及服务端主版本。测试库与开发库同名时，配置解析立即失败，包括主机别名和不同账号指向同名库的情形。Alembic 的连接必须与当前应用连接具有相同主机、端口、库名及不同角色。版本目录在首次业务模型交付时添加第一条迁移。本地单进程连接池上限为 5，额外连接数为 0，取连接最长等待 10 秒。正式并发验收时按 DP-09 校准。每次请求结束由 Flask-SQLAlchemy 清理 Session。

### C 的 Story 验收命令

设置 `LABBOOKING_PG_BIN` 为已校验的 EDB 发行包 bin 目录后运行：

```powershell
git rev-parse HEAD
python -m tools.verify_runtime
python -m pytest -q tests/test_app_foundation.py
```

测试自动创建临时 PostgreSQL 集群、普通应用角色、迁移角色和两个数据库。覆盖缺失配置的脱敏错误、应用及迁移误指开发库、首次连接与复用连接的隔离级别、跨请求事务清理、Alembic 版本表仅出现在测试库，以及实际 Waitress 工厂入口的 HTTP 响应。测试结束时停止临时服务并清理数据。
