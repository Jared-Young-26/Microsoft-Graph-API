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

# Load environment variables from .env file
load_dotenv()
REQUIRED_ENV_VARS = ["TENANT_ID", "CLIENT_ID", "CLIENT_SECRET"]

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

    def run(self, script):
        self._start()
        token = f"__CODEX_PS_END__{uuid.uuid4().hex}"
        wrapped = (
            "$ErrorActionPreference = 'Stop'\n"
            "$__codex_ok = $true\n"
            "try {\n"
            f"{script}\n"
            "} catch {\n"
            "  $__codex_ok = $false\n"
            "  $_ | Out-String | Write-Output\n"
            "}\n"
            f"if ($__codex_ok) {{ Write-Output '{token}::OK' }} else {{ Write-Output '{token}::ERR' }}\n"
        )

        output_lines = []
        with self._lock:
            self.process.stdin.write(wrapped)
            self.process.stdin.flush()

            while True:
                line = self.process.stdout.readline()
                if line == "":
                    break
                line_stripped = line.strip()
                if line_stripped == f"{token}::OK":
                    return "".join(output_lines).strip()
                if line_stripped == f"{token}::ERR":
                    output = "".join(output_lines).strip()
                    raise PowerShellCommandError("PowerShell command failed.", output=output)
                output_lines.append(line)
        return "".join(output_lines).strip()

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

    def run_json(self, script, depth=8):
        output = self.run(f"{script} | ConvertTo-Json -Depth {depth}")
        if not output:
            return None
        return json.loads(output)


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
            self.session.run(script)
        self.connected = True
        return True

    def run(self, script):
        self.connect()
        return self.session.run(script)

    def run_json(self, script):
        output = self.run(f"{script} | ConvertTo-Json -Depth 8")
        if not output:
            return None
        return json.loads(output)

    def disconnect(self):
        script = self._disconnect_script()
        if script:
            try:
                self.session.run(script)
            except PowerShellCommandError:
                pass
        self.connected = False
        return True

    def close(self):
        self.disconnect()
        self.session.close()
