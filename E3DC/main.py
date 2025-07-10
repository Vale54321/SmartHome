from e3dc import E3DC

TCP_IP = '10.0.10.2'
USERNAME = 'test@test.com'
PASS = 'MySecurePassword'
KEY = 'abc123'
CONFIG = {}

print("local connection")
e3dc_obj = E3DC(E3DC.CONNECT_LOCAL, username=USERNAME, password=PASS, ipAddress = TCP_IP, key = KEY, configuration = CONFIG)

print(e3dc_obj.poll(keepAlive=True))
print(e3dc_obj.get_pvi_data(keepAlive=True))
e3dc_obj.disconnect()