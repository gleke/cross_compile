# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import getpass
from typing import NamedTuple
from typing import Optional

ToolchainDockerPair = NamedTuple('ToolchainDockerPair', [('toolchain', str), ('docker_base', str)])

# NOTE: when changing any following values, update README.md Supported Targets section
SUPPORTED_ARCHITECTURES = {
    'armhf': ToolchainDockerPair(
        toolchain='arm-linux-gnueabihf',
        docker_base='arm32v7',
    ),
    'aarch64': ToolchainDockerPair(
        toolchain='aarch64-linux-gnu',
        docker_base='arm64v8',
    )
}

SUPPORTED_ROS2_DISTROS = ['dashing', 'eloquent']
SUPPORTED_ROS_DISTROS = ['kinetic', 'melodic']

ROSDISTRO_OS_MAPPING = {
    'kinetic': {
        'ubuntu': 'xenial',
        'debian': 'jessie',
    },
    'melodic': {
        'ubuntu': 'bionic',
        'debian': 'stretch',
    },
    'dashing': {
        'ubuntu': 'bionic',
        'debian': 'stretch',
    },
    'eloquent': {
        'ubuntu': 'bionic',
        'debian': 'buster',
    },
}
# NOTE: when changing any preceding values, update README.md Supported Targets section


class Platform:
    """
    Represents the target platform for cross compiling.

    Includes:
    * Target architecture
    * Target operating system
    * Target ROS distribution
    """

    def __init__(
        self, arch: str, os_name: str, rosdistro: str, override_base_image: Optional[str]
    ):
        """Initialize platform parameters."""
        self._arch = arch
        self._rosdistro = rosdistro
        self._os_name = os_name

        try:
            self._cc_toolchain = SUPPORTED_ARCHITECTURES[arch].toolchain
        except KeyError:
            raise ValueError('Unknown target architecture "{}" specified'.format(arch))

        if self.rosdistro in SUPPORTED_ROS2_DISTROS:
            self._ros_version = 'ros2'
        elif self.rosdistro in SUPPORTED_ROS_DISTROS:
            self._ros_version = 'ros'
        else:
            raise ValueError('Unknown ROS distribution "{}" specified'.format(rosdistro))

        if self.os_name not in ROSDISTRO_OS_MAPPING[self.rosdistro]:
            raise ValueError(
                'OS "{}" not supported for ROS distro "{}"'.format(os_name, rosdistro))

        if override_base_image:
            self._docker_target_base = override_base_image
        else:
            docker_org = SUPPORTED_ARCHITECTURES[self.arch].docker_base
            self._os_distro = ROSDISTRO_OS_MAPPING[self.rosdistro][self.os_name]
            self._docker_target_base = '{}/{}:{}'.format(docker_org, self.os_name, self.os_distro)
            self._docker_native_base = '{}:{}'.format(self.os_name, self.os_distro)

    @property
    def arch(self):
        return self._arch

    @property
    def ros_distro(self):
        return self._rosdistro

    @property
    def os_name(self):
        return self._os_name

    @property
    def os_distro(self):
        return self._os_distro

    @property
    def cc_toolchain(self):
        return self._cc_toolchain

    @property
    def ros_version(self):
        return self._ros_version

    def __str__(self):
        """Return string representation of platform parameters."""
        return '-'.join((self.arch, self.os_name, self.rosdistro))

    @property
    def sysroot_image_tag(self) -> str:
        """Generate docker image name and tag."""
        return getpass.getuser() + '/' + str(self) + ':latest'

    @property
    def target_base_image(self) -> str:
        """Name of the base OS Docker image for the target architecture."""
        return self._docker_target_base

    @property
    def native_base_image(self) -> str:
        """Name of the base OS Docker image for the host platform."""
        return self._docker_native_base
