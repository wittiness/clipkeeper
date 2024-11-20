from setuptools import setup, find_packages

setup(
    name="clipkeeper",
    version="0.1.4",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    package_data={
        "clipkeeper.web": [
            "static/css/styles.css",
            "static/js/main.js",
            "templates/index.html",
        ],
    },
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        "Flask>=2.0.0,<3.0.0",
        "Flask-SocketIO>=5.0.0,<6.0.0",
        "click>=8.0.0,<9.0.0",
        "pathlib>=1.0.1,<2.0.0",
        "Werkzeug>=2.0.0,<3.0.0",
        "Jinja2>=3.0.0,<4.0.0",
        "itsdangerous>=2.0.0,<3.0.0",
        "python-dateutil>=2.8.0,<3.0.0",
        "rich>=12.0.0",
        "colorama>=0.4.4,<1.0.0",
        "pyperclip>=1.8.2",
        "pywin32>=305",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "black>=23.0.0,<24.0.0",
            "flake8>=6.0.0,<7.0.0",
            "mypy>=1.0.0,<2.0.0",
            "isort>=5.0.0,<6.0.0",
            "Sphinx>=6.0.0,<7.0.0",
            "sphinx-rtd-theme>=1.2.0,<2.0.0",
            "build>=0.10.0,<1.0.0",
            "twine>=4.0.0,<5.0.0",
        ],
        "windows": ["pywin32>=305"],
    },
    entry_points={
        "console_scripts": [
            "clipkeeper=clipkeeper.cli:cli",
        ],
    },
)
