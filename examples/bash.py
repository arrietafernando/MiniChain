from parsita import TextParsers, lit, reg, rep
from minichain import Backend, JinjaPrompt, SimplePrompt, start_chain
from typing import List

class Bash(JinjaPrompt[List[str]]):
    prompt_template = """If someone asks you to perform a task, your job is to come up with a series of bash commands that will perform the task. There is no need to put "#!/bin/bash" in your answer. Make sure to reason step by step, using this format:

Question: "copy the files in the directory named 'target' into a new directory at the same level as target called 'myNewDirectory'"

I need to take the following actions:
- List all files in the directory
- Create a new directory
- Copy the files from the first directory into the second directory
```bash
ls
mkdir myNewDirectory
cp -r target/* myNewDirectory
```

That is the format. Begin!

Question: {{question}}"""

    class BashParser(TextParsers):  # type: ignore
        result = (lit("```bash\n") >> rep(reg(r'[^\n]*\n') > str) << lit("```"))
        
    @classmethod
    def parse(cls, inp: str) -> List[str]:
        return cls.BashParser.result.parse(inp).or_die()  # type: ignore


        
def bash(inp: str, openai: Backend, bash: Backend) -> str:
    result = Bash.run(openai, dict(question=inp), name="ask")
    result = SimplePrompt.run(bash, ";".join(result.val).replace("\n", ""))
    return result.val

    
if __name__ == "__main__":
    with start_chain("bash") as backend:
        mock = backend.Mock(
            [
"""```bash
ls
```
"""])

        openai = backend.OpenAI("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")
        result = bash(
            "\"go up one directory and list the files in the directory\"",
            openai,
            backend.BashProcess()

        )
        print(result)
