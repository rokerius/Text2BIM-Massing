"""Adapted MyAgent from Text2BIM agents.py:198–367, plan_designer:56–134.

Copyright (c) 2024 dcy0577. MIT; see adjacent LICENSE.
Prompt substitution and role methods retain the source structure. Execution,
retry accounting and the transport are injected instead of vs/Transformers.
"""

from .utils import clean_code_for_chat_extend


class MyAgent:
    def __init__(self, llm, chat_prompt_template, tool_description, *, executor=None, max_repairs=2, role="Programmer", log=None):
        self.llm = llm
        self.chat_prompt_template = chat_prompt_template
        self.tool_description = tool_description
        self.executor = executor
        self.max_repairs = max_repairs
        self.role = role
        self.log = log or (lambda *args: None)
        self.response_counter = 0

    def generate_one(self, prompt, stop=None):
        self.llm.role = self.role
        return self.llm.generate_one(prompt, stop)

    def chat(self, task, chat_history="", *, hint_string=None):
        self.response_counter = 0
        while True:
            prompt = self.chat_prompt_template.replace("<<all_tools>>", self.tool_description)
            if hint_string:
                prompt = prompt.replace("<<floor_plan_text>>", hint_string.strip())
            if chat_history:
                self.chat_history = prompt.replace("<<chat_history>>", chat_history.strip() + "\n")
            else:
                self.chat_history = prompt.replace("<<chat_history>>", "")
            prompt = self.chat_history
            prompt = prompt.replace("<<task>>", task)
            original_result = self.generate_one(prompt, stop=["User:", "Programmer:", "Product Owner:"])
            explanations, codes = clean_code_for_chat_extend(original_result)
            for explanation in explanations:
                self.log("explanation", text=explanation)
            code = "\n\n".join(codes)
            self.log("generated_code", code=code, attempt=self.response_counter)
            if code:
                result = self.executor.execute(code)
            else:
                from ...execution import ExecutionResult
                result = ExecutionResult(False, "The response contains no executable code block")
            self.log("execution", success=result.success, error=result.error, stdout=result.stdout)
            if result.success:
                self.response_counter = 0
                return result, original_result
            self.response_counter += 1
            if self.response_counter > self.max_repairs:
                return result, original_result
            # Source's repair request assumed partial execution. The adapted
            # transaction restores both scene and variables before this retry.
            task = (
                f"Could you please fix the error by revising your code: {result.error}. "
                "The entire failed script was rolled back, including its variables. "
                "Previously successful scripts remain. Correct this script in one Python block."
            )
            chat_history += "\nProgrammer: " + original_result

    def chat_with_function_call(self, task, chat_history, available_functions, function_description):
        prompt = self.chat_prompt_template.replace("<<all_tools>>", self.tool_description)
        if chat_history:
            self.chat_history = prompt.replace("<<chat_history>>", chat_history.strip() + "\n")
        else:
            self.chat_history = prompt.replace("<<chat_history>>", "")
        prompt = self.chat_history
        prompt = prompt.replace("<<task>>", task)
        self.llm.role = self.role
        result = self.llm.generate_with_function_call(
            prompt, stop=["User:", "Programmer:", "Product Owner:"],
            available_functions=available_functions, function_description=function_description,
        )
        self.log("agent_text", role=self.role, text=result)
        return result

    def chat_check(self, code=None, issues=None, stop=None):
        prompt = self.chat_prompt_template.replace("<<all_tools>>", self.tool_description)
        if code:
            prompt = prompt.replace("<<code>>", code)
        if issues:
            prompt = prompt.replace("<<issues>>", issues)
        result = self.generate_one(prompt, stop)
        self.log("agent_text", role=self.role, text=result)
        return result


def plan_designer(query, *, llm, prompt_template):
    # From original plan_designer: insert task into Architect template, then send
    # one user-message using the already configured client and shared budgets.
    prompt = prompt_template.replace("<<task>>", query)
    previous = llm.role
    llm.role = "Architect"
    try:
        return llm.generate_one(prompt, stop=["User:"])
    finally:
        llm.role = previous
