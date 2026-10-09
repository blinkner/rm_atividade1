from setuptools import setup
from glob import glob

setup(
    name='rm_atividade1',
    version='0.1.0',
    packages=['rm_atividade1'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/rm_atividade1']),
        ('share/rm_atividade1', ['package.xml'])
    ] + [('share/rm_atividade1/' + d, glob(d + '/*')) for d in ['launch', 'config', 'worlds', 'rviz']],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Adriano',
    maintainer_email='maintainer@example.com',
    description='Aula 04: teleop, sensores e navegacao reativa',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'navigator = rm_atividade1.navigator:main',
            'command_gate = rm_atividade1.command_gate:main',
        ],
    },
)