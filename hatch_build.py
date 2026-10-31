from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_support import sync_all

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class SyncToolkitHook(BuildHookInterface):
    def initialize(self, version, build_data):
        sync_all()
