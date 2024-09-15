import random
from time import sleep

import docker
import requests
from docker import DockerClient
from docker.models.containers import Container


class SeleniumStandaloneContainer:
    _container: Container

    def __init__(self, container: Container):
        self._container = container

    @property
    def container(self) -> Container:
        return self._container.client.containers.get(self.id)

    @property
    def id(self) -> str: return self._container.id

    @property
    def ip_address(self) -> str:
        return self.container.attrs["NetworkSettings"]["IPAddress"]

    @property
    def ports(self) -> list[int]:
        return [
            int(item.split("/")[0])
            for item, port in self.container.attrs["NetworkSettings"]["Ports"].items()
            if port is not None
        ]

    def kill(self):
        self.container.kill()

    @staticmethod
    def get_list_of_ports(containers: list[Container]) -> list[int]:
        return sum([SeleniumStandaloneContainer(container).ports for container in containers], [])


class SeleniumStandaloneContainerRunner:
    _client: DockerClient
    _ports = {'4444/tcp': 4444}
    _container: SeleniumStandaloneContainer

    def __init__(self, path_to_daemon=None):
        if not path_to_daemon:
            self._client = docker.from_env()
        else:
            self._client = DockerClient(path_to_daemon)

    def run_container(self, container_name: str = None):
        if self.is_port_busy():
            self.port = self.__get_random_port_number()

        self._container = SeleniumStandaloneContainer(
            self._client.containers.run(
                image="selenium/standalone-chrome",
                name=container_name,
                detach=True,
                ports=self._ports,
                auto_remove=True
            )
        )

    @property
    def _get_webdriver_address(self):
        ip_address = self._container.ip_address if self._container.ip_address != "" else "0.0.0.0"
        port = 4444

        return f"http://{ip_address}:{port}/wd/hub"

    def get_webdriver_address(self):
        self._wait_container_to_be_running()
        return self._get_webdriver_address

    def _wait_container_to_be_running(self):
        webdriver_path = self._get_webdriver_address
        while True:
            try:
                requests.get(webdriver_path[:-6])
                break
            except requests.exceptions.ConnectionError as e:
                # print(e, "-----" * 5)
                sleep(0.5)

    def kill_container(self):
        self._container.kill()

    @property
    def port(self):
        return list(self._ports.values())[0]

    @port.setter
    def port(self, _new_port: int):
        self._ports = {f"{_new_port}/tcp": _new_port}

    def is_port_busy(self) -> bool:
        return True if self.port in self._get_list_of_busy_ports() else False

    def _get_list_of_busy_ports(self) -> list[int]:
        return SeleniumStandaloneContainer.get_list_of_ports(self._client.containers.list())

    def __get_random_port_number(self) -> int:
        port = None

        while not port:
            port = random.randint(1000, 2**16)
            port = port if port not in self._get_list_of_busy_ports() else None

        return port
