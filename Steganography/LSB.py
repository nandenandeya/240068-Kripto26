import argparse, os, random, struct
import numpy as np
from PIL import Image

MAGIC = b"STG1"


def _bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def _bytes(bits: np.ndarray) -> bytes:
    return np.packbits(bits).tobytes()


def _order(total: int, start: int, key):
    """Urutan index byte yang dipakai setelah header (sequential / acak)."""
    idx = list(range(start, total))
    if key:
        random.Random(key).shuffle(idx)
    return idx


def encode(cover, out, text=None, file=None, key=None):
    img = Image.open(cover).convert("RGB")
    flat = np.array(img, dtype=np.uint8).flatten()

    if file:
        name = os.path.basename(file).encode()
        body = open(file, "rb").read()
        kind = 1
    else:
        name, body, kind = b"", text.encode(), 0

    payload = struct.pack(">BB", kind, len(name)) + name + body
    # header: magic + panjang payload (selalu disimpan sekuensial)
    header = MAGIC + struct.pack(">I", len(payload))
    hbits, pbits = _bits(header), _bits(payload)

    if len(hbits) + len(pbits) > flat.size:
        raise ValueError(f"Pesan terlalu besar. Kapasitas: {(flat.size - len(hbits)) // 8} byte")

    flat[:len(hbits)] = (flat[:len(hbits)] & 0xFE) | hbits
    pos = np.array(_order(flat.size, len(hbits), key)[:len(pbits)])
    flat[pos] = (flat[pos] & 0xFE) | pbits

    Image.fromarray(flat.reshape(np.array(img).shape)).save(out, "PNG")
    print(f"[OK] Stego-image disimpan: {out} ({len(payload)} byte disisipkan)")


def decode(stego, key=None, outdir="."):
    flat = np.array(Image.open(stego).convert("RGB"), dtype=np.uint8).flatten()

    hlen = 8 * 8  # 4 byte magic + 4 byte panjang
    header = _bytes(flat[:hlen] & 1)
    if header[:4] != MAGIC:
        raise ValueError("Tidak ditemukan pesan tersembunyi.")
    plen = struct.unpack(">I", header[4:])[0]

    pos = np.array(_order(flat.size, hlen, key)[:plen * 8])
    payload = _bytes(flat[pos] & 1)

    kind, nlen = struct.unpack(">BB", payload[:2])
    name, body = payload[2:2 + nlen], payload[2 + nlen:]
    if kind == 0:
        print("[OK] Pesan teks:", body.decode(errors="replace"))
    else:
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "extracted_" + name.decode())
        open(path, "wb").write(body)
        print(f"[OK] File diekstrak: {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Steganografi LSB")
    p.add_argument("mode", choices=["encode", "decode"])
    p.add_argument("-c", "--cover")
    p.add_argument("-s", "--stego")
    p.add_argument("-t", "--text")
    p.add_argument("-f", "--file")
    p.add_argument("-o", "--out", default=None)
    p.add_argument("-k", "--key", default=None)
    a = p.parse_args()

    if a.mode == "encode":
        if not a.cover or not (a.text or a.file):
            p.error("encode butuh -c dan (-t atau -f)")
        encode(a.cover, a.out or "stego.png", a.text, a.file, a.key)
    else:
        if not a.stego:
            p.error("decode butuh -s")
        decode(a.stego, a.key, a.out or ".")