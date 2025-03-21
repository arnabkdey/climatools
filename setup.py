from setuptools import setup, find_packages

setup(
    name="climatools",
    version="0.1.0",
    author="Arnab K. Dey",
    author_email="arnabxdey@gmail.com",
    description="Tools for downloading, extracting, and processing climate data",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/arnabkdey/climatools",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "earthengine-api",
        "numpy",
        "pandas"
    ],
)