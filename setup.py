import os

from glob import glob

try:
    import setuptools
except ImportError:
    print("Network Runner needs setuptools in order to build.", file=sys.stderr)
    sys.exit(1)

def get_data_files(directory):
    lst = glob(os.path.join(directory, '*'))
    files = [f for f in lst if os.path.isfile(f)]
    data_files = [('{}{}'.format(os.sep, directory), files)] if files else []
    data_files.extend([get_data_files(d) for d in lst if os.path.isdir(d)])
    return data_files

def main():

    with open("README.rst", "r") as fh:
        long_description = fh.read()

    setuptools.setup(
        name='network_runner',
        version='0.1.0',
        description='Abstracton and Python API for Ansible Networking',
        author='Ansible',
        author_email='info@ansible.com',
        url='https://github.com/ansible-network/network-runner/',
        project_urls={
            'Bug Tracker': 'https://github.com/ansible-network/network-runner/issues',
            'Source Code': 'https://github.com/ansible-network/network-runner/',
        },
        license='Apache 2',
        python_requires='>=2.7',
        packages=['network_runner'],
        classifiers=[
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'Intended Audience :: System Administrators',
            'Natural Language :: English',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
        ],
        data_files=get_data_files('/etc/ansible/roles/network_runner'),
    )

if __name__ == '__main__':
    main()
