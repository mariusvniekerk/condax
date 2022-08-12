import pathlib
import tempfile
import textwrap
from condax.config import C, set_via_file, set_via_value

Path = pathlib.Path


def test_set_via_value_1():
    prefix_dir = Path("/some/arbitrary dir/path/to/something")
    set_via_value(prefix_dir=prefix_dir)
    assert C.prefix_dir() == prefix_dir


def test_set_via_value_2():
    bin_dir = Path("/yet/another dir/path/toward/foo/bar")
    set_via_value(bin_dir=bin_dir)
    assert C.bin_dir() == bin_dir


def test_set_via_value_3():
    bin_dir = Path("~/.babakeke")
    set_via_value(bin_dir=bin_dir)
    assert C.bin_dir() == Path.home() / bin_dir.name


def test_set_via_value_4():
    prefix_dir = Path("~/.abc34178")
    set_via_value(prefix_dir=prefix_dir)
    assert C.prefix_dir() == Path.home() / prefix_dir.name


def test_set_via_file_1():
    temp = tempfile.NamedTemporaryFile()
    text = textwrap.dedent(
        """
        prefix_dir: /some/../path/to/
        bin_dir: "~/.yet/another path/toward/../foo/"
        channels: ["fastchan"]
    """
    )
    temp.write(text.encode("utf-8"))
    temp.seek(0)

    set_via_file(temp.name)
    assert C.prefix_dir() == Path("/path/to/")
    assert C.bin_dir() == Path.home() / ".yet/another path/foo"
    assert "fastchan" in C.channels()
