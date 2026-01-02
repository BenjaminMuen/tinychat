import shlex

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any, Dict, List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.completion import WordCompleter

@dataclass
class Command:
    name: str
    func: Callable[..., Any]
    description: str

class TerminalState(Enum):
    STOPPED = 0
    RUNNING = 1

class Terminal:
    def __init__(self, prompt: str = "> ", intro: str = "Hello There! Type 'help' or 'exit'."):
        self.prompt = prompt
        self.intro = intro

        self._state = TerminalState.STOPPED
        
        self._registry: Dict[str, Command] = {}
        self._handle_exit: Optional[Callable] = None

        self._register_builtins()

    def _register_builtins(self):
        self._register_command(self._help, name="help", description="Show available commands")
        self._register_command(self._stop, name="exit", description="Exit the application")
        self._register_command(self._stop, name="quit", description="Exit the application")
    
    def _register_command(self, func: Callable, name: str, description: str = ""):
        self._registry[name] = Command(name, func, description)

    def command(self, name: str = None, description: str = ""):
        def decorator(func: Callable) -> Callable:
            cmd_name = name if name else func.__name__
            self._register_command(func, cmd_name, description)
            return func
        return decorator

    def on_exit(self):
        def decorator(func: Callable) -> Callable:
            self._handle_exit = func
            return func
        return decorator
    
    def _help(self):
        print("\nAvailable commands:")
        for name, cmd in sorted(self._registry.items()):
            print(f"  {name:<15} : {cmd.description}")
        print()

    def _stop(self):
        if self._state == TerminalState.STOPPED:
            print("Terminal is already stopped.")
            return
        
        self._state = TerminalState.STOPPED

        if self._handle_exit is not None:
            try:
                self._handle_exit()
            except Exception as e:
                print(f"Error executing exit handler: {e}")

    def _execute(self, name: str, args: List[str]):
        cmd = self._registry.get(name)

        if cmd is None:
            print(f"Unknown command: '{name}'.")
            return
        
        try:
            cmd.func(*args)
        except TypeError as e:
            print(f"Argument Error executing '{name}': {e}")
        except Exception as e:
            print(f"Error executing '{name}': {e}")

    def run(self):
        if self._state == TerminalState.RUNNING:
            print("Terminal is already running.")
            return
        
        self._state = TerminalState.RUNNING

        print(f"\n{self.intro}")

        completer = WordCompleter(list(self._registry.keys()), ignore_case=True)
        session = PromptSession(completer=completer)

        with patch_stdout():
            while self._state == TerminalState.RUNNING:
                try:
                    text = session.prompt(self.prompt).strip()

                    if text is None:
                        continue
                    
                    parts = shlex.split(text)

                    self._execute(parts[0].lower(), parts[1:])
                except KeyboardInterrupt:
                    self._stop()
                    break
                except EOFError:
                    self._stop()
                    break
                except ValueError:
                    print("Syntax Error: Check your quotes.")
                except Exception as e:
                    print(f"Unexpected Error: {e}")