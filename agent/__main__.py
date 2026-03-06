from __future__ import annotations

import argparse
import os
import sys

from .runtime import AgentRuntime
from .config import load_agent_config


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "pair":
        pair_parser = argparse.ArgumentParser(prog="gas-agent pair", description="Pair an agent with a control plane via code")
        pair_parser.add_argument("control_plane_url", help="Control plane base URL (ex: http://127.0.0.1:8000)")
        pair_parser.add_argument("pairing_code", help="One-time pairing code from the UI/bootstrap page")
        pair_parser.add_argument(
            "--config",
            dest="config_path",
            default=None,
            help="Path to agent config JSON (optional).",
        )
        args = pair_parser.parse_args(sys.argv[2:])
        os.environ["CONTROL_PLANE_URL"] = str(args.control_plane_url or "").strip()
        os.environ["GAS_PAIRING_CODE"] = str(args.pairing_code or "").strip()
        config = load_agent_config(args.config_path)
        runtime = AgentRuntime(config)
        runtime.register_only()
        return 0

    parser = argparse.ArgumentParser(prog="gas-agent", description="Graph Admin Studio execution agent")
    parser.add_argument(
        "--config",
        dest="config_path",
        default=None,
        help="Path to agent config JSON (optional).",
    )
    parser.add_argument(
        "--register-only",
        dest="register_only",
        action="store_true",
        help="Register/pair and exit (does not start polling loop).",
    )
    args = parser.parse_args()

    config = load_agent_config(args.config_path)
    runtime = AgentRuntime(config)
    if args.register_only:
        runtime.register_only()
        return 0
    runtime.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
