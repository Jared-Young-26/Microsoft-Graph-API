from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import time
import msal
import requests
import random
import subprocess
import uuid
import threading
import json
import re

# Load environment variables from .env file
load_dotenv()
REQUIRED_ENV_VARS = ["TENANT_ID", "CLIENT_ID", "CLIENT_SECRET"]

SENSITIVE_KEYWORDS = (
    "password",
    "passphrase",
    "secret",
    "token",
    "credential",
    "private",
    "client_secret",
    "refresh_token",
    "access_token",
    "apikey",
    "api_key",
)


def _is_sensitive_key(key: str) -> bool:
    normalized = str(key or "").lower()
    if not normalized:
        return False
    if normalized.endswith("_key") or normalized.endswith("apikey"):
        return True
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS)


def _redact_payload(value, depth: int = 0):
    if value is None or isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        redacted = value
        for keyword in SENSITIVE_KEYWORDS:
            pattern = re.compile(rf"(?i)({re.escape(keyword)}\\s*[:=]\\s*)(\\S+)")
            redacted = pattern.sub(r"\\1[redacted]", redacted)
        return redacted
    if depth > 6:
        return "[truncated]"
    if isinstance(value, list):
        return [_redact_payload(item, depth + 1) for item in value]
    if isinstance(value, dict):
        sanitized = {}
        for key, val in value.items():
            if _is_sensitive_key(key):
                sanitized[key] = "[redacted]"
            else:
                sanitized[key] = _redact_payload(val, depth + 1)
        return sanitized
    return value


def is_powershell_envelope(value) -> bool:
    if not isinstance(value, dict):
        return False
    return all(key in value for key in ("ok", "data", "error", "meta"))


def unwrap_powershell_data(value):
    if is_powershell_envelope(value):
        return value.get("data")
    return value

class GraphAPIError(RuntimeError):
    def __init__(
        self,
        message,
        status_code=None,
        request_id=None,
        response=None,
        code=None,
        retry_after=None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
        self.response = response
        self.code = code
        self.retry_after = retry_after


class GraphSession:
    def __init__(self, *, tenant_id=None, client_id=None, client_secret=None, debug=False):
        self._validate_env(tenant_id, client_id, client_secret)
        self.tenant_id = tenant_id or os.getenv("TENANT_ID")
        self.client_id = client_id or os.getenv("CLIENT_ID")
        self.client_secret = client_secret or os.getenv("CLIENT_SECRET")
        self.scope = ["https://graph.microsoft.com/.default"]
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.graph_base = "https://graph.microsoft.com/v1.0"
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            authority=authority,
            client_credential=self.client_secret,
        )
        self.session = requests.Session()
        self.token = None
        self.expires_at = 0
        self.debug = debug
    
    def token_expiry_human(self):
        if not self.expires_at:
            return "No token aquired"
        
        dt = datetime.fromtimestamp(self.expires_at, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def _validate_env(self, tenant_id, client_id, client_secret):
        missing = []
        if not (tenant_id or os.getenv("TENANT_ID")):
            missing.append("TENANT_ID")
        if not (client_id or os.getenv("CLIENT_ID")):
            missing.append("CLIENT_ID")
        if not (client_secret or os.getenv("CLIENT_SECRET")):
            missing.append("CLIENT_SECRET")
        if missing:
            raise RuntimeError(f"Missing Microsoft Configuration Variables: {missing}")
    
    def _request(self, method, url, **kwargs):
        max_attempts = kwargs.pop("max_attempts", 5)
        extra_headers = kwargs.pop("headers", {})

        for attempt in range(1, max_attempts + 1):
            headers = {**self.get_headers(), **extra_headers}
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=30,
                    **kwargs,
                )
            except requests.RequestException as exc:
                if attempt == max_attempts:
                    raise exc
                sleep_time = min((2 ** attempt) + random.random(), 30)
                time.sleep(sleep_time)
                continue

            if response.status_code in (429, 500, 502, 503, 504):
                retry_after = self._parse_retry_after(response.headers)
                if attempt == max_attempts:
                    raise GraphAPIError(
                        f"Transient Graph Error {response.status_code}",
                        status_code=response.status_code,
                        request_id=response.headers.get("request-id"),
                        response=response,
                        retry_after=retry_after,
                    )
                sleep_time = retry_after if retry_after is not None else min((2 ** attempt) + random.random(), 30)
                time.sleep(sleep_time)
                continue

            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                response = e.response
                request_id = response.headers.get("request-id") if response else None
                detail = None
                code = None
                retry_after = None
                if response is not None:
                    retry_after = self._parse_retry_after(response.headers)
                    try:
                        error_payload = response.json().get("error", {})
                        detail = error_payload.get("message")
                        code = error_payload.get("code")
                        if detail is None:
                            detail = code
                    except Exception:
                        detail = response.text.strip()
                message = f"Graph request failed ({response.status_code})"
                if code:
                    message = f"{message} [{code}]"
                if detail:
                    message = f"{message}: {detail}"
                raise GraphAPIError(
                    message,
                    status_code=response.status_code if response else None,
                    request_id=request_id,
                    response=response,
                    code=code,
                    retry_after=retry_after,
                )
            return response

    def _parse_retry_after(self, headers):
        if not headers:
            return None
        retry_after = headers.get("Retry-After")
        if retry_after:
            try:
                return int(retry_after)
            except (TypeError, ValueError):
                return None
        retry_after_ms = headers.get("x-ms-retry-after-ms")
        if retry_after_ms:
            try:
                return max(1, int(int(retry_after_ms) / 1000))
            except (TypeError, ValueError):
                return None
        return None

    def get_graph_token(self):
        result = self.app.acquire_token_for_client(scopes=self.scope)

        if "access_token" not in result:
            raise RuntimeError(f"Could not acquire Microsoft Graph token: {result}")
        
        self.token = result["access_token"]
        self.expires_at = time.time() + int(result["expires_in"])
        self._log(f"Token acquired. Expires at: {self.token_expiry_human()}")
        return self.token

    def get_headers(self):
        if not self.token or time.time() > self.expires_at - 60:
            self.get_graph_token()
        
        return {"Authorization": f"Bearer {self.token}"}
    
    def url(self, path):
        return f"{self.graph_base}/{path.lstrip('/')}"
    
    def get(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("GET", full_url, **kwargs)
    
    def post(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("POST", full_url, **kwargs)

    def put(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("PUT", full_url, **kwargs)
    
    def patch(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("PATCH", full_url, **kwargs)
    
    def delete(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("DELETE", full_url, **kwargs)
    
    def paged_get(self, url):
        results = []
        while url:
            response = self.get(url)
            data = response.json()
            results.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
        return results
    
    def _log(self, msg):
        if self.debug:
            print(msg)


class ServiceClient:
    def __init__(self, graph_session):
        self.graph = graph_session

    def get(self, url, **kwargs):
        return self.graph.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self.graph.post(url, **kwargs)

    def put(self, url, **kwargs):
        return self.graph.put(url, **kwargs)

    def patch(self, url, **kwargs):
        return self.graph.patch(url, **kwargs)

    def delete(self, url, **kwargs):
        return self.graph.delete(url, **kwargs)


class PowerShellCommandError(RuntimeError):
    def __init__(self, message, output=None):
        super().__init__(message)
        self.output = output


class PowerShellSession:
    def __init__(self, pwsh_path="pwsh"):
        self.pwsh_path = pwsh_path
        self.process = None
        self._lock = threading.Lock()

    def _start(self):
        if self.process and self.process.poll() is None:
            return
        try:
            self.process = subprocess.Popen(
                [self.pwsh_path, "-NoLogo", "-NoProfile", "-Command", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except FileNotFoundError as e:
            raise RuntimeError("PowerShell (pwsh) not found. Install PowerShell 7 and ensure 'pwsh' is on PATH.") from e

    def _build_param_block(self, parameters):
        if not parameters:
            return "$__codex_params = @{}"
        payload = json.dumps(parameters)
        payload = payload.replace("'", "''")
        return (
            "$__codex_params = @{}; "
            f"try {{ $__codex_params = '{payload}' | ConvertFrom-Json -AsHashtable }} "
            "catch { $__codex_params = @{} }"
        )

    def _wrap_script(self, script, *, parameters=None, depth=8, capture_text=False, working_dir=None):
        token = f"__CODEX_PS_ENVELOPE__{uuid.uuid4().hex}"
        param_block = self._build_param_block(parameters)
        invoke_with_params = False
        if parameters:
            stripped = (script or "").strip()
            if stripped and all(ch not in stripped for ch in ["\n", ";", "|", "`", "{", "}"]) and " " not in stripped:
                invoke_with_params = True
        invoke_flag = "$true" if invoke_with_params else "$false"
        cmd_literal = script.replace("'", "''") if script else ""
        workdir_block = ""
        if working_dir:
            workdir_literal = working_dir.replace("'", "''")
            workdir_block = f"Push-Location '{workdir_literal}'"
        pop_block = "Pop-Location" if working_dir else ""
        capture_block = "| Out-String" if capture_text else ""
        return token, (
            "$ErrorActionPreference = 'Stop'\n"
            "$ProgressPreference = 'SilentlyContinue'\n"
            "$Error.Clear()\n"
            f"{param_block}\n"
            "foreach ($k in $__codex_params.Keys) { Set-Variable -Name $k -Value $__codex_params[$k] -Scope Local }\n"
            "$__codex_ok = $true\n"
            "$__codex_error = $null\n"
            "$__codex_data = $null\n"
            "$__codex_start = Get-Date\n"
            "try {\n"
            f"{workdir_block}\n"
            f"  if ({invoke_flag}) {{ $__codex_data = & '{cmd_literal}' @__codex_params {capture_block} }}\n"
            "  else {\n"
            f"    $__codex_data = & {{\n{script}\n    }} {capture_block}\n"
            "  }\n"
            "} catch {\n"
            "  $__codex_ok = $false\n"
            "  $__codex_error = $_\n"
            "} finally {\n"
            f"  {pop_block}\n"
            "}\n"
            "$__codex_end = Get-Date\n"
            "$__codex_errors = @()\n"
            "if ($Error.Count -gt 0) {\n"
            "  $__codex_errors = $Error | ForEach-Object {\n"
            "    [PSCustomObject]@{\n"
            "      message = $_.Exception.Message\n"
            "      type = $_.Exception.GetType().FullName\n"
            "      category = $_.CategoryInfo.Reason\n"
            "      fully_qualified_error_id = $_.FullyQualifiedErrorId\n"
            "    }\n"
            "  }\n"
            "}\n"
            "$__codex_error_info = $null\n"
            "if ($__codex_error) {\n"
            "  $__codex_error_info = [PSCustomObject]@{\n"
            "    message = $__codex_error.Exception.Message\n"
            "    type = $__codex_error.Exception.GetType().FullName\n"
            "    category = $__codex_error.CategoryInfo.Reason\n"
            "    fully_qualified_error_id = $__codex_error.FullyQualifiedErrorId\n"
            "    script_stack_trace = $__codex_error.ScriptStackTrace\n"
            "    details = ($__codex_error | Out-String).Trim()\n"
            "  }\n"
            "}\n"
            "$__codex_meta = [PSCustomObject]@{\n"
            "  started_at = $__codex_start.ToString('o')\n"
            "  ended_at = $__codex_end.ToString('o')\n"
            "  duration_ms = [math]::Round((($__codex_end) - $__codex_start).TotalMilliseconds, 2)\n"
            "  error_count = $Error.Count\n"
            "  non_terminating_errors = $__codex_errors\n"
            "}\n"
            "$__codex_payload = [PSCustomObject]@{\n"
            "  ok = $__codex_ok\n"
            "  data = $__codex_data\n"
            "  error = $__codex_error_info\n"
            "  meta = $__codex_meta\n"
            "}\n"
            f"Write-Output '{token}::BEGIN'\n"
            f"$__codex_payload | ConvertTo-Json -Depth {depth} -Compress\n"
            f"Write-Output '{token}::END'\n"
        )

    def _read_envelope(self, token):
        payload_lines = []
        started = False
        while True:
            line = self.process.stdout.readline()
            if line == "":
                break
            line_stripped = line.strip()
            if line_stripped == f"{token}::BEGIN":
                started = True
                payload_lines = []
                continue
            if line_stripped == f"{token}::END":
                break
            if started:
                payload_lines.append(line)
        return "".join(payload_lines).strip()

    def _execute_enveloped(self, script, *, parameters=None, depth=8, capture_text=False, working_dir=None):
        self._start()
        token, wrapped = self._wrap_script(
            script,
            parameters=parameters,
            depth=depth,
            capture_text=capture_text,
            working_dir=working_dir,
        )
        with self._lock:
            self.process.stdin.write(wrapped)
            self.process.stdin.flush()
            payload_text = self._read_envelope(token)
        if not payload_text:
            return {"ok": False, "data": None, "error": {"message": "No PowerShell output"}, "meta": {}}
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            payload = {
                "ok": False,
                "data": payload_text,
                "error": {"message": f"Failed to parse PowerShell JSON: {exc}"},
                "meta": {},
            }
        if parameters:
            payload.setdefault("meta", {})
            payload["meta"]["parameters"] = _redact_payload(parameters)
        payload["data"] = _redact_payload(payload.get("data"))
        payload["error"] = _redact_payload(payload.get("error"))
        return payload

    def run(self, script, parameters=None, working_dir=None):
        return self._execute_enveloped(script, parameters=parameters, capture_text=True, working_dir=working_dir)

    def close(self):
        if not self.process or self.process.poll() is not None:
            return
        try:
            self.process.stdin.write("exit\n")
            self.process.stdin.flush()
            self.process.stdin.close()
            self.process.wait(timeout=5)
        except Exception:
            pass

    def run_json(self, script_or_command, parameters=None, depth=8, working_dir=None):
        return self._execute_enveloped(
            script_or_command,
            parameters=parameters,
            depth=depth,
            capture_text=False,
            working_dir=working_dir,
        )


class PowerShellModuleClient:
    def __init__(self, session=None, pwsh_path="pwsh"):
        self.session = session or PowerShellSession(pwsh_path=pwsh_path)
        self.connected = False

    def _connect_script(self):
        return None

    def _disconnect_script(self):
        return None

    def connect(self):
        if self.connected:
            return True
        script = self._connect_script()
        if script:
            result = self.session.run(script)
            if isinstance(result, dict) and not result.get("ok", True):
                raise PowerShellCommandError("PowerShell connect failed.", output=result)
        self.connected = True
        return True

    def run(self, script, parameters=None, working_dir=None):
        self.connect()
        return self.session.run(script, parameters=parameters, working_dir=working_dir)

    def run_json(self, script, parameters=None, depth=8, working_dir=None):
        return self.session.run_json(script, parameters=parameters, depth=depth, working_dir=working_dir)

    def disconnect(self):
        script = self._disconnect_script()
        if script:
            try:
                result = self.session.run(script)
                if isinstance(result, dict) and not result.get("ok", True):
                    raise PowerShellCommandError("PowerShell disconnect failed.", output=result)
            except PowerShellCommandError:
                pass
        self.connected = False
        return True

    def close(self):
        self.disconnect()
        self.session.close()
