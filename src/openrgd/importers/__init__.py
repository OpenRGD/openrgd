from .urdf.parser import URDFImporter
from .usd.parser import USDImporter

# Mappa Estensione -> Classe Importer
# Supportiamo più estensioni per lo stesso parser (es. usda/usdc)
IMPORTER_REGISTRY = {
    ".urdf": URDFImporter,
    ".xml": URDFImporter,   # Spesso URDF sono .xml generici
    ".usda": USDImporter,
    ".usd": USDImporter     # Nota: il parser USD deve gestire il check ASCII interno
}

def get_importer_class(extension: str):
    """Returns the importer class for a given extension, or None."""
    return IMPORTER_REGISTRY.get(extension.lower())

def list_supported_formats():
    """Returns a list of supported extensions."""
    return list(IMPORTER_REGISTRY.keys())