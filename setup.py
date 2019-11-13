from distutils.core import setup

setup(
    name="circuit",
    description="A very simple digital circuit simulator.",
    long_description=open("README.md").read(),
    version=open("circuit/VERSION").read(),
    author="Oran Looney",
    author_email="olooney@gmail.com",
    packages=[
        "circuit",
    ],
    install_requires=[],
)
