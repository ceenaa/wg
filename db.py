import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def cache_names():
    file = open("/etc/wireguard/wg0.conf", "r")
    # file = open("test.conf", "r")
    lines = file.readlines()
    file.close()
    for i in range(13, len(lines), 6):
        name = lines[i]
        name = name.split(" ")[1]
        address = lines[i + 3]
        address = address.split(" = ")[1]
        address = address.strip()
        r.hset(address, "name", name)
        r.sadd("users", name)


def cache_last_records():
    file = open("peers.txt", "r")
    file.close()
    lines = file.readlines()
    for i in range(0, len(lines), 4):
        address = lines[i + 1].strip()
        last_handshake = lines[i + 2].strip()
        transfer = float(lines[i + 3].strip())
        r.hset(address, "last_handshake", last_handshake)
        r.hset(address, "transfer", transfer)

