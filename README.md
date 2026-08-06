# A Python Library for Roth's TouchlineSL System

<a href="https://github.com/jnsgruk/pytouchlinesl/actions/workflows/test.yaml"><img src="https://github.com/jnsgruk/pytouchlinesl/actions/workflows/test.yaml/badge.svg"></a>
<a href="https://github.com/jnsgruk/pytouchlinesl/actions/workflows/publish.yaml"><img src="https://github.com/jnsgruk/pytouchlinesl/actions/workflows/publish.yaml/badge.svg"></a>
<a href="https://pypi.org/project/pytouchlinesl/"><img src="https://img.shields.io/pypi/v/pytouchlinesl"></a>

Roth TouchlineSL is a control system for underfloor heating, cooling and radiator control. They
have a public API which is documented on [their
website](https://api-documentation.roth-touchlinesl.com/).

This project provides a Python client for interacting with the API, and controlling heating
systems. It does not have complete coverage of the API, and currently provides the facility to:

- Authenticate with a https://roth-touchlinesl.com account
- List modules associated with an account
- Get details of individual zones
- Get details of global heating schedules
- Set a constant target temperature for a zone
- Assign a zone to a specific global schedule

The library was designed primarily to support the development of a [Home
Assistant](https://home-assistant.io/) integration.

## Design

Roth's API design makes operations on individual zones or schedules quite difficult. Only one
endpoint is provided for fetching the configuration of zones, and it's the same endpoint that
returns data for _all_ zones attached to a module.

As a result, this client implements some basic caching. Each time the modules endpoint is queried,
the result is cached for 30 seconds. Any POST requests made (setting temperatures, assigning zones
to schedules) will invalidate the cache, and all GET methods have a `refresh` argument that can be
used to force a refresh of the underlying data.

## Installation

The package can be installed from PyPi as usual:

```bash
pip install pytouchlinesl
```

## Example Usage

```python
import asyncio
import os

from pytouchlinesl import TouchlineSL


async def touchlinesl_example():
    tsl = TouchlineSL(
        username=os.getenv("TOUCHLINESL_LOGIN"),
        password=os.getenv("TOUCHLINESL_PASSWORD"),
    )

    # Fetch a list of modules associated with the account
    modules = await tsl.modules()
    module = await tsl.module(module_id=modules[0].id)

    # Fetch a zone by name, set a constant target temperature of 17.0
    utility = await module.zone_by_name("Utility Room")
    await utility.set_temperature(17.0)

    # Fetch a zone by ID, assign it to a global schedule named "Living Spaces"
    kitchen = await module.zone(2411)
    living_spaces = await module.schedule_by_name("Living Spaces")
    await kitchen.set_schedule(living_spaces.id)


if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.run(touchlinesl_example())
```

## Contributing / Hacking

Contributions in either code or documentation are welcome. The set of features is limited at the
moment, but I'm happy to expand as the need arises.

Commit messages and PR titles should be formatted using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

The project does not have many dependencies; just `asyncio` and `pytest`/`pytest-asyncio` for
testing.

Dependencies are managed using [`uv`](https://github.com/astral-sh/uv). You can get started like
so:

```bash
# Clone the repository
git clone https://github.com/jnsgruk/pytouchlinesl
cd pytouchlinesl

# Run the tests
uv run pytest
# Lint the code
uv run ruff check --fix
# Format the code
uv run ruff format
```

If you'd rather use standard Python tooling, you can do so:

```python
# Clone the repository
git clone https://github.com/jnsgruk/pytouchlinesl
cd pytouchlinesl

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dev/project dependencies
pip install -e '.[dev]'

# Run the tests
pytest -s
# Lint the code
ruff check --fix
# Format the code
ruff format
```

## Releasing

Once all the changes have been merged into `main` for a release, use the
[`.github/tag-release`](./.github/tag-release.sh) script to create a version bump commit in the
right format, create, **and push** the tag ready for release.

This could be automated with Github Actions - but commit signing gets a little complicated, so for
now it's just a script that can be run by maintainers.
