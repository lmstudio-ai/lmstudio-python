# LM Studio Python SDK semi-automated test suite

The SDK test suite is currently only partially automated: the
tests need to be executed on a machine with the LM Studio
desktop application already running locally. If the test suite
is running on Windows under WSL, WSL must be running with mirrored
networking enabled (otherwise the test suite won't be able to
access the desktop app via the local loopback interface).

In addition to the desktop app being app and run, the following
conditions must also be met for the test suite to pass:

- the API server must be enabled and running on port 1234
- the following models model must be loaded with their default identifiers
  - `text-embedding-nomic-embed-text-v1.5` (text embedding model)
  - `llama-3.2-1b-instruct` (text LLM)
  - `ZiangWu/MobileVLM_V2-1.7B-GGUF` (visual LLM)
  - `qwen2.5-7b-instruct-1m` (tool using LLM)

Additional models should NOT be loaded when running the test suite,
as some model querying tests may fail in that case.

There are also some JIT model loading/unloading test cases which
expect `smollm2-135m` (small text LLM) to already be downloaded.
A full test run will download this model (since it is also the
model used for the end-to-end search-and-download test case).

There's no problem with having additional models downloaded.
The only impact is that the test that checks all of the expected
models can be found in the list of downloaded models will take a
little longer to run.


# Loading and unloading the required models

The `load-test-models` `tox` environment can be used to ensure the required
models are loaded *without* a time-to-live set:

```console
$ tox -m load-test-models
```

To ensure the test models are loaded with the config expected by the test suite,
any previously loaded instances are unloaded first.

There is also an `unload-test-models` `tox` environment that can be used to
explicitly unload the test models:

```console
$ tox -m unload-test-models
```

The model downloading test cases can be specifically run with:

```console
$ tox -m test -- -k test_download_model
```


## Adding new tests

Test files should follow the following naming conventions:

- `test_XYZ.py`: mix of async and sync test cases for `XYZ` that aren't amenable to automated conversion
  (for whatever reason; for example, `anyio.fail_after` has no sync counterpart)
- `async/test_XYZ_async.py` : async test cases for `XYZ` that are amenable to automated sync conversion;
  all test method names should also end in `_async`.
- `sync/test_XYZ_sync.py` : sync test cases auto-generated from `test_XYZ_async.py`

`python async2sync.py` will run the automated conversion (there are no external dependencies,
so there's no dedicated `tox` environment for this).

## Marking slow tests

`pytest` accepts a `--durations=N` option to print the "N" slowest tests (and their durations).

Any tests that consistently take more than 3 seconds to execute should be marked as slow. It's
also reasonable to mark any tests that take more than a second as slow.

Tests that are missing the marker can be identified via:

```
tox -m test -- --durations=10 -m "not slow"
```

Tests that have the marker but shouldn't can be identified via:

```
tox -m test -- --durations=0 -m "slow"
```

(the latter command prints the durations for all executed tests)
