from setuptools import setup, find_packages

setup(
    name="simple_vcs",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "svcs=simple_vcs.cli:main",
        ],
    },
    author="Kawori",
    author_email="mihailobraztsov08@gmail.com",
    description="SimpleVCS",
    python_requires=">=3.7",
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
)