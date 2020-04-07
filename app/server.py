#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        print(data)

        decoded = data.decode().replace("\r\n", "")

        if self.login is not None:
            if decoded != "":
                if decoded == "quit":
                    self.transport.close()
                else:
                    self.send_message(False, decoded)
        else:
            if decoded.startswith("login:"):
                newlogin = decoded.replace("login:", "").replace("\r\n", "")
                login_busy = False
                for client in self.server.clients:
                    if not login_busy:
                        login_busy = newlogin == client.login
                if login_busy:
                    self.transport.write(f"Логин {newlogin} занят, попробуйте другой".encode())
                    self.transport.close()
                else:
                    self.login = newlogin
                    self.transport.write(f"Привет, {self.login}!\r\n".encode())
                    if len(self.server.history) > 0:
                        self.transport.write(f"Последние сообщения:\r\n".encode())
                        for message in self.server.history:
                            self.transport.write(f"{message}".encode())
                    self.send_message(True, f"{self.login} подключился.")
            else:
                self.transport.write("Неправильный логин\r\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Клиент вышел")
        if self.login is not None:
            self.send_message(True, f"{self.login} отключился.")

    def send_message(self, info: bool, content: str):
        message = f"{content}\r\n"
        if not info:
            message = f"{self.login}: " + message
        self.server.history.append(message)
        if len(self.server.history) > 10:
            del(self.server.history[0])
        for user in self.server.clients:
            if self.login != user.login:
                user.transport.write(message.encode())

class Server:
    clients: list
    history: list

    def __init__(self):
        self.clients = []
        self.history = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
