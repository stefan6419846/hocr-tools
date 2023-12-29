import shutil
import subprocess
from pathlib import Path
from unittest import TestCase


class SmokeTests(TestCase):
    @classmethod
    def get_tool_list(cls):
        base_directory = Path(__file__).parent.parent
        base_directory = base_directory / 'hocr_tools_lib' / 'tools'
        return [
            path.stem.replace('_', '-') for path in base_directory.glob('*.py')
            if path.stem.startswith('hocr_')
        ]

    def test_help(self):
        for tool in self.get_tool_list():
            with self.subTest(tool):
                binary_path = shutil.which(tool)
                self.assertIsNotNone(binary_path)
                subprocess.check_call(
                    [binary_path, '-h'], stdout=subprocess.PIPE
                )
                subprocess.check_call(
                    [binary_path, '--help'], stdout=subprocess.PIPE
                )
