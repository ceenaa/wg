class Peer:
    def __init__(self, name, address, last_handshake, transfer, active):
        self.name = name
        self.address = address
        self.last_handshake = last_handshake
        self.transfer = round(transfer, 2)
        self.active = active

    def __str__(self):
        s = f"{self.name}\n{self.address}\n{self.last_handshake}\n{self.transfer}\n{self.active}"
        return s

    def increase_transfer(self, transfer):
        self.transfer += transfer
        self.transfer = round(self.transfer, 2)
