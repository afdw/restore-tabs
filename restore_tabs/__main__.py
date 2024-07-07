import pathlib
import argparse
from structer.structer import memmap, elf
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Restore tabs from a coredump of the main Chrome process.")
parser.add_argument("core", type=pathlib.Path)
args = parser.parse_args()

core = elf.Elf(memmap(args.core))

def read_byte(x):
    return core.fetch(x, 1)[0]

def read_word(x):
    return int.from_bytes(core.fetch(x, 8), "little")

def read_string(x):
    return bytes(core.fetch(read_word(x), min(read_word(x + 8), 4096))).decode()

def read_u16string(x):
    return bytes(core.fetch(read_word(x), min(read_word(x + 8) * 2, 8192))).decode("utf-16le")

# https://source.chromium.org/chromium/chromium/src/+/main:chrome/browser/ui/tabs/tab_renderer_data.h;drc=fe91e486972e3ce15459cea8765892913e487824;l=43
def read_TabRendererData(x):
    title = read_u16string(x)
    visible_url = read_string(x + 3 * 8)
    visible_url_valid = read_byte(x + 6 * 8)
    last_commited_url = read_string(x + 18 * 8)
    last_commited_url_valid = read_byte(x + 21 * 8)
    should_display_url = read_byte(x + 33 * 8)
    incognito = read_byte(x + 34 * 8)
    if visible_url_valid != 1 or last_commited_url_valid != 1 or should_display_url != 1 or incognito not in {0, 1}:
        raise ValueError
    if visible_url != last_commited_url:
        raise ValueError
    if not visible_url.startswith("http://") and not visible_url.startswith("https://"):
        raise ValueError
    return bool(incognito), visible_url, title

def scan_all_memory():
    res = []
    for seg in tqdm(list(core.addrindex)):
        for i in range(seg.addr, seg.addr + seg.length, 8):
            try:
                read_TabRendererData(i)
                res.append(i)
            except Exception:
                pass
    return res

roots = scan_all_memory()

print()
print("Normal")
print("------")
i = 0
for x in roots:
    incognito, url, title = read_TabRendererData(x)
    if not incognito:
        i += 1
        print(f"{i}. [{title}]({url})")

print()
print("Incognito")
print("---------")
i = 0
for x in roots:
    incognito, url, title = read_TabRendererData(x)
    if incognito:
        i += 1
        print(f"{i}. [{title}]({url})")
