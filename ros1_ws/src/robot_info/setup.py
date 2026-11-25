# Installs the Python package robot_info (src/robot_info) so the nodes can "import robot_info".
# Do not run this file yourself - catkin_make uses it through catkin_python_setup().
from setuptools import setup
from catkin_pkg.python_setup import generate_distutils_setup

setup_args = generate_distutils_setup(
    packages=["robot_info"],
    package_dir={"": "src"},
)

setup(**setup_args)
