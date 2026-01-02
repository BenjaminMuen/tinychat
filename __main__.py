import argparse

from lib.udpclient import UDPClient
from lib.terminal import Terminal

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--port", "-p", type=int, default=6000, help="UDP listening port")

    args = parser.parse_args()

    client = UDPClient()

    def handle_message(data: bytes, addr: tuple):
        message = data.decode("utf-8")
        print(f"{addr[0]}:{addr[1]} -> {message}")

    client.listen(port=args.port, on_data=handle_message)

    app = Terminal()

    @app.command(description="Sends a UDP message to the specified address and port")
    def send(address: str, port: str, message: str):
        UDPClient.send(address, int(port), message)
    
    @app.on_exit()
    def exit():
        print("Bye!\n")
        client.stop()

    app.run()

if __name__ == "__main__":
    main()