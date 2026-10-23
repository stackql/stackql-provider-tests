from pathlib import Path
import runpy
import subprocess
import unittest
from unittest.mock import patch


VERIFY = runpy.run_path(str(Path(__file__).with_name("verify-provider.py")))
CONFIG = {"verifyConfig": {"nopVerify": False}}


class SignedProviderTests(unittest.TestCase):
    def test_reads_provider_and_every_service(self):
        with patch("subprocess.run", side_effect=[
            subprocess.CompletedProcess([], 0, "name\none\ntwo\n", ""),
            subprocess.CompletedProcess([], 0, "name\nthing\n", ""),
            subprocess.CompletedProcess([], 0, "name\nother\n", ""),
        ]) as run:
            self.assertEqual(VERIFY["verify_provider"]("stackql", "example", CONFIG), (2, 2))
            self.assertEqual(run.call_count, 3)
            self.assertIn("--registry=", run.call_args.args[0][3])

    def test_zero_exit_status_does_not_hide_verification_failure(self):
        with patch("subprocess.run", return_value=subprocess.CompletedProcess(
            [], 0, "", "pqsig: signature verification failed"
        )):
            with self.assertRaisesRegex(RuntimeError, "signature verification failed"):
                VERIFY["verify_provider"]("stackql", "example", CONFIG)

    def test_rejects_disabled_verification(self):
        with self.assertRaisesRegex(ValueError, "nopVerify"):
            VERIFY["verify_provider"]("stackql", "example", {"verifyConfig": {"nopVerify": True}})

    def test_empty_metadata_is_not_success(self):
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, "", "")):
            with self.assertRaisesRegex(RuntimeError, "expected named metadata"):
                VERIFY["verify_provider"]("stackql", "example", CONFIG)
