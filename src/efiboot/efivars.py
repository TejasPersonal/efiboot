import os

EFIVARS_PATH = "/sys/firmware/efi/efivars/"


def get_boot_entry_file_paths() -> list[str]:
    efivars = os.listdir(EFIVARS_PATH)
    boot_entry_file_paths: list[str] = []

    for var in efivars:
        if var.startswith("Boot") and var[8] == "-" and var[4] != "N":
            boot_entry_file_paths.append(str(EFIVARS_PATH + var))

    return boot_entry_file_paths


def get_boot_entry_file_path_from_index(index: str) -> str:
    """
    index: hex string
    """
    file_name = f"Boot{index}-8be4df61-93ca-11d2-aa0d-00e098032b8c"

    boot_entry_path = EFIVARS_PATH + file_name
    if os.path.exists(boot_entry_path):
        return str(boot_entry_path)

    raise FileNotFoundError(2, "Invalid index, no such file", boot_entry_path)


def hex4_from_bytes(i: bytes) -> str:
    return f"{int.from_bytes(i, 'little'):04x}"


def get_boot_timeout() -> int:
    """
    Seconds
    """
    timeout_file_path = EFIVARS_PATH + "Timeout-8be4df61-93ca-11d2-aa0d-00e098032b8c"

    with open(timeout_file_path, "rb") as file:
        data = file.read()

    data = data[4:]

    return int.from_bytes(data, "little")


def get_next_boot_index() -> str:
    """
    Stays even if entry was deleted but system wasn't restarted,
    if deleted next boot will essentially be the first entry of
    the boot order.
    """
    boot_next_file_path = EFIVARS_PATH + "BootNext-8be4df61-93ca-11d2-aa0d-00e098032b8c"

    with open(boot_next_file_path, "rb") as file:
        data = file.read()

    data = data[4:]

    return hex4_from_bytes(data)


def get_current_boot_index() -> str:
    boot_current_file_path = (
        EFIVARS_PATH + "BootCurrent-8be4df61-93ca-11d2-aa0d-00e098032b8c"
    )

    with open(boot_current_file_path, "rb") as file:
        data = file.read()

    data = data[4:]

    return hex4_from_bytes(data)


def get_boot_order() -> list[str]:
    """
    returns a list of hex strings containing indexes of boot entries
    in order,
    the first one boots automatically after restarts if next boot
    index isn't set
    """
    boot_order_file_path = (
        EFIVARS_PATH + "BootOrder-8be4df61-93ca-11d2-aa0d-00e098032b8c"
    )

    with open(boot_order_file_path, "rb") as file:
        data = file.read()

    data = data[4:]
    order: list[str] = []

    for i in range(2, len(data), 2):
        order.append(hex4_from_bytes(data[i - 2 : i]))

    return order
