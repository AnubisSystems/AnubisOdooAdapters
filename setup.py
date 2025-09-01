from setuptools import setup, find_packages

setup(
    name="hexarch_odoo_adapters",
    version="0.0.0",
    packages=find_packages(),
    author="Jose Manuel Herrera Saenz",
    author_email="incubadoradepollos@gmail.com",
    description="Adaptadores de ODOO para anubis ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AnubisSystems/AnubisOdooAdapters.git",
    install_requires=[
        "anubis_product_core @ git+https://github.com/AnubisSystems/AnubisProductCore.git"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Intended Audience :: Legal Industry",
        "Topic :: Education",
    ]
    python_requires=">=3.13.0",
)
