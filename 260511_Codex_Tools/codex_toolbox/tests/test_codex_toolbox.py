import json
import inspect
import tempfile
import unittest
from pathlib import Path

from codex_toolbox import app as toolbox_app
from codex_toolbox.codex_repair import (
    build_repair_command,
    read_account_summary,
)


class CodexRepairToolTests(unittest.TestCase):
    def test_read_account_summary_prefers_active_account_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "accounts.json").write_text(
                json.dumps(
                    {
                        "currentAccountId": "current-id",
                        "settings": {"activeAccountId": "active-id"},
                        "accounts": [
                            {"id": "current-id", "label": "Current"},
                            {"id": "active-id", "label": "Active"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            summary = read_account_summary(root)

        self.assertEqual(summary.current_account_id, "current-id")
        self.assertEqual(summary.active_account_id, "active-id")
        self.assertEqual(summary.effective_account_id, "active-id")
        self.assertEqual(summary.account_count, 2)

    def test_build_repair_command_launches_existing_powershell_gui(self):
        command = build_repair_command(
            script_path=Path(r"D:\Codex_Sandbox\Codex_Resume\CodexThreadRepairGui.ps1"),
            powershell_exe="powershell",
        )

        self.assertEqual(command[0], "powershell")
        self.assertIn("-NoProfile", command)
        self.assertIn("-ExecutionPolicy", command)
        self.assertIn("Bypass", command)
        self.assertIn("-File", command)
        self.assertEqual(command[-1], r"D:\Codex_Sandbox\Codex_Resume\CodexThreadRepairGui.ps1")

    def test_toolbox_registry_keeps_repair_first_and_registers_dashboards(self):
        tools = toolbox_app.get_tool_specs()
        tool_ids = [tool.tool_id for tool in tools]

        self.assertGreaterEqual(len(tools), 3)
        self.assertEqual(tools[0].tool_id, "codex_thread_repair")
        self.assertEqual(tools[1].tool_id, "gpu_status_dashboard")
        self.assertIn("col_realtime_orchestration", tool_ids)

    def test_dashboard_command_targets_packaged_gpu_dashboard_exe(self):
        command = toolbox_app.build_gpu_dashboard_command(
            exe_path=Path(r"D:\Codex_Sandbox\Huawei_Hard\GPUStatusDashboard.exe")
        )

        self.assertEqual(command, [r"D:\Codex_Sandbox\Huawei_Hard\GPUStatusDashboard.exe"])

    def test_col_realtime_command_launches_project_dashboard(self):
        command = toolbox_app.build_col_realtime_command(
            script_path=Path(r"D:\Codex_Sandbox\260421_Codex_Language\colang\realtime.py"),
            python_exe="python",
        )

        self.assertEqual(command[0], "python")
        self.assertEqual(command[1], r"D:\Codex_Sandbox\260421_Codex_Language\colang\realtime.py")
        self.assertIn("--scan-count", command)
        self.assertIn("8765", command)

    def test_toolbox_status_and_launch_are_backgrounded(self):
        refresh_source = inspect.getsource(toolbox_app.CodexToolboxApp.refresh_status)
        launch_source = inspect.getsource(toolbox_app.CodexToolboxApp.launch_selected_tool)

        self.assertIn("threading.Thread", refresh_source)
        self.assertIn("_load_status", refresh_source)
        self.assertIn("threading.Thread", launch_source)
        self.assertIn("_launch_tool", launch_source)


if __name__ == "__main__":
    unittest.main()
