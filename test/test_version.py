from peakrdl_pyral_runtime.__about__ import __version__ as runtime_version
from peakrdl_pyral.__about__ import __version__ as exporter_version

from peakrdl_pyral_runtime.dbapi import DBAPI
from peakrdl_pyral.db_generator import DBAPI_VERSION

def test_versions_equal():
    assert runtime_version == exporter_version
    assert DBAPI_VERSION == DBAPI.DBAPI_VERSION
