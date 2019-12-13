import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wikiservice",
    version="0.1.1",
    author="Leonid Lunin",
    author_email="lunin.leonid@gmail.com",
    description="Lightweight library to work with MediaWiki-API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lrlunin/wikiservice",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests>=2.20'
    ],
    python_requires='>=3.6'
)
