from pathlib import Path
import pytest
from acquisition_service.mapping import load_mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODBUS_MAPPING_PATH = (
    PROJECT_ROOT
    / "config"
    / "modbus_mapping.yaml"
)


@pytest.fixture
def modbus_mapping_config():
    """
    Carrega o mapping Modbus real utilizado
    pelo Acquisition Service.
    """
    return load_mapping(
        MODBUS_MAPPING_PATH
    )
