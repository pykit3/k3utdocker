# k3utdocker

[![Action-CI](https://github.com/pykit3/k3utdocker/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3utdocker/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3utdocker/badge/?version=stable)](https://k3utdocker.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3utdocker)](https://pypi.org/project/k3utdocker)

Docker client utilities for unit testing - manage containers, networks, and images in tests.

k3utdocker is a component of [pykit3](https://github.com/pykit3) project: a python3 toolkit set.

## Installation

```bash
pip install k3utdocker
```

## Quick Start

```python
import k3utdocker

# Get Docker client
client = k3utdocker.get_client()

# Start a container
k3utdocker.start_container(
    name='test-redis',
    image='redis:latest',
    port_bindings={6379: 6379}
)

# Check if container exists
if k3utdocker.does_container_exist('test-redis'):
    k3utdocker.stop_container('test-redis')
    k3utdocker.remove_container('test-redis')
```

## API Reference

::: k3utdocker

## License

The MIT License (MIT) - Copyright (c) 2015 Zhang Yanpo (张炎泼)
