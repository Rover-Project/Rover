"""
setup.py – empacotamento do plugin pca9685 para o projeto Rover.
"""
from setuptools import setup, find_packages

setup(
    name="rover-pca9685",
    version="1.0.0",
    description="Plugin PCA9685 próprio para controle de servos no Rover (IC)",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "smbus2>=0.4.0",
    ],
    extras_require={
        "test": ["pytest>=7.0"],
    },
)
