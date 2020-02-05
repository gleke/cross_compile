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
import logging
from pathlib import Path

import docker

from ros_cross_compile.platform import Platform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Rosdep Gatherer')


def gather_rosdep_dependencies(platform: Platform, workspace: Path, docker_dir: Path) -> Path:
    docker_client = docker.from_env()
    base = platform.native_base_image
    logger.info('Fetching base image for installing rosdep')
    docker_client.images.pull(base)

    output_tag = 'rcc/rosdep:{arch}-{os_name}-{os_distro}-{ros_version}'.format(
        arch=platform.arch,
        os_name=platform.os_name,
        os_distro=platform.os_distro,
        ros_version=platform.ros_version,
    )

    logger.info('Building rosdep gatherer "{}"'.format(output_tag))
    docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')
    log_generator = docker_api.build(
        path=docker_dir,
        dockerfile='rosdep.Dockerfile',
        tag=output_tag,
        buildargs={
            'BASE_IMAGE': base,
            'ROS_VERSION': platform.ros_version,
        },
        quiet=False,
        nocache=False,
        decode=True,
    )
