import os
import tempfile
import unittest
from unittest import mock

import docker.errors
import docker.utils
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


class TestPullImage(unittest.TestCase):
    def test_pull_image_passes_the_whole_reference(self):
        # The second item is how pull() of the SDK splits the reference.
        cases = (
            ("zookeeper:3.4.10", ("zookeeper", "3.4.10")),
            ("busybox", ("busybox", None)),
            ("localhost:5000/example:tag", ("localhost:5000/example", "tag")),
            ("busybox@sha256:" + "a" * 64, ("busybox", "sha256:" + "a" * 64)),
        )
        for image, repository_tag in cases:
            dcli = mock.MagicMock()
            dcli.api.images.return_value = []
            with mock.patch("k3utdocker.utdocker.get_client", return_value=dcli):
                k3utdocker.pull_image(image)

            self.assertEqual([mock.call(image)], dcli.api.pull.call_args_list, image)
            self.assertEqual(repository_tag, docker.utils.parse_repository_tag(image))


class TestBuildImage(unittest.TestCase):
    def test_build_image_raises_an_error_in_the_stream(self):
        stream = [
            {"stream": "Step 1/2 : FROM scratch\n"},
            {"error": "boom", "errorDetail": {"message": "boom"}},
        ]
        dcli = mock.MagicMock()
        dcli.api.images.return_value = []
        dcli.api.build.return_value = iter(stream)

        with (
            mock.patch("k3utdocker.utdocker.get_client", return_value=dcli),
            self.assertRaises(docker.errors.BuildError) as ctx,
        ):
            k3utdocker.build_image("k3utdocker-test:latest", "/path")

        self.assertEqual(
            [mock.call(path="/path", nocache=True, tag="k3utdocker-test:latest", decode=True)],
            dcli.api.build.call_args_list,
        )
        self.assertEqual("boom", ctx.exception.msg)
        self.assertEqual(stream, ctx.exception.build_log)
