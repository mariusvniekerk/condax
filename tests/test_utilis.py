from condax.utils import split_match_specs


def test_split_match_specs():
    x = split_match_specs("numpy=1.11")
    assert x == ("numpy", "=1.11")

    x = split_match_specs(" numpy == 1.11")
    assert x == ("numpy", "== 1.11")

    x = split_match_specs("numpy > 1.11")
    assert x == ("numpy", "> 1.11")

    x = split_match_specs("numpy=1.11.1|1.11.3")
    assert x == ("numpy", "=1.11.1|1.11.3")

    x = split_match_specs("numpy>=1.8,<2")
    assert x == ("numpy", ">=1.8,<2")

    x = split_match_specs("numpy")
    assert x == ("numpy", "")

