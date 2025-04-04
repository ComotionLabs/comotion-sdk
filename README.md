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
make html
`
## Rerunning code generator

We use OpenApi generator to generate the python.

The requirements for this are a swagger file that can be gotten from WHERE?

The latest swagger file is stored in openapi_generator/comodash_api_swagger.json

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
We have changed from asyncio to urllib3 to ensure simplicity in coding without requiring "await" and "async"

To generate an html of the api:
```
java -jar \
  ./openapi_generator/openapi-generator-cli.jar generate \
        -i ./openapi_generator/comodash_api_swagger.yaml\
        -g html \
        -o ./html/
```