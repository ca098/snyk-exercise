# Snyk Recursive npm Exercise

This is my solution to the Snyk python recursive npm [PR review](https://github.com/snyk/snyk-code-review-exercise/pull/9) exercise.
I have included comments around any logic that I have changed. It is worth noting that the biggest issue on the original PR is that there is no caching. Therefore, dependencies will require
multiple `npm` look-ups in the original state. I have cached at both the `get_dependencies()` and `get_package()` methods in order to improve performance. Caching has been done with `redis` rather than a simple hash table, this was so that we can clear the cache independently of runtime as well as setting an expiry to flush the cache. This method is ideal as packages will occasionally be updated and it should keep them in-line with the current `npm` registry.

The other issue was that in the original PR the format uses the `npm` package name as a key. This is not advisable as it makes it near impossible to
query the response data when the key is dynamic.

Other than the above, the issues are simply detecting when the response from the npm registry does not include a description,
as well as determining when you're visiting a circular dependency. An example of this can be seen [here](https://npm.anvaka.com/#/view/2d/d) with reference to the `npm` package `d`. Without this check you will run into a maximum recursion depth exceeded error, as it will keep iterating over a collection of the same packages.

If you're looking for a package to stress test use `largest-package` -> https://www.npmjs.com/package/largest-package

## Prerequisites

* [Python 3.9](https://www.python.org/downloads/release/python-399/)

## Getting Started

To install dependencies and start the server in development mode:

```sh
brew install redis
brew services start redis

pip install poetry
poetry install
python src/app.py
```

The server will now be running on an available port (defaulting to 3000) and
will restart on changes to the src files.

Then we can try the `/package` endpoint. Here is an example that uses `curl` and
`jq`, but feel free to use any client.

```sh
curl -s http://localhost:3000/package/react/16.13.0 | jq .
```

Most of the code is boilerplate; the logic for the `/package` endpoint can be
found in [src/package.py](src/package.py), and some basic tests in
[test/test_package.py](test/test_package.py)

You can run the tests with:

```sh
pytest
```
