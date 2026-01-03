import argparse
from typing import Tuple

from utils.console import Console
from utils.udpclient import UDPClient

def main() -> None:
    parser = argparse.ArgumentParser(prog="tinychat", description="Simple network utility")

    parser.add_argument("--port", "-p", type=int, default=6000, help="UDP listening port")
    parser.add_argument("--listen", "-l", action="store_true", help="Run listener without console")

    args = parser.parse_args()

    # Initialize UDP client
    client = UDPClient()

    @client.on_data()
    def handle_message(data: bytes, addr: Tuple[str, int]):
        message = data.decode('utf-8', errors='ignore')
        print(f"-> Message from {addr[0]}:{addr[1]}: {message}")

    # Start listening
    client.listen(port=args.port)

    # Non-interactive mode
    if args.listen:
        try:
            input(f"Listening on UDP port {args.port}. Press any key to exit...")
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass
        finally:
            client.stop()
        
        # Exit application
        return
    
    # Interactive mode

    # Initialize console application
    app = Console()

    @app.command(description=f"Send a UDP message")
    def send(host: str, port: str, message: str):
        UDPClient.send(host, int(port), message)

    @app.on_exit()
    def exit():
        print("Bye!\n")
        client.stop()

    # Start console
    app.run()

if __name__ == "__main__":
    main()