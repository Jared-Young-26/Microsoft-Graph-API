import subprocess
import time

try:
    import paramiko
except Exception:  # pragma: no cover - optional dependency
    paramiko = None


def _ps_quote(value):
    return str(value).replace("'", "''")


class RemoteSSHClient:
    def run_command(
        self,
        host,
        command,
        user=None,
        port=22,
        key_path=None,
        strict_host_key=True,
        timeout=60,
    ):
        runner = SshRunner(
            host=host,
            user=user,
            port=port,
            key_path=key_path,
            strict_host_key_checking=strict_host_key,
        )
        return runner.run_command(command, timeout=timeout)


class SshRunner:
    def __init__(
        self,
        host: str,
        user: str | None = None,
        port: int = 22,
        key_path: str | None = None,
        strict_host_key_checking: bool = True,
    ):
        self.host = host
        self.user = user
        self.port = port or 22
        self.key_path = key_path
        self.strict_host_key_checking = strict_host_key_checking

    def _run_paramiko(self, command: str, timeout: int):
        if not paramiko:
            raise RuntimeError("Paramiko not available.")
        client = paramiko.SSHClient()
        if self.strict_host_key_checking:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        start = time.monotonic()
        try:
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                key_filename=self.key_path,
                timeout=timeout,
                banner_timeout=timeout,
                auth_timeout=timeout,
            )
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            out_text = stdout.read().decode(errors="ignore")
            err_text = stderr.read().decode(errors="ignore")
        finally:
            try:
                client.close()
            except Exception:
                pass
        duration_ms = int((time.monotonic() - start) * 1000)
        return {
            "host": self.host,
            "user": self.user,
            "port": self.port,
            "command": command,
            "returncode": exit_code,
            "stdout": out_text,
            "stderr": err_text,
            "duration_ms": duration_ms,
            "transport": "paramiko",
        }

    def _run_subprocess(self, command: str, timeout: int):
        target = f"{self.user}@{self.host}" if self.user else self.host
        args = ["ssh", "-p", str(self.port), "-o", "BatchMode=yes"]
        if self.strict_host_key_checking:
            args += ["-o", "StrictHostKeyChecking=accept-new"]
        else:
            args += ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
        if self.key_path:
            args += ["-i", self.key_path]
        args += [target, command]
        start = time.monotonic()
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("SSH command timed out.")
        duration_ms = int((time.monotonic() - start) * 1000)
        return {
            "host": self.host,
            "user": self.user,
            "port": self.port,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_ms": duration_ms,
            "transport": "subprocess",
        }

    def run_command(self, command: str, timeout: int = 60):
        if not self.host:
            raise ValueError("Host is required.")
        if not command:
            raise ValueError("Command is required.")
        try:
            if paramiko:
                return self._run_paramiko(command, timeout)
        except Exception:
            if paramiko is None:
                raise
        return self._run_subprocess(command, timeout)

    def test_connection(self, timeout: int = 10):
        results = {"ok": False, "host": self.host, "user": self.user, "port": self.port, "checks": {}}
        hostname = self.run_command("hostname", timeout=timeout)
        results["checks"]["hostname"] = hostname.get("stdout", "").strip()
        user = self.run_command("whoami", timeout=timeout)
        results["checks"]["whoami"] = user.get("stdout", "").strip()
        os_info = self.run_command("uname -a", timeout=timeout)
        os_out = os_info.get("stdout", "").strip()
        if not os_out:
            os_info = self.run_command("cmd /c ver", timeout=timeout)
            os_out = os_info.get("stdout", "").strip()
        results["checks"]["os"] = os_out
        results["ok"] = True
        return results
