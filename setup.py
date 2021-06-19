import setuptools

if __name__ == "__main__":

    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

    with open("VERSION", "r", encoding="utf-8") as vfh:
        version = vfh.read()

    setuptools.setup(
        name="comotion-sdk",
        version=version,
        author="Comotion",
        author_email="tim@comotion.us",
        description="SDK for interacting with the Comotion Dash API",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/ComotionLabs/comotion-sdk",
        project_urls={
            "Bug Tracker": "https://github.com/ComotionLabs/comotion-sdk/issues"  # noqa E501
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        python_requires=">=3.6",
        install_requires=[
            'requests>=2.25.0',
            'pandas>=1.2.0'
        ]
    )
