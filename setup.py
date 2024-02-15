from setuptools import find_packages, setup

with open("./README.md", "r") as f:
    long_description = f.read()

setup(
    name= "listeningpy",
    version= "0.0.1",
    description = "A package for listening test design.",
    package_dir={"": "listeningpy"},
    packages=find_packages(where="listeningpy"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url= "https://github.com/vyhyb/listeningpy",
    author="David Jun",
    author_email="David.Jun@vut.cz",
    licence="GNU GPLv3",
    classifiers=[
        "Licence :: OSI Approved :: GNU GPLv3",
        "Programming Language :: Python :: 3.9", 
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "sounddevice",
        "soundfile", 
        "pyloudnorm",
        "mosqito",
        "numpy", 
        "pandas",
        "scipy",
        "customtkinter"
    ],
    extras_require={
    "dev": ["pytest", "twine"],
    },
    python_requires=">=3.9"
)