class peer:
    def __init__(self, name, address, last_handshake, transfer):
        self.name = name.strip()
        self.address = address.strip()
        self.last_handshake = last_handshake.strip()
        self.transfer = transfer

    def __str__(self):
        s = f"{self.name}\n{self.address}\n{self.last_handshake}\n{round(self.transfer, 2)}"
        return s

