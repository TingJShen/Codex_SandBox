import subprocess
import unittest

from scripts import dashboard_launcher
from scripts import status_dashboard


class QuerySubprocessConfigTests(unittest.TestCase):
    def test_windows_query_subprocess_config_hides_console(self) -> None:
        kwargs = status_dashboard.build_query_subprocess_kwargs("nt")

        self.assertIn("startupinfo", kwargs)
        self.assertIn("creationflags", kwargs)
        self.assertEqual(
            kwargs["creationflags"],
            getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        self.assertIsNotNone(kwargs["startupinfo"])
        self.assertTrue(kwargs["startupinfo"].dwFlags & subprocess.STARTF_USESHOWWINDOW)
        self.assertEqual(kwargs["startupinfo"].wShowWindow, 0)

    def test_non_windows_query_subprocess_config_is_empty(self) -> None:
        self.assertEqual(status_dashboard.build_query_subprocess_kwargs("posix"), {})

    def test_dashboard_default_port_is_8766(self) -> None:
        self.assertEqual(status_dashboard.DEFAULT_PORT, 8766)
        self.assertEqual(dashboard_launcher.status_dashboard.DEFAULT_PORT, 8766)


if __name__ == "__main__":
    unittest.main()
