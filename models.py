import math


class peer:
    def __init__(self, name, address, last_handshake, transfer):
        self.name = name
        self.address = address
        self.last_handshake = last_handshake
        self.transfer = round(transfer, 2)

    def __str__(self):
        s = f"{self.name}\n{self.address}\n{self.last_handshake}\n{self.transfer}"
        return s

    def increaseTransfer(self, transfer):
        self.transfer += transfer
        self.transfer = round(self.transfer, 2)