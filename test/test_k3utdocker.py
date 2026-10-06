import os
import tempfile
import unittest

import k3ut

import k3utdocker

dd = k3ut.dd

this_base = os.path.dirname(__file__)


class TestK3utdocker(unittest.TestCase):
    foo_fn = "/tmp/foo"

    def _clean(self):
        # remove written file
        try:
            os.unlink(self.foo_fn)
        except OSError:
            pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_procerror(self):
        pass

    def test_build_image(self):
        # A Dockerfile that starts FROM scratch builds without a download.
        image = "k3utdocker-test-build:latest"
        with tempfile.TemporaryDirectory() as path:
            with open(os.path.join(path, "Dockerfile"), "w") as f:
                f.write("FROM scratch\nLABEL k3utdocker=test\n")

            k3utdocker.build_image(image, path)

        dcli = k3utdocker.get_client()
        tags = dcli.api.inspect_image(image)["RepoTags"]
        self.assertEqual([image], tags)

        dcli.api.remove_image(image)
