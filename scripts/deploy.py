#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QA System 一键部署脚本

Usage:
    python scripts/deploy.py              # 交互式菜单
    python scripts/deploy.py deploy       # 部署后端
    python scripts/deploy.py status       # 查看服务状态
    python scripts/deploy.py logs         # 查看后端日志
    python scripts/deploy.py restart      # 重启后端
    python scripts/deploy.py rollback     # 回滚到上次备份
    python scripts/deploy.py db           # 运行数据库迁移
    python scripts/deploy.py test         # 运行测试

依赖:
    pip install paramiko
"""

import sys
import os
import time
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("错误: 请先安装 paramiko → pip install paramiko")
    sys.exit(1)

# ==================== 配置 ====================

# Load .deploy.env if exists (local only, not committed to git)
_env_file = Path(__file__).parent / ".deploy.env"
if _env_file.exists():
    for line in _env_file.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# ⚠️ SECURITY: Configure your own server credentials here.
# DO NOT commit real passwords to git.
# Use environment variables or .env file in production.
SERVER = {
    "host": os.environ.get("DEPLOY_HOST", "YOUR_SERVER_IP"),
    "port": int(os.environ.get("DEPLOY_PORT", "22")),
    "user": os.environ.get("DEPLOY_USER", "root"),
    "password": os.environ.get("DEPLOY_PASSWORD", ""),
}

PATHS = {
    "local_backend": Path(__file__).parent.parent / "backend",
    "remote_base": "/opt/qa-system",
    "remote_backend": "/opt/qa-system/backend",
    "venv": "/opt/qa-system/venv/bin",
    "service": "qa-backend",
}

# Files to skip during upload
SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache", "node_modules", ".venv", "data"}
SKIP_FILES = {".pyc", ".pyo", ".env"}

# ==================== Colors ====================

class C:
    G = '\033[92m'
    R = '\033[91m'
    Y = '\033[93m'
    B = '\033[94m'
    W = '\033[0m'
    BOLD = '\033[1m'


def log(msg, color=C.W):
    print(f"{color}{msg}{C.W}")


def log_step(step, msg):
    print(f"\n{C.BOLD}[{step}] {msg}{C.W}")


def ok(msg):
    print(f"  {C.G}[OK]{C.W} {msg}")


def warn(msg):
    print(f"  {C.Y}[!]{C.W} {msg}")


def err(msg):
    print(f"  {C.R}[ERR]{C.W} {msg}")


# ==================== SSH ====================

class Remote:
    def __init__(self):
        self.ssh = None
        self.sftp = None

    def connect(self):
        log_step("SSH", f"Connecting to {SERVER['user']}@{SERVER['host']}...")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            SERVER["host"], SERVER["port"],
            SERVER["user"], SERVER["password"],
            timeout=30,
        )
        self.sftp = self.ssh.open_sftp()
        ok("Connected")

    def close(self):
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()

    def run(self, cmd, timeout=120, show=True):
        if show:
            display = cmd if len(cmd) <= 80 else cmd[:77] + "..."
            log(f"  $ {display}", C.B)
        _, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace").strip()
        code = stdout.channel.recv_exit_status()
        if code != 0 and show:
            e = stderr.read().decode("utf-8", errors="replace").strip()
            if e:
                warn(f"stderr: {e[:300]}")
        return code, out

    def upload_dir(self, local_dir, remote_dir):
        """Recursively upload directory, skipping __pycache__ etc."""
        count = 0
        for root, dirs, files in os.walk(local_dir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            rel = os.path.relpath(root, local_dir)
            rpath = remote_dir if rel == "." else f"{remote_dir}/{rel}".replace("\\", "/")

            try:
                self.sftp.stat(rpath)
            except FileNotFoundError:
                self.sftp.mkdir(rpath)

            for f in files:
                if any(f.endswith(ext) for ext in SKIP_FILES):
                    continue
                local_file = os.path.join(root, f)
                remote_file = f"{rpath}/{f}"
                self.sftp.put(local_file, remote_file)
                count += 1

        return count

    def upload_file(self, local_path, remote_path):
        self.sftp.put(str(local_path), remote_path)


# ==================== Actions ====================

def action_deploy(r: Remote):
    """Full deployment: backup → upload → migrate → restart → health check"""

    # 1. Backup
    log_step("1/5", "Backing up remote backend...")
    r.run(f"cp -r {PATHS['remote_backend']} {PATHS['remote_backend']}.bak.$(date +%Y%m%d%H%M%S)", show=False)
    ok("Backup created")

    # 2. Upload
    log_step("2/5", "Uploading backend code...")
    count = r.upload_dir(PATHS["local_backend"], PATHS["remote_backend"])
    ok(f"Uploaded {count} files")

    # 3. Migrate
    log_step("3/5", "Running database migration...")
    code, out = r.run(f"cd {PATHS['remote_backend']} && {PATHS['venv']}/python -m alembic upgrade head 2>&1")
    if "Running upgrade" in out or "already" in out.lower():
        ok(f"Migration: {out.split(chr(10))[-1]}")
    else:
        warn(f"Migration output: {out[:200]}")

    # 4. Restart
    log_step("4/5", "Restarting service...")
    r.run("systemctl restart qa-backend", show=False)
    time.sleep(8)
    code, out = r.run("systemctl is-active qa-backend", show=False)
    if out == "active":
        ok("Service is active")
    else:
        err(f"Service status: {out}")
        r.run(f"journalctl -u {PATHS['service']} --no-pager -n 20")
        return False

    # 5. Health check
    log_step("5/5", "Health check...")
    code, out = r.run("curl -s http://localhost:8000/api/v1/health", show=False)
    try:
        import json
        data = json.loads(out)
        if data.get("status") == "ok":
            ok("API healthy")
        else:
            warn(f"API response: {out[:100]}")
    except Exception:
        warn(f"Health response: {out[:100]}")

    # Stats
    code, out = r.run("curl -s http://localhost:8000/api/v1/stats", show=False)
    if out and "error" not in out:
        ok(f"Stats: {out[:200]}")

    log(f"\n  Deploy complete!", C.G)
    return True


def action_status(r: Remote):
    """Check all service statuses"""
    log_step("Status", "Checking services...")

    # Backend
    code, out = r.run("systemctl is-active qa-backend", show=False)
    status = out.strip()
    if status == "active":
        ok(f"qa-backend: {C.G}active{C.W}")
    else:
        err(f"qa-backend: {status}")

    # Uptime
    code, out = r.run("systemctl show qa-backend --property=ActiveEnterTimestamp --value", show=False)
    if out:
        log(f"    Started: {out}", C.B)

    # PostgreSQL
    code, out = r.run("docker ps --filter name=qa-postgres --format '{{.Status}}'", show=False)
    ok(f"PostgreSQL: {out}") if out else err("PostgreSQL: not running")

    # Redis
    code, out = r.run("docker ps --filter name=qa-redis --format '{{.Status}}'", show=False)
    ok(f"Redis: {out}") if out else err("Redis: not running")

    # Health
    code, out = r.run("curl -s http://localhost:8000/api/v1/health", show=False)
    ok(f"API: {out}") if "ok" in out else warn(f"API: {out[:100]}")

    # DB stats
    code, out = r.run("curl -s http://localhost:8000/api/v1/stats 2>/dev/null", show=False)
    if out and "error" not in out:
        ok(f"DB Stats: {out[:200]}")

    # Disk & Memory
    code, out = r.run("df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\" used)\"}'", show=False)
    log(f"    Disk: {out}", C.B)
    code, out = r.run("free -h | awk '/Mem:/{print $3\"/\"$2}'", show=False)
    log(f"    Memory: {out}", C.B)


def action_logs(r: Remote, lines=50):
    """View recent backend logs"""
    log_step("Logs", f"Last {lines} lines of qa-backend:")
    code, out = r.run(f"journalctl -u qa-backend --no-pager -n {lines} --output=cat", show=False)
    print(out)


def action_restart(r: Remote):
    """Restart backend service"""
    log_step("Restart", "Restarting qa-backend...")
    r.run("systemctl restart qa-backend", show=False)
    time.sleep(8)
    code, out = r.run("systemctl is-active qa-backend", show=False)
    if out == "active":
        ok("Service restarted successfully")
    else:
        err(f"Status: {out}")
        r.run(f"journalctl -u {PATHS['service']} --no-pager -n 15")


def action_rollback(r: Remote):
    """Rollback to latest backup"""
    log_step("Rollback", "Finding latest backup...")
    code, out = r.run(f"ls -td {PATHS['remote_backend']}.bak.* 2>/dev/null | head -1", show=False)
    if not out:
        err("No backup found")
        return False

    log(f"    Latest backup: {out}", C.B)
    r.run(f"rm -rf {PATHS['remote_backend']}")
    r.run(f"cp -r {out} {PATHS['remote_backend']}")
    ok("Files restored")

    r.run("systemctl restart qa-backend", show=False)
    time.sleep(8)
    code, status = r.run("systemctl is-active qa-backend", show=False)
    if status == "active":
        ok("Rollback successful, service running")
    else:
        err("Rollback done but service failed to start")
    return True


def action_db(r: Remote):
    """Run database migration"""
    log_step("DB", "Running Alembic migration...")
    code, out = r.run(f"cd {PATHS['remote_backend']} && {PATHS['venv']}/python -m alembic upgrade head 2>&1")
    print(out)


def action_test(r: Remote):
    """Run health & connectivity tests"""
    log_step("Test", "Quick tests...")

    tests = [
        ("Health", "curl -s http://localhost:8000/api/v1/health"),
        ("Stats", "curl -s http://localhost:8000/api/v1/stats"),
        ("Conversations", "curl -s http://localhost:8000/api/v1/qa/conversations"),
        ("Data API", "curl -s http://localhost:8000/api/v1/data/system/overview"),
        ("DB Connection", "docker exec qa-postgres psql -U postgres -d ai_qa -c 'SELECT COUNT(*) FROM users;' -t"),
        ("Redis Ping", "docker exec qa-redis redis-cli ping"),
    ]

    passed = 0
    for name, cmd in tests:
        code, out = r.run(cmd, show=False)
        if code == 0 and out and "error" not in out.lower():
            ok(f"{name}: {out[:100]}")
            passed += 1
        else:
            err(f"{name}: {out[:100] if out else 'no response'}")

    print(f"\n  Result: {passed}/{len(tests)} passed")


# ==================== Menu ====================

BANNER = f"""{C.BOLD}
╔══════════════════════════════════════════╗
║    QA System Deploy Tool                 ║
╚══════════════════════════════════════════╝{C.W}
Server: {SERVER['host']} → /opt/qa-system
"""

MENU = """
  1. Deploy (upload + migrate + restart)
  2. Status (check all services)
  3. Logs (view backend logs)
  4. Restart (restart backend)
  5. Rollback (restore last backup)
  6. DB Migrate (run alembic)
  7. Quick Test (health checks)
  0. Exit
"""

ACTIONS = {
    "deploy": action_deploy,
    "status": action_status,
    "logs": action_logs,
    "restart": action_restart,
    "rollback": action_rollback,
    "db": action_db,
    "test": action_test,
}

MENU_MAP = {
    "1": "deploy", "2": "status", "3": "logs", "4": "restart",
    "5": "rollback", "6": "db", "7": "test",
}


def main():
    print(BANNER)

    # CLI args
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        if action in ["-h", "--help", "help"]:
            print(__doc__)
            return
        if action not in ACTIONS:
            print(f"Unknown action: {action}")
            print(f"Available: {', '.join(ACTIONS.keys())}")
            return
    else:
        print(MENU)
        try:
            choice = input("  Select: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye")
            return
        if choice == "0":
            return
        action = MENU_MAP.get(choice)
        if not action:
            print("Invalid choice")
            return

    # Execute
    r = Remote()
    try:
        r.connect()
        ACTIONS[action](r)
    except KeyboardInterrupt:
        print("\nAborted")
    except Exception as e:
        err(f"Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        r.close()


if __name__ == "__main__":
    main()
