"""Generate openapi doc."""

from fastapi.openapi.utils import get_openapi
from rdf_diff_store.main import app
import yaml

spec = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version=app.openapi_version,
    description=app.description,
    routes=app.routes,
)

with open("openapi.yml", "w") as f:
    f.write(yaml.dump(spec))
