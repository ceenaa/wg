from datetime import datetime


class peer:
    def __init__(self, name, address, last_handshake, transfer, active):
        self.name = name
        self.address = address
        self.last_handshake = last_handshake
        self.transfer = round(transfer, 2)
        self.active = active

    def __str__(self):
        s = f"{self.name}\n{self.address}\n{self.last_handshake}\n{self.transfer}\n{self.active}\n"
        return s

    def increaseTransfer(self, transfer):
        self.transfer += transfer
        self.transfer = round(self.transfer, 2)
