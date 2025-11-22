import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rover-lib",
    version="0.1.0",
    author="gutoportelaa",
    author_email="gutoportelaa@gmail.com",
    description="Uma biblioteca Python para manipulação de um Rover com Visão Computacional.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rover-Project/Rover",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Robotics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.9',
    install_requires=[
        'numpy',
        'opencv-python',
        # As bibliotecas a seguir são para a Raspberry Pi e devem ser instaladas lá
        # 'RPi.GPIO',
        # 'picamera2',
    ],
    include_package_data=True,
)
