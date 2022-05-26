from __future__ import annotations
from typing import Optional, List  # Add list

from pydantic import BaseModel


class Package(BaseModel):
    name: str
    version: str
    dependencies: Optional[List[Package]] = []


class NPMPackageVersion(BaseModel):
    name: str
    version: str
    dependencies: Optional[dict[str, str]] = {}


class NPMPackage(BaseModel):
    name: str
    description: str
    dist_tags: dict[str, str]
    versions: dict[str, NPMPackageVersion]


Package.update_forward_refs()
