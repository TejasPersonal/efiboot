import dataclasses
import uuid


@dataclasses.dataclass
class LoaderLocationNode:
    type: int
    sub_type: int
    location_information: bytes


class TailFileGptDrivePart:
    """
    this is the structure where last location information
    node is file followed by GPT drive partition
    """

    def __init__(self, lln: list[LoaderLocationNode]):
        if len(lln) < 2:
            raise ValueError("Structure mismatch")

        file_node = lln[-1]
        part_node = lln[-2]

        if not (
            file_node.type == 4
            and file_node.sub_type == 4
            and part_node.type == 4
            and part_node.sub_type == 1
        ):
            raise ValueError("Structure type mismatch")

        gpt = True if part_node.location_information[36] == 2 else False
        if not gpt:
            raise ValueError("Non GPT drive partition")

        self.loader_path = file_node.location_information.decode("utf-16le").rstrip(
            "\x00"
        )

        self.partition_number = int.from_bytes(
            part_node.location_information[0:4], "little"
        )
        self.partition_start = int.from_bytes(
            part_node.location_information[4:12], "little"
        )  # unit: sectors
        self.partition_size = int.from_bytes(
            part_node.location_information[12:20], "little"
        )
        self.partition_signature = part_node.location_information[20:36]  # PARTUUID
        self.partuuid = str(uuid.UUID(bytes_le=self.partition_signature))


# LATER: May be replace current logic with offset logic for efficiency
class BootEntry:
    def __init__(self, boot_entry_file_path: str) -> None:
        with open(boot_entry_file_path, "rb") as file:
            data = file.read()

        # HEX string
        self.index = boot_entry_file_path[-41:-37]

        data = data[4:]

        self.attributes = data[:4]
        self.is_active = (self.attributes[0] & 0x01) != 0
        self.is_force_reconnect = (self.attributes[0] & 0x02) != 0
        self.is_hidden = (self.attributes[0] & 0x08) != 0
        data = data[4:]

        loader_location_size = int.from_bytes(data[:2], byteorder="little")
        data = data[2:]

        i = 2
        while i <= len(data):
            if data[i - 2 : i] == b"\x00\x00":
                break
            i += 2
        else:
            raise ValueError("No UTF-16 null terminator found")

        self.description = data[: i - 2].decode("utf-16le")
        data = data[i:]

        self.loader_parameters = data[loader_location_size:]
        data = data[:loader_location_size]

        self.loader_location: list[LoaderLocationNode] = []

        while True:
            info_type = data[0]
            info_sub_type = data[1]
            if info_type == 0x7F and info_sub_type == 0xFF:
                break
            node_size = int.from_bytes(data[2:4], byteorder="little")

            self.loader_location.append(
                LoaderLocationNode(info_type, info_sub_type, data[4:node_size])
            )

            data = data[node_size:]
