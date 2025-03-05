# A simple interface to handle multiple language models

class ModelInterface:
    def __init__(self, default_model="gpt", credentials=None):
        self.current_model = default_model
        self.credentials = credentials or {}
        self.context = []

    def send_query(self, prompt):
        # Append prompt to context
        self.context.append(prompt)
        # Dynamically route to the appropriate model handler based on the current model
        if self.current_model.lower() == "gpt":
            return self._send_query_gpt(prompt)
        elif self.current_model.lower() == "grok":
            return self._send_query_grok(prompt)
        else:
            raise ValueError("Unsupported model type.")

    def _send_query_gpt(self, prompt):
        # Simulate a GPT API call using stored credentials
        api_key = self.credentials.get("gpt")
        # Replace below with actual GPT API call logic
        return f"GPT response for '{prompt}' with api_key {api_key}"

    def _send_query_grok(self, prompt):
        # Simulate a Grok API call using stored credentials
        api_key = self.credentials.get("grok")
        # Replace below with actual Grok API call logic
        return f"Grok response for '{prompt}' with api_key {api_key}"

    def update_context(self, message):
        # Manage conversation context. Can append message or implement trimming logic.
        self.context.append(message)
        return self.context

    def switch_model(self, model_name, new_credentials=None):
        # Dynamically switch the active model and update credentials if provided
        self.current_model = model_name
        if new_credentials:
            self.credentials[model_name] = new_credentials
        return self.current_model


if __name__ == "__main__":
    # Example usage
    interface = ModelInterface(default_model="gpt", credentials={
                               "gpt": "gpt_key_123", "grok": "grok_key_456"})
    print(interface.send_query("What is AI?"))
    interface.switch_model("grok")
    print(interface.send_query("Explain artificial intelligence."))
