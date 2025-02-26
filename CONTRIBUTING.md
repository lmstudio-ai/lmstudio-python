# Contributing

`lmstudio-python` is the Python SDK for LM Studio. It is an open-source project under the Apache 2.0 license. We welcome community contributions. There are many ways to help, from writing tutorials or blog posts, improving the documentation, submitting bug reports and feature requests or contributing code which can be incorporated into the SDK itself.

Note: the SDK documentation is maintained in combination with the [`lmstudio.js`](https://github.com/lmstudio-ai/lmstudio.js)
in a dedicated [documentation repo](https://github.com/lmstudio-ai/docs).

## Before you start

If you are planning to add a feature or fix a bug, please open an issue first to discuss it. This is mainly to avoid duplicate work and to make sure that your contribution is in line with the project's goals. The LM Studio team is available to chat in the `#dev-chat` channel within the [LM Studio Discord server](https://discord.gg/pwQWNhmQTY).

## How to make code contributions

_`lmstudio-python` requires Python 3.11 or later_

1. Fork this repository
2. Clone your fork: `git clone git@github.com:lmstudio-ai/lmstudio-python.git` onto your local development machine
3. Install the `tox` environment manager via your preferred mechanism (such as `pipx` or `uvx`)
4. Run `tox -m test` to run the test suite (`pytest` is the test runner, pass options after a `--` separator)
5. Run `tox -m static` to run the linter and typechecker
6. Run `tox -e format` to run the code autoformatter

Refer to [`README.md`](./README.md) and [`testing/README.md`](testing/README.md)for additional details
on working with the `lmstudio-python` code and test suite.

## Q&A

- **How does `lmstudio-python` communicate with LM Studio?**

  `lmstudio-python` communicates with LM Studio through its native dedicated websocket API, rather than via its Open AI compatibility layer.

- **How does `lmstudio-python` relate to `lmstudio.js`?**

  `lmstudio-python` communicates with LM Studio based on JSON interface types defined in `lmstudio.js`.
  The `lmstudio-python` repository includes `lmstudio.js` as a submodule in order to support generating
  the Python API interface classes from the JSON schema definitions exported by `lmstudio.js`.

## Questions

If you have any other questions, feel free to join the [LM Studio Discord server](https://discord.gg/pwQWNhmQTY) and ask in the `#dev-chat` channel.

## Is the LM Studio team hiring?

Yes, yes we are. Please see our careers page: https://lmstudio.ai/careers.
