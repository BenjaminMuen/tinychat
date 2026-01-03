import socket
import threading

from enum import Enum
from typing import Callable, Optional

from core.utils.logger import Logger

class UDPClientState(Enum):
    STOPPED = 0
    RUNNING = 1

class UDPClient:
    def __init__(self):
        self._port: int = 5000
        self._state = UDPClientState.STOPPED
        
        self._handle_data: Optional[Callable] = None
        self._socket: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None

    @classmethod
    def send(cls, ip: str, port: int, message: str):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message.encode('utf-8'), (ip, port))
        Logger.info(f"[UDPClient] Message '{message}' sent to {ip}:{port}")

    def on_data(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._handle_data = func
            return func
        return decorator

    def listen(self, port: int = 5000):
        if self._state == UDPClientState.RUNNING:
            Logger.warning(f"[UDPClient] Already listening at port {self._port}")
            return
        
        self._state = UDPClientState.RUNNING

        Logger.log("[UDPClient] Starting UDP listener...")

        self._port = port

        try:
            # Initialize UDP socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind(("0.0.0.0", port))
            self._socket.settimeout(1.0)
        except Exception as e:
            Logger.error(f"[UDPClient] Error initializing socket: {e}")
            self._state = UDPClientState.STOPPED
            return
        
        # Initialize listener thread
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

        Logger.log(f"[UDPClient] UDP listener started.")

    def stop(self):
        if self._state == UDPClientState.STOPPED:
            Logger.warning("[UDPClient] Listener is already stopped.")
            return

        self._state = UDPClientState.STOPPED

        Logger.log("[UDPClient] Stopping UDP listener...")

        # Close UDP socket
        if self._socket is not None:
            self._socket.close()
            self._socket = None

        # Stop listener thread
        if self._thread is not None:
            self._thread.join()
            self._thread = None

        Logger.log("[UDPClient] UDP listener stopped.")

    def _loop(self):
        Logger.info(f"[UDPClient] Listening at port {self._port}...")

        while self._state == UDPClientState.RUNNING:
            try:
                data, addr = self._socket.recvfrom(1024)

                if self._handle_data is not None:
                    self._handle_data(data, addr)
                else:
                    Logger.info(f"[UDPClient] Received data from {addr[0]}:{addr[1]}: {data.decode('utf-8', 'ignore')}")
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as e:
                if self._state == UDPClientState.RUNNING:
                    Logger.error(f"[UDPClient] Error receiving data: {e}")
                continue