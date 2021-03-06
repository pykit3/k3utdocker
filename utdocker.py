import docker
import docker.types
import k3ut

dd = k3ut.dd

# default network config for unittest
net_config = {
    'network1': {
        'subnet': '192.168.52.0/24',
        'gateway': '192.168.52.254',
    }
}


def get_client():
    dcli = docker.DockerClient(base_url='unix://var/run/docker.sock')
    return dcli


def does_container_exist(name):

    dcli = get_client()

    try:
        dcli.api.inspect_container(name)
        return True
    except docker.context.api.errors.NotFound:
        return False


def stop_container(*names):

    dcli = get_client()
    for name in names:
        try:
            dcli.api.stop(container=name)
        except Exception as e:
            dd(repr(e), ' while trying to stop docker container: ' + repr(name))


def remove_container(*names):

    dcli = get_client()

    for name in names:
        try:
            dcli.api.kill(name)
        except Exception as e:
            dd(repr(e) + ' while killing container: ' + repr(name))

        try:
            dcli.api.remove_container(name)
        except Exception as e:
            dd(repr(e) + ' while removing container: ' + repr(name))


def create_network():

    net_name = 'network1'
    dcli = get_client()

    try:
        dcli.api.inspect_network(net_name)
        return
    except docker.context.api.errors.NotFound as e:
        dd(repr(e))

    ipam_pool = docker.types.IPAMPool(**net_config[net_name])

    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
    )

    dcli.api.create_network(net_name, driver="bridge", ipam=ipam_config)


def start_container(name, image,
                    ip=None,
                    command='',
                    port_bindings=None,
                    volume_bindings=None,
                    env=None):

    net_name = 'network1'
    dcli = get_client()

    kwargs = {}
    _config_kwargs = {}
    if env is not None:
        kwargs['environment'] = env

    if port_bindings is not None:
        kwargs['ports'] = list(port_bindings.keys())
        _config_kwargs['port_bindings'] = port_bindings

    if volume_bindings is not None:
        volumes = []
        for bind in volume_bindings:
            volumes.append(bind.split(':')[1])

        kwargs['volumes'] = volumes
        _config_kwargs['binds'] = volume_bindings

    kwargs['host_config'] = dcli.api.create_host_config(
        **_config_kwargs)

    if ip is not None:
        net_cfg = dcli.api.create_networking_config({
            net_name: dcli.api.create_endpoint_config(ipv4_address=ip,)
        })
        kwargs['networking_config'] = net_cfg

    if not does_container_exist(name):
        dcli.api.create_container(
            name=name,
            image=image,
            command=command,
            **kwargs
        )

    dcli.api.start(container=name)


def pull_image(image):

    dcli = get_client()
    rst = dcli.api.images(image)
    if len(rst) > 0:
        dd(image + ' is ready')
        dd(rst)
        return

    # 'daocloud.io/zookeeper:3.4.10' --> ('daocloud.io/zookeeper', '3.4.10')
    rst = dcli.api.pull(*image.split(':'))
    dd(rst)


def build_image(image, path):

    dcli = get_client()

    rst = dcli.images(image)
    if len(rst) > 0:
        dd(image + ' is ready')
        dd(rst)
        return

    dd('build: ' + image + ' from ' + path)

    for line in dcli.api.build(path=path,
                           nocache=True,
                           tag=image):

        dd('build ' + image + ':', line)
