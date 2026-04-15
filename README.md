# efiboot

A Python library for reading and managing UEFI boot entries on Linux systems.

Reads EFI variables directly from /sys/firmware/efi/efivars/, exposing the full raw data while keeping common use cases simple. Uses efibootmgr only for write operations.

> **Note:** Most operations require root privileges.

## Reading Boot Entries

### List all boot entries with details

```python
file_paths = efiboot.get_boot_entry_file_paths()

for path in file_paths:
    entry = efiboot.BootEntry(path)
    print(entry.index, entry.description, "active:", entry.is_active)
    # entry.description is also known as label or name
```

### Get a specific entry by index

```python
path = efiboot.get_boot_entry_file_path_from_index("0001")
entry = efiboot.BootEntry(path)
print(entry.description)
```

## BootEntry attributes

| Attribute | Type | Description |
|---|---|---|
| `index` | `str` | 4-character hex index (e.g. `0001`) |
| `description` | `str` | Human-readable label |
| `is_active` | `bool` | Whether the entry is enabled |
| `is_hidden` | `bool` | Whether the entry is hidden |
| `is_force_reconnect` | `bool` | Whether reconnect is forced on boot |
| `loader_location` | `list[LoaderLocationNode]` | Raw EFI device path nodes |
| `loader_parameters` | `bytes` | Raw loader arguments |

---

### Other EFI variables

```python
print(efiboot.get_boot_order())         # e.g. ['0001', '0002', '0003']
print(efiboot.get_current_boot_index()) # e.g. '0001'
print(efiboot.get_next_boot_index())    # e.g. '0002'
print(efiboot.get_boot_timeout())       # seconds, e.g. 5
```

---

## TailFileGptDrivePart

This is the class for inspecting boot entries that point to a file (e.g. a kernel image or `.efi` file) on a GPT-partitioned drive — the most common use case for efiboot.

Given a `BootEntry`, pass its `loader_location` to `TailFileGptDrivePart`. It will raise `ValueError` if the entry doesn't match this structure (e.g. network boot, non-GPT disk), so wrap it in a try/except.

```python
file_paths = efiboot.get_boot_entry_file_paths()

for path in file_paths:
    entry = efiboot.BootEntry(path)
    try:
        loader = efiboot.TailFileGptDrivePart(entry.loader_location)
        print(f"[{entry.index}] {entry.description}")
        print(f"  Loader path : {loader.loader_path}")
        print(f"  Partition   : {loader.partition_number}")
        print(f"  PARTUUID    : {loader.partuuid}")
    except ValueError:
        pass  # Entry uses a different boot mechanism, skip it
```

### Available attributes

| Attribute | Type | Description |
|---|---|---|
| `loader_path` | `str` | Path to the loader file on the partition (e.g. `\vmlinuz-linux`) |
| `partuuid` | `str` | UUID of the GPT partition |
| `partition_number` | `int` | Partition number on the disk |
| `partition_start` | `int` | Partition start offset in sectors |
| `partition_size` | `int` | Partition size in sectors |
| `partition_signature` | `bytes` | Raw 16-byte partition GUID |

---

## Managing Boot Entries

### Create a boot entry

Use `create_boot_entry_unicode` for standard Linux kernel entries (loader parameters as a string):

```python
efiboot.create_boot_entry_unicode(
    partition_path="/dev/sda1",
    description="Arch Linux",
    loader_path="\\vmlinuz-linux",
    loader_parameters="rw root=PARTUUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx initrd=\\initramfs-linux.img",
)
```

Use `create_boot_entry` when you need raw binary loader parameters:

```python
efiboot.create_boot_entry(
    partition_path="/dev/sda1",
    description="My OS",
    loader_path="\\EFI\\myos\\bootx64.efi",
    loader_parameters=bin,
)
```

Both functions will raise `FileNotFoundError` if the loader file doesn't exist on the partition.

> **Note**: loader_path accepts both / and \ path separators. Any paths embedded in loader_parameters must use \ separators.

### Delete a boot entry

```python
efiboot.delete_boot_entry("0003")
```

### Set boot order

```python
efiboot.set_boot_order(["0001", "0003", "0002"])
```

### Activate or deactivate an entry

```python
efiboot.set_boot_entry_active("0001", state=True)   # activate
efiboot.set_boot_entry_active("0001", state=False)  # deactivate
```

### One-time next boot

```python
efiboot.set_next_boot("0002")   # boot this entry once on next restart
efiboot.delete_next_boot()      # cancel the one-time override
```
