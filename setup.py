import pathlib
from setuptools import setup, find_packages

# The directory containing this file
rootDir = pathlib.Path(__file__).parent

# The text of the README file
README = (rootDir / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="symphysics",
    version="0.1.0",
    description="The symphysics library for creating physics simulations using python and sympy",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rjbourne/symphysics/",
    author="Robert B., Zeph B.",
    author_email="symphysicsDev@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["sympy", "numpy", "scipy", "dill", "matplotlib"],
    python_requires='>=3.5'
)