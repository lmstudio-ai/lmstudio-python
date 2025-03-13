# LM Studio Python SDK

## Using the SDK

### Installation

The SDK can be installed from PyPI as follows:

```console
$ pip install lmstudio
```

Installation from the repository URL or a local clone is also
supported for development and pre-release testing purposes.

## Examples

The base component of the LM Studio SDK is the (synchronous) `Client`.
This should be created once and used to manage the underlying
websocket connections to the LM Studio instance.

However, a top level convenience API is provided for convenience in
interactive use (this API implicitly creates a default `Client` instance
which will remain active until the Python interpreter is terminated).

Using this convenience API, requesting text completion from an already
loaded LLM is as straightforward as:

```python
import lmstudio as lms

model = lms.llm()
model.complete("Once upon a time,")
```

Requesting a chat response instead only requires the extra step of
setting up a `Chat` helper to manage the chat history and include
it in response prediction requests:

```python
import lmstudio as lms

EXAMPLE_MESSAGES = (
    "My hovercraft is full of eels!",
    "I will not buy this record, it is scratched."
)

model = lms.llm()
chat = lms.Chat("You are a helpful shopkeeper assisting a foreign traveller")
for message in EXAMPLE_MESSAGES:
    chat.add_user_message(message)
    print(f"Customer: {message}")
    response = model.respond(chat)
    chat.add_assistant_response(response)
    print(f"Shopkeeper: {response}")
```

Additional SDK examples and usage recommendations may be found in the main
[LM Studio Python SDK documentation](https://lmstudio.ai/docs/python).

## SDK versioning

The LM Studio Python SDK uses a 3-part `X.Y.Z` numeric version identifier:

* `X`: incremented when the minimum version of significant dependencies is updated
  (for example, dropping support for older versions of Python or LM Studio).
  Previously deprecated features may be dropped when this part of the version number
  increases.
* `Y`: incremented when new features are added, or some other notable change is
  introduced (such as support for additional versions of Python). New deprecation
  warnings may be introduced when this part of the version number increases.
* `Z`: incremented for bug fix releases which don't contain any other changes.
  Adding exceptions and warnings for previously undetected situations is considered
  a bug fix.

This versioning policy is intentionally similar to [semantic versioning](https://semver.org/),
but differs in the specifics of when the different parts of the version number will be updated.

Release candidates *may* be published prior to full releases, but this will typically only
occur when seeking broader feedback on particular features prior to finalizing the release.

Outside the preparation of a new release, the SDK repository will include a `.devN` suffix
on the nominal Python package version.

## Contributing to SDK development

### Fetching the source code

```console
$ git clone https://github.com/lmstudio-ai/lmstudio-python
$ cd lmstudio-python
```

To be able to run `tox -e sync-sdk-schema`, it is also
necessary to ensure the `lmstudio-js` submodule is updated:

```console
$ git submodule update --init --recursive
```

### Development Environment

In order to work on the Python SDK, you need to install
:pypi:`pdm`, :pypi:`tox`, and :pypi:`tox-pdm`
(everything else can be executed via `tox` environments).

Given these tools, the default development environment can be set up
and other commands executed as described below.

The simplest option for handling that is to install `uv`, and then use
its `uv tool` command to set up `pdm` and a second environment
with `tox` + `tox-pdm`. `pipx` is another reasonable option for this task.

In order to _use_ the Python SDK, you just need some form of
Python environment manager (since `lmstudio-python` publishes
the package `lmstudio` to PyPI).

### Recommended local checks

The set of checks recommended for local execution are accessible via
the `check` marker in `tox`:

```console
$ tox -m check
```

This runs the same checks as the `static` and `test` markers (described below).

### Code consistency checks

The project source code is autoformatted and linted using :pypi:`ruff`.
It also uses :pypi:`mypy` in strict mode to statically check that Python APIs
are being accessed as expected.

All of these commands can be invoked via tox:

```console
$ tox -e format
```

```console
$ tox -e lint
```

```console
$ tox -e typecheck
```

Linting and type checking can be executed together using the `static` marker:

```console
$ tox -m static
```

Avoid using `# noqa` comments to suppress these warnings - wherever
possible, warnings should be fixed instead. `# noqa` comments are
reserved for rare cases where the recommended style causes severe
readability problems, and there isn't a more explicit mechanism
(such as `typing.cast`) to indicate which check is being skipped.

`# fmt: off/on` and `# fmt: skip` comments may be used as needed
when the autoformatter makes readability worse instead of better
(for example, collapsing lists to a single line when they intentionally
cover multiple lines, or breaking alignment of end-of-line comments).

### Automated testing

The project's tests are written using the :pypi:`pytest` test framework.
:pypi:`tox` is used to automate the setup and execution of these tests
across multiple Python versions. One of these is nominated as the
default test target, and is accessible via the `test` marker:

```console
$ tox -m test
```

You can also use other defined versions by specifying the target
environment directly:

```console
$ tox -e py3.11
```

There are additional labels defined for running the oldest test environment,
the latest test environment, and all test environments:

```console
$ tox -m test_oldest
$ tox -m test_latest
$ tox -m test_all
```

To ensure all the required models are loaded before running the tests, run the
following command:

```
$ tox -e load-test-models
```

`tox` has been configured to forward any additional arguments it is given to
`pytest`. This enables the use of pytest's
[rich CLI](https://docs.pytest.org/en/stable/how-to/usage.html#specifying-which-tests-to-run).
In particular, you can select tests using all the options that pytest provides:

```console
$ # Using file name
$ tox -m test -- tests/test_basics.py
$ # Using markers
$ tox -m test -- -m "slow"
$ # Using keyword text search
$ tox -m test -- -k "catalog"
```

Additional notes on running and updating the tests can be found in the
`tests/README.md` file.


### Expanding the API

- the content of `src/lmstudio/_sdk_models` is automatically generated by the
  `sync-sdk-schema.py` script in `sdk-schema` and should not be modified directly.
  Run `tox -e sync-sdk-schema` to regenerate the Python submodule from the existing
  export of the `lmstudio-js` schema (for example, after modifying the data model
  template). Run `tox -e sync-sdk-schema -- --regen-schema` after updating the
  `sdk-schema/lmstudio-js` submodule itself to a newer iteration of the
  `lmstudio-js` JSON API.
- as support for new API namespaces is added to the SDK, each should get a dedicated
  session type (similar to those for the already supported namespaces), even if it
  is only used privately by the client implementation.
- as support for new API channel endppoints is added to the SDK, each should get a
  dedicated base endpoint type (similar to those for the already supported channels).
  This avoids duplicating the receive message processing between the sync and async APIs.
- the `json_api.SessionData` base class is useful for defining rich result objects which
  offer additional methods that call back into the SDK (for example, this is how downloaded
  model listings offer their interfaces to load a new instance of a model).
