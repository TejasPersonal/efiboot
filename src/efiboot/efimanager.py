import os
import subprocess
import tempfile

from . import disk, process


def set_boot_entry_active(index: str, state: bool = True):
    cmd = ["efibootmgr", "--quiet", "--bootnum", index]
    if state:
        cmd.append("--active")
    else:
        cmd.append("--inactive")
    process.run(*cmd)


def set_boot_order(order: list[str]):
    """
    order: a list of hex strings containing indexes of boot entries
    in order,
    the first one boots automatically after restarts if next boot
    index isn't set
    """
    process.run("efibootmgr", "--quiet", "--bootorder", ",".join(order))


def set_next_boot(index: str):
    """
    index: hex string
    sets a boot entry to boot after restart once
    """
    process.run("efibootmgr", "--quiet", "--bootnext", index)


def delete_next_boot():
    """
    undoes set_next_boot
    """
    process.run("efibootmgr", "--quiet", "--delete-bootnext")


def delete_boot_entry(index: str):
    process.run("efibootmgr", "--quiet", "--bootnum", index, "--delete-bootnum")


def create_boot_entry(
    partition_path: str, description: str, loader_path: str, loader_parameters: bytes
):
    """
    description also known as label
    loader path must be relative to partition
    """
    disk_path = disk.get_disk_path_from_partition_path(partition_path)
    partition_number = disk.get_partition_number_from_path(partition_path)

    with tempfile.TemporaryDirectory() as temp:
        with disk.mount(partition_path, temp):
            mounted_loader_path = f"{temp}{loader_path.replace('\\', '/')}"

            if not os.path.exists(mounted_loader_path):
                raise FileNotFoundError(
                    2, f"No such file relative to {partition_path}", loader_path
                )

    subprocess.run(
        [
            "efibootmgr",
            "--quiet",
            "--create",
            "--disk",
            disk_path,
            "--part",
            str(partition_number),
            "--label",
            description,
            "--loader",
            loader_path,
            "--append-binary-args",
            "-",
        ],
        input=loader_parameters,
        check=True,
        capture_output=True,
    )


def create_boot_entry_unicode(
    partition_path: str, description: str, loader_path: str, loader_parameters: str
):
    """
    description also known as label
    loader path must be relative to partition

    in linux loader_parameters are kernel parameters which are seprated by space
    """
    disk_path = disk.get_disk_path_from_partition_path(partition_path)
    partition_number = disk.get_partition_number_from_path(partition_path)

    with tempfile.TemporaryDirectory() as temp:
        with disk.mount(partition_path, temp):
            mounted_loader_path = f"{temp}{loader_path.replace('\\', '/')}"

            if not os.path.exists(mounted_loader_path):
                raise FileNotFoundError(
                    2, f"No such file relative to {partition_path}", loader_path
                )

    process.run(
        "efibootmgr",
        "--quiet",
        "--create",
        "--disk",
        disk_path,
        "--part",
        str(partition_number),
        "--label",
        description,
        "--loader",
        loader_path,
        "--unicode",
        loader_parameters,
    )
