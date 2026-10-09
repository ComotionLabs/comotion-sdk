# comotion-sdk

comotion-sdk is the python SDK for interacting with the Comotion APIs.  Initial support is limited to Dash, but may expand in future.


# Documentation

Documentation for this module can be found [here](https://comotionlabs.github.io/comotion-sdk/).

# Contributing

In order to contribute to this project, fork this repo and submit a pull request to this project

In order to set up a local environment, pull this repo and install.

`pipenv` is used to manage dependencies on this project. in order to use it, ensure that pipenv is installed.

The deployment depends on the pipfile, so ensure that is complete.

```
pip install --upgrade pip
pip install pipenv
```

And then enter the virtual environment for this project that will automatically ensure all dependencies are available

```
pipenv install -e .
pipenv shell
```

When using nvim with basedpyright, start the editor from inside `pipenv shell`
so the language server inherits the same Python environment. Type checking is
configured in `pyproject.toml` and only covers hand-written code under
`src/comotion/` and `tests/` (generated API clients are excluded).

## Adding modules


Ensure dependencies are also added to setup.py in the `install_requires` section.  Then run

```
pipenv install -e .
```

Ensure you understand pipenv when [installing new libraries] (https://pipenv.pypa.io/en/latest/install/#installing-packages-for-your-project).


## running tests

To run tests
```
pipenv install --deploy --dev
pipenv run test -v
```


## Building docs

Run the following from the docs directly. Ensure to watch out for warnings.
`
pipenv install --dev
pipenv shell
make html
`
## Rerunning code generator

We use OpenApi generator to generate the python.

There are two specifications, because the SDK talks to two different APIs:

| Spec | Generated package | API |
| --- | --- | --- |
| `openapi_generator/comodash_api_swagger.yaml` | `comodash_api_client_lowlevel` | Main Dash API, `https://{org}.api.comodash.io/v2` |
| `openapi_generator/comodash_dailyrun_api_swagger.yaml` | `comodash_dailyrun_api_client_lowlevel` | DailyRun endpoints on the per-organisation frontend API, `https://api.{org}.comodash.io/superset` |

They are generated independently, so regenerating one never touches the other.

The requirements for this are a swagger file that can be gotten from WHERE?

Download latest [jar of OpenAPI Generator](https://github.com/OpenAPITools/openapi-generator#13---download-jar)

```
java -jar \
  ./openapi_generator/openapi-generator-cli.jar generate \
        -i ./openapi_generator/comodash_api_swagger.yaml\
        -g python \
        --package-name comodash_api_client_lowlevel \
        --additional-properties \
            generateSourceCodeOnly=True,library=urllib3 \
        -o ./src/
```

```powershell
java -jar `
  openapi_generator/openapi-generator-cli.jar generate `
        -i openapi_generator/comodash_api_swagger.yaml `
        -g python `
        --package-name comodash_api_client_lowlevel `
        --additional-properties `
            "generateSourceCodeOnly=True,library=urllib3" `
        -o src
```

We have changed from asyncio to urllib3 to ensure simplicity in coding without requiring "await" and "async"

### Regenerating the DailyRun client

The DailyRun client is generated the same way, from its own spec and into its own
package. Note the different output directory: both generator runs would otherwise
write `src/.openapi-generator/FILES`, `src/.openapi-generator/VERSION` and
`src/.openapi-generator-ignore`, and the second run would overwrite the first
run's copies of them. Generating into a scratch directory and copying only the
package across keeps those shared files intact.

```
java -jar \
  ./openapi_generator/openapi-generator-cli.jar generate \
        -i ./openapi_generator/comodash_dailyrun_api_swagger.yaml\
        -g python \
        --package-name comodash_dailyrun_api_client_lowlevel \
        --additional-properties \
            generateSourceCodeOnly=True,library=urllib3 \
        -o ./build/dailyrun_gen/

cp -r build/dailyrun_gen/comodash_dailyrun_api_client_lowlevel src/
cp build/dailyrun_gen/comodash_dailyrun_api_client_lowlevel_README.md src/
rm -rf build
```

If you do not have a Java runtime, the generator also runs from its official
Docker image. Pin the version so the output matches the existing clients:

```
docker run --rm -v "$PWD:/local" openapitools/openapi-generator-cli:v7.12.0 generate \
        -i /local/openapi_generator/comodash_dailyrun_api_swagger.yaml \
        -g python \
        --package-name comodash_dailyrun_api_client_lowlevel \
        --additional-properties generateSourceCodeOnly=True,library=urllib3 \
        -o /local/build/dailyrun_gen/
```

After regenerating, check that the shared generator metadata is untouched:

```
git status src/.openapi-generator src/.openapi-generator-ignore
```

The hand-written `comotion.dash.DailyRun` class wraps this generated client and
holds the behaviour the specification cannot express (scope checks, treating the
`409` from `start_execution` as a normal result, the `verify` argument and the
`GetDailyRunExecutionMode` enum). It lives in `src/comotion/`, which
`src/.openapi-generator-ignore` excludes, so regenerating never discards it.

To generate an html of the api:
```
java -jar \
  ./openapi_generator/openapi-generator-cli.jar generate \
        -i ./openapi_generator/comodash_api_swagger.yaml\
        -g html \
        -o ./html/
```