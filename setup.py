from setuptools import find_packages, setup


def get_requirements(filepath):
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


with open("README.md") as readme:
    setup(
        name="endotech",
        version="0.0.1",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        install_requires=get_requirements("requirements.txt"),
        author="Ivan",
        author_email="ivan@bogomolov.su",
        description="A short description of your package",
        long_description=readme.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/irr123/endotech.io",
        classifiers=[],
        python_requires=">=3.6",
    )
