from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)

invalid_package = "this_package_does_not_exist"
invalid_version = "112.0.1.1"


def test_get_package():
    response = client.get("/package/react/16.13.0")
    assert response.status_code == 200
    assert response.json() == {
        "name": "react",
        "version": "16.13.0",
        "dependencies": [
            {
                "name": "loose-envify",
                "version": "1.4.0",
                "dependencies": [{"name": "js-tokens", "version": "4.0.0", "dependencies": []}],
            },
            {"name": "object-assign", "version": "4.1.1", "dependencies": []},
            {
                "name": "prop-types",
                "version": "15.8.1",
                "dependencies": [
                    {
                        "name": "loose-envify",
                        "version": "1.4.0",
                        "dependencies": [
                            {"name": "js-tokens", "version": "4.0.0", "dependencies": []}
                        ],
                    },
                    {"name": "object-assign", "version": "4.1.1", "dependencies": []},
                    {"name": "react-is", "version": "16.13.1", "dependencies": []},
                ],
            },
        ],
    }


def test_invalid_package_version():
    response = client.get(f"package/react/{invalid_version}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"v{invalid_version} was not found in the list of available react packages."
    }


def test_invalid_package_and_invalid_package_version():
    response = client.get(f"package/{invalid_package}/{invalid_version}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"The package '{invalid_package}' was not found in the npm registry."
    }


def test_invalid_package():
    response = client.get(f"package/{invalid_package}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"The package '{invalid_package}' was not found in the npm registry."
    }


def test_get_package_no_version():
    response = client.get("/package/react")
    assert response.status_code == 200
    assert response.json() == {
        "name": "react",
        "version": "18.1.0",
        "dependencies": [
            {
                "name": "loose-envify",
                "version": "1.4.0",
                "dependencies": [{"name": "js-tokens", "version": "4.0.0", "dependencies": []}],
            }
        ],
    }


def test_circular_dependency():
    """
    Ensure we do not get into a recursion depth exceeded with circular dependencies
    """

    response = client.get("/package/d")
    assert response.status_code == 200
    assert response.json() == {
        "name": "d",
        "version": "1.0.1",
        "dependencies": [
            {
                "name": "es5-ext",
                "version": "0.10.61",
                "dependencies": [
                    {
                        "name": "es6-iterator",
                        "version": "2.0.3",
                        "dependencies": [
                            {
                                "name": "d",
                                "version": "1.0.1",
                                "dependencies": [
                                    {"name": "es5-ext", "version": "^0.10.50", "dependencies": []},
                                    {"name": "type", "version": "1.2.0", "dependencies": []},
                                ],
                            },
                            {
                                "name": "es5-ext",
                                "version": "0.10.61",
                                "dependencies": [
                                    {
                                        "name": "es6-iterator",
                                        "version": "^2.0.3",
                                        "dependencies": [],
                                    },
                                    {
                                        "name": "es6-symbol",
                                        "version": "3.1.3",
                                        "dependencies": [
                                            {
                                                "name": "d",
                                                "version": "1.0.1",
                                                "dependencies": [
                                                    {
                                                        "name": "es5-ext",
                                                        "version": "^0.10.50",
                                                        "dependencies": [],
                                                    },
                                                    {
                                                        "name": "type",
                                                        "version": "1.2.0",
                                                        "dependencies": [],
                                                    },
                                                ],
                                            },
                                            {
                                                "name": "ext",
                                                "version": "1.6.0",
                                                "dependencies": [
                                                    {
                                                        "name": "type",
                                                        "version": "2.6.0",
                                                        "dependencies": [],
                                                    }
                                                ],
                                            },
                                        ],
                                    },
                                    {"name": "next-tick", "version": "1.1.0", "dependencies": []},
                                ],
                            },
                            {
                                "name": "es6-symbol",
                                "version": "3.1.3",
                                "dependencies": [
                                    {
                                        "name": "d",
                                        "version": "1.0.1",
                                        "dependencies": [
                                            {
                                                "name": "es5-ext",
                                                "version": "^0.10.50",
                                                "dependencies": [],
                                            },
                                            {
                                                "name": "type",
                                                "version": "1.2.0",
                                                "dependencies": [],
                                            },
                                        ],
                                    },
                                    {
                                        "name": "ext",
                                        "version": "1.6.0",
                                        "dependencies": [
                                            {
                                                "name": "type",
                                                "version": "2.6.0",
                                                "dependencies": [],
                                            }
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "es6-symbol",
                        "version": "3.1.3",
                        "dependencies": [
                            {
                                "name": "d",
                                "version": "1.0.1",
                                "dependencies": [
                                    {"name": "es5-ext", "version": "^0.10.50", "dependencies": []},
                                    {"name": "type", "version": "1.2.0", "dependencies": []},
                                ],
                            },
                            {
                                "name": "ext",
                                "version": "1.6.0",
                                "dependencies": [
                                    {"name": "type", "version": "2.6.0", "dependencies": []}
                                ],
                            },
                        ],
                    },
                    {"name": "next-tick", "version": "1.1.0", "dependencies": []},
                ],
            },
            {"name": "type", "version": "1.2.0", "dependencies": []},
        ],
    }
