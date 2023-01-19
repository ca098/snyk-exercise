from typing import Optional

import requests
from fastapi import HTTPException
from semver import max_satisfying

from src.models import NPMPackage, Package
from src.services.caching_service import CachingService

caching_service = CachingService()
NPM_REGISTRY_URL = "https://registry.npmjs.org"


async def get_package(name: str, version: Optional[str] = None) -> dict:
    cache_key = (
        f"{name}_{version}".replace(" ", "") if version is not None else f"{name}"
    )  # Create acceptable cache key
    cached_result = caching_service.get(cache_key)

    if cached_result is not None:
        return cached_result

    url = f"{NPM_REGISTRY_URL}/{name}"

    r = requests.get(url)
    if r.status_code != 200:
        raise HTTPException(
            status_code=404, detail=f"The package '{name}' was not found in the npm registry."
        )  # Raise exception if not found

    npm_package = r.json()
    package = NPMPackage(
        name=npm_package["name"],
        description=npm_package["description"]
        if "description" in npm_package
        else "N/A",  # Default description if not exists
        dist_tags=npm_package["dist-tags"],
        versions=npm_package["versions"],
    )
    if not version:
        version = max_satisfying(package.versions.keys(), "*")

    # Check package for the requested version
    dependencies = package.versions[version].dependencies if version in package.versions else None
    if dependencies is None:
        raise HTTPException(
            status_code=404,
            detail=f"v{version} was not found in the list of available {name} packages.",
        )

    # Return list of dependencies for selected package
    dependency_list = [
        await get_dependencies(dependency_name, dependency_range)
        for dependency_name, dependency_range in dependencies.items()
    ]

    package_result = {"name": name, "version": version, "dependencies": dependency_list}

    caching_service.put(cache_key, package_result)
    return package_result


async def get_dependencies(name: str, range: str) -> Package:
    # We cache at this level to avoid redundant npm look-ups on package dependencies we have already seen
    pd_key = f"{name}_{range}".replace(" ", "")
    circular_d_key = f"{pd_key}_dp"

    cached_result = caching_service.get(pd_key)
    circular_dep_check = caching_service.get(circular_d_key)

    if cached_result is None and circular_dep_check:
        return Package(name=name, version=range, dependencies=[])

    if cached_result is not None:
        return cached_result

    url = f"{NPM_REGISTRY_URL}/{name}"
    npm_package = requests.get(url).json()
    package = NPMPackage(
        name=npm_package["name"],
        description=npm_package["description"] if "description" in npm_package else "N/A",
        dist_tags=npm_package["dist-tags"],
        versions=npm_package["versions"],
    )

    caching_service.put(circular_d_key, True)

    dependency_list = []
    version = max_satisfying(package.versions.keys(), range)
    if version:
        new_dependencies = package.versions[version].dependencies

        # Again, it's important to return the list of dependencies so that user look-up is possible
        dependency_list = [
            await get_dependencies(dependency_name, dependency_range)
            for dependency_name, dependency_range in new_dependencies.items()
        ]

    package_result = Package(name=name, version=version or range, dependencies=dependency_list)

    caching_service.put(pd_key, package_result)

    return package_result
