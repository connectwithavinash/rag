from . import register


class PromptManager:
    def __init__(self, default_str = "extract information") -> None:
        self.prompt_registry = register.prompt_registry
        self.default_str = default_str
    
    def get_prompt(self, container_name: str):
        prompt = self.prompt_registry.get(container_name)
        if not prompt:
            prompt = self.prompt_registry.get(self.default_str)
            if not prompt:
                prompt = "Extract information"  # Final fallback
                return prompt
        return prompt


def get_prompt_manager():
    return PromptManager()