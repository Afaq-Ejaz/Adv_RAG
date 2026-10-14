"""Import every ORM model so `Base.metadata` is complete (used by Alembic and schema tests).

Each phase that adds tables appends its models module here.
"""

from advance_rag.auth import models as auth_models
from advance_rag.core.db import Base
from advance_rag.documents import models as document_models
from advance_rag.tenancy import models as tenancy_models

__all__ = ["Base", "auth_models", "document_models", "tenancy_models"]
