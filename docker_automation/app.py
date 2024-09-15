import argparse

from docker import DockerClient

from selenium_standalone import SeleniumStandaloneContainerRunner

parser = argparse.ArgumentParser()

parser.add_argument("-p", "--port")
parser.add_argument("-n", "--container-name")
parser.add_argument("-P", "--path-to-daemon")

args = parser.parse_args()

print(args)

port: int = int(args.port) if args.port else None
container_name: str = str(args.container_name) if args.container_name else None
path_to_daemon: str = str(args.path_to_daemon) if args.path_to_daemon else None

client = SeleniumStandaloneContainerRunner(path_to_daemon)

if port:
    client.port = port

container = client.run_container(container_name)

driver_path = client.get_webdriver_address()
print(driver_path)
print("client._container._container.attrs")
print(client._container._container.attrs)

container_id = client._container._container.id
_container = DockerClient(path_to_daemon).containers.get(container_id)
print('_container.attrs.get("NetworkSettings").get("IPAddress")')
print(_container.attrs.get("NetworkSettings").get("IPAddress"))

print('_container.attrs')
print(_container.attrs)
# client.kill_container()
