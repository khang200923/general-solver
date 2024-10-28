import os
import sys
from colorama import Fore, init
from openai import OpenAI
import task


def main():
    init(autoreset=True)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    t = task.Task(sys.argv[1], client=client)
    while True:
        t.user(input(f"{Fore.CYAN}u>> "))
        finish = False
        while not finish:
            comp = t.generate()
            req = comp.tool_calls[0]
            if req.function.name == "create_problem":
                print(f"{Fore.GREEN}a>", "Creating a problem...")
            if req.function.name == "read_problem":
                print(f"{Fore.GREEN}a>", "Reading some problem...")
            if req.function.name == "edit_problem":
                print(f"{Fore.GREEN}a>", "Editing some problem...")
            t.do_tool()
            finish = t.messages[-1]["role"] == "assistant"
        print(f"{Fore.GREEN}a>>", f"{Fore.YELLOW}{t.messages[-1]["content"]}")

if __name__ == "__main__": main()
