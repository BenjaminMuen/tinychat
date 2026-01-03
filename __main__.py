import argparse
from typing import Tuple

from core.utils.console import Console
from core.utils.udpclient import UDPClient

from core.utils.logger import Logger, LogLevel

def main() -> None:
    parser = argparse.ArgumentParser(prog="tinychat", description="Simple network utility")
    
    parser.add_argument("--listen", "-d", action="store_true", help="Run listener without console")
    parser.add_argument("--level", "-l", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    parser.add_argument("--port", "-p", type=int, default=6000, help="UDP listening port (default: 6000)")

    args = parser.parse_args()

    # Initialize logger
    Logger.set_level(LogLevel.from_string(args.level))

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
    
    @app.command(description="Show Information about the application")
    def info():
        print("This is a simple UDP based chat application.")

    @app.on_exit()
    def exit():
        print("Bye!\n")
        client.stop()

    # Start console
    app.run()

if __name__ == "__main__":
    main()