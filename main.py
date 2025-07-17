#!/usr/bin/env python3

import os
from time import sleep

from websockets.sync.client import connect
from dotenv import load_dotenv

load_dotenv(".env")

PASSWD = os.getenv("PASSWD")
IP = os.getenv("IP")


counter = (hex(i) for _ in iter(int, 1) for i in range(256))


class MCX:
    def __init__(self):
        pass


def encrypt(str_, publicKeyE, publicKeyN):
    out = [str((ord(i) * publicKeyE) % publicKeyN) for i in str_]
    return ",".join(out)


def serialize(list_):
    out = bytearray()
    for item in list_:
        if len(item) < 27:
            out += (160 | len(item)).to_bytes()
        else:
            out += b"\xDA" + len(item).to_bytes(2, "big")
        out += item.encode()
    return out


def set_var(int_):
    if int_ < 128:
        return int_.to_bytes()
    else:
        return b"\xCC" + int_.to_bytes()


def set_pgm_volume(int_, ws):
    ws.send((b"\x93\x02"
             + serialize(["AUDIO_FADER"])
             + set_var(int_)
             ))


def pool(ws):
    ws.send((b"\x94\x00\x01"
             + serialize(["POOLING", ""])
             ))


def read_all(ws):
    ws.send((b"\x93\x02"
             + serialize(["READ", "ALL"])
             ))


def receive(ws):
    # print(len(ws.messages))
    try:
        return ws.recv(timeout=3)
    except TimeoutError:
        pass


def main():
    with connect(
            "ws://" + IP + "/linear",
            user_agent_header=None,
            # proxy="http://localhost:8888",
            origin=IP) as ws:

        read_all(ws)

        res = receive(ws)

        publicKeyE = int.from_bytes(res[29:31], 'big')
        publicKeyN = int.from_bytes(res[32:36], 'big')

        ws.send((b"\x94\x00\x02"
                 + serialize([
                     "AUTHENTICATION_CHECK",
                     encrypt(PASSWD, publicKeyE, publicKeyN)])
                 ))

        receive(ws)

        for i in range(1, 254, 10):
            set_pgm_volume(i, ws)
            receive(ws)
            sleep(2)

        set_pgm_volume(194, ws)

        # for i in range(1, 6):
        #     ws.send((b"\x93\x02"
        #              + serialize(["SCAN_BUTTON"])
        #              + b"\x92"
        #              + serialize([f"0x1000000{i}"])
        #              + b"\x01"
        #              ))

        #     receive(ws)
        #     sleep(2)

        # for i in range(11, 16):
        #     ws.send((b"\x93\x02"
        #              + serialize(["SCAN_BUTTON"])
        #              + b"\x92"
        #              + serialize([f"0x100000{i}"])
        #              + b"\x01"
        #              ))

        #     receive(ws)
        #     sleep(2)

        # for i in range(2):
        #     ws.send((b"\x93\x02"
        #              + serialize(["SCAN_BUTTON"])
        #              + b"\x92"
        #              + serialize([f"0x2000005"])
        #              + b"\x01"
        #              ))

        #     receive(ws)
        #     ws.send((b"\x93\x02"
        #              + serialize(["MENU_OPERATION"])
        #              + b"\x93"
        #              + serialize(["0x02040500", "0x00011005"])
        #              + b"\x01"
        #              ))

        #     print(receive(ws))
        #     sleep(2)

        # pool(ws)


if __name__ == "__main__":
    main()
