# Tools

* `data_builder.py` Script converting .md formatted reports to .csv and .json data.

## Requirements

* python >= 3.6.0
* pip

## Usage

```bash
# Install python dependencies first
pip install -r requirements.txt

# Run script from within root directory of project
python tools/data_builder.py
```

## Tests

Tests use the [pytest](https://docs.pytest.org/) framework

### Adding tests
- For getting started with Pytest, see [official docs](https://docs.pytest.org/en/stable/getting-started.html)
- Prefix test names with `test_`
- All test names must be unique

### Running tests

- From inside of the `tools` folder, run `pytest` (this will pick up tests in all files named `test_*.py` or `*_test.py`)

### Checking test coverage report

- From inside of the `tools` folder, run `pytest --cov=. --cov-report=html`
- Run `open htmlcov/index.html` to open the interactive html coverage report
