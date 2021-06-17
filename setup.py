import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dash-sdk",
    version="0.0.1",
    author="Tim Vieyra",
    author_email="tim@comotion.us",
    description="SDK for interacting with the Comotion Dash API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ComotionLabs/dash-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/ComotionLabs/dash-sdk/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
