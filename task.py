from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, List
from openai import OpenAI
from app import App, create_storage

def prompt(name: str):
    with open(Path("prompts") / f"{name}") as f:
        return f.read()

@dataclass
class Task:
    storage: str
    client: OpenAI
    problem: int | None = None
    app: App = field(init=False)
    messages: List[Dict[str, str]] = field(init=False)

    def __post_init__(self):
        create_storage(self.storage)
        self.messages = [{"role": "system", "content": prompt("start.md")}]
        if self.problem is not None:
            self.messages[0]["content"] += prompt("start_specialize.md").format(id=self.problem, problem=self.app.read(self.problem))
        self.app = App(self.storage)

    def generate(self):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            tools=json.loads(prompt("tools.json")),
            tool_choice='required'
        )
        self.messages.append(completion.choices[0].message)
        return completion.choices[0].message

    def user(self, val: str):
        self.messages.append({"role": "user", "content": val})

    def system(self, val: str):
        self.messages.append({"role": "system", "content": val})

    def assistant(self, val: str):
        self.messages.append({"role": "assistant", "content": val})

    def tool(self, id: str, name: str, val: str):
        self.messages.append({"role": "tool", "tool_call_id": id, "name": name, "content": val})

    def undo(self):
        self.messages.pop()

    def do_tool(self):
        req = self.messages[-1].tool_calls[0]
        data = json.loads(req.function.arguments)
        match req.function.name:
            case "create_problem":
                id = self.app.create(data["topic"])
                self.tool(req.id, req.function.name, json.dumps({
                    "id": id,
                    "read": self.app.read(id)
                }))
            case "read_problem":
                self.tool(req.id, req.function.name, json.dumps({
                    "read": self.app.read(data["id"])
                }))
            case "edit_problem":
                self.app.edit(data["id"], data["content"])
                self.tool(req.id, req.function.name, "ok")
            case "respond":
                self.tool(req.id, req.function.name, "ok")
                self.assistant(data["message"])
