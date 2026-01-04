from setuptools import setup, find_packages

setup(
    name="AnubisOdooAdapters",
    version="0.0.5",
    packages=find_packages(),
    author="Jose Manuel Herrera Saenz",
    author_email="incubadoradepollos@gmail.com",
    description="Adaptadores de ODOO para anubis ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AnubisSystems/AnubisOdooAdapters.git",
    install_requires=[
        "AnubisCore @ git+https://github.com/AnubisSystems/AnubisCore.git"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Intended Audience :: Legal Industry",
        "Topic :: Education",
    ],
    python_requires=">=3.13.0",
)
