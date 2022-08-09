import textwrap
from condax.metadata import MainPackage, InjectedPackage, CondaxMetaData


def test_metadata_to_json():
    main = MainPackage("jq", apps=["jq"])
    injected = [InjectedPackage("ripgrep", apps=["rg"], include_apps=False)]
    metadata = CondaxMetaData(main, injected)

    expected = textwrap.dedent(
        """
    {
        "injected_packages": [
            {
                "apps": [
                    "rg"
                ],
                "include_apps": false,
                "name": "ripgrep"
            }
        ],
        "main_package": {
            "apps": [
                "jq"
            ],
            "include_apps": true,
            "name": "jq"
        }
    }
    """
    ).strip()

    assert expected == metadata.to_json()
