import contextlib
import os

from . import process


def get_disk_path_from_partition_path(partition_path: str) -> str:
    partition_name = os.path.basename(partition_path)

    sys_partition_path = "/sys/class/block/" + partition_name
    sys_disk = os.path.dirname(os.path.realpath(sys_partition_path, strict=True))
    disk_name = os.path.basename(sys_disk)

    return "/dev/" + disk_name


def get_partition_number_from_path(partition_path: str) -> int:
    partition_name = os.path.basename(partition_path)
    sys_partition_path = f"/sys/class/block/{partition_name}"

    partition_file = os.path.join(sys_partition_path, "partition")

    with open(partition_file) as file:
        return int(file.read())


@contextlib.contextmanager
def mount(partition: str, path: str):
    process.run("mount", partition, path)
    try:
        yield
    finally:
        process.run("umount", path)
