# Contributing to Our Open Source Projects

First off, thank you for considering contributing to our open source projects! 👾❤️ 

`lmstudio-python` is the Python SDK for LM Studio. It is an open-source project under the MIT license. We welcome community contributions. 

There are many ways to help, from writing tutorials or blog posts, improving the documentation, submitting bug reports and feature requests or contributing code which can be incorporated into the SDK itself.

Note: the SDK documentation is maintained in combination with [`lmstudio-js`](https://github.com/lmstudio-ai/lmstudio-js)
in a dedicated [documentation repo](https://github.com/lmstudio-ai/docs).

## Communication

- **The best way to communicate with the team is to open an issue in this repository**
- For bug reports, include steps to reproduce, expected behavior, and actual behavior
- For feature requests, explain the use case and benefits clearly

## Before You Contribute

- **If you find an existing issue you'd like to work on, please comment on it first and tag the team**
- This allows us to provide guidance and ensures your time is well spent
- **We discourage drive-by feature PRs** without prior discussion - we want to make sure your efforts align with our roadmap and won't go to waste

## Development Workflow

`lmstudio-python` makes extensive use of pattern matching and hence requires _Python 3.10 or later_

1. Fork this repository
2. Clone your fork: `git clone git@github.com:lmstudio-ai/lmstudio-python.git` onto your local development machine
3. Install the `tox` environment manager via your preferred mechanism (such as `pipx` or `uvx`)
4. Run `tox -m test` to run the test suite (`pytest` is the test runner, pass options after a `--` separator)
5. Run `tox -m static` to run the linter and typechecker
6. Run `tox -e format` to run the code autoformatter

Refer to [`README.md`](./README.md) and [`testing/README.md`](testing/README.md)for additional details
on working with the `lmstudio-python` code and test suite.

## Creating Good Pull Requests

### Keep PRs Small and Focused

- Address one concern per PR
- Smaller PRs are easier to review and more likely to be merged quickly

### Write Thoughtful PR Descriptions

- Clearly explain what the PR does and why
- When applicable, show before/after states or screenshots
- Include any relevant context for reviewers
- Reference the issue(s) your PR addresses with GitHub keywords (Fixes #123, Resolves #456)

### Quality Expectations

- Follow existing code style and patterns
- Include tests for new functionality
- Ensure all tests pass
- Update documentation as needed

## Code Review Process

- Maintainers will review your PR as soon as possible
- We may request changes or clarification
- Once approved, a maintainer will merge your contribution

## Contributor License Agreement (CLA)

- We require all contributors to sign a Contributor License Agreement (CLA)
- For first-time contributors, a bot will automatically comment on your PR with instructions
- You'll need to accept the CLA before we can merge your contribution
- This is standard practice in open source and helps protect both contributors and the project

## Q&A

- **How does `lmstudio-python` communicate with LM Studio?**

  `lmstudio-python` communicates with LM Studio through its native dedicated websocket API, rather than via its Open AI compatibility layer.

- **How does `lmstudio-python` relate to `lmstudio-js`?**

  `lmstudio-python` communicates with LM Studio based on JSON interface types defined in `lmstudio-js`.
  The `lmstudio-python` repository includes `lmstudio-js` as a submodule in order to support generating
  the Python API interface classes from the JSON schema definitions exported by `lmstudio-js`.

## Questions

If you have any other questions, feel free to join the [LM Studio Discord server](https://discord.gg/pwQWNhmQTY) and ask in the `#dev-chat` channel.

## Is the LM Studio team hiring?

Yes, yes we are. Please see our careers page: https://lmstudio.ai/careers.

Thank you for your contributions!
