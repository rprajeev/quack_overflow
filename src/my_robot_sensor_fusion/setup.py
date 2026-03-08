from setuptools import find_packages, setup

package_name = 'my_robot_sensor_fusion'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rohith-rajeev',
    maintainer_email='rajeevrohith10@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "1tof_test = my_robot_sensor_fusion.test.1tof_test:main",
            "3tof_test = my_robot_sensor_fusion.test.3tof_test:main",
        ],
    },
)
