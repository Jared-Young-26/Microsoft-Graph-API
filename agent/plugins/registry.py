from __future__ import annotations

from typing import List

from .interface import AgentPlugin
from .demo import DemoPlugin
from .runner_core import RunnerCorePlugin
from .graph_runner import GraphRunnerPlugin
from .vision_u_eye_runner import VisionUEyeRunnerPlugin
from .windows_powershell_runner import WindowsPowerShellRunnerPlugin


def load_plugins() -> List[AgentPlugin]:
    """Plugin discovery (static import list for v0)."""
    return [
        RunnerCorePlugin(),
        DemoPlugin(),
        GraphRunnerPlugin(),
        VisionUEyeRunnerPlugin(),
        WindowsPowerShellRunnerPlugin(),
    ]
