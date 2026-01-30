import subprocess


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
        if not host:
            raise ValueError("Host is required.")
        if not command:
            raise ValueError("Command is required.")
        target = f"{user}@{host}" if user else host
        args = ["ssh", "-p", str(port), "-o", "BatchMode=yes"]
        if strict_host_key:
            args += ["-o", "StrictHostKeyChecking=accept-new"]
        else:
            args += ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
        if key_path:
            args += ["-i", key_path]
        args += [target, command]
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("SSH command timed out.")
        return {
            "host": host,
            "user": user,
            "port": port,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
