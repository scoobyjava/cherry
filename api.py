#!/usr/bin/env python3
# filepath: /workspaces/cherry/cherry/api.py
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SummarizationLLM:
    def execute(self, request_data):
        # Dummy summarization: returns a simple summary
        summary = "Summary: " + str(request_data.get("text", "No text provided"))
        logger.info("SummarizationLLM executed")
        # Marking output as public for saving
        return {"summary": summary, "status": "public"}

class ChatLLM:
    def execute(self, request_data):
        # Dummy chat: echoes back the message with a prefix
        message = request_data.get("message", "Hello")
        response = f"ChatLLM response: {message}"
        logger.info("ChatLLM executed")
        return {"response": response, "status": "public"}

class DefaultLLM:
    def execute(self, request_data):
        # Default behavior, simply returns the request data
        logger.info("DefaultLLM executed")
        return {"result": request_data, "status": "public"}

class AnalyticsDB:
    def save(self, data):
        # Simulate saving data to an analytics database
        logger.info("AnalyticsDB: Data saved.")
        return True

class LoggingDB:
    def save(self, data):
        # Simulate saving log data to a logging database
        logger.info("LoggingDB: Log saved.")
        return True

class DefaultDB:
    def save(self, data):
        # Default database simply logs the saved data
        logger.info("DefaultDB: Data saved.")
        return True

class APIManager:
    def __init__(self, config):
        self.config = config

    def select_llm(self, context):
        # Dynamically pick an LLM handler based on context
        if context == 'summarization':
            return SummarizationLLM()
        elif context == 'chat':
            return ChatLLM()
        else:
            return DefaultLLM()

    def select_db(self, context):
        # Dynamically pick a database connection based on context
        if context == 'analytics':
            return AnalyticsDB()
        elif context == 'logging':
            return LoggingDB()
        else:
            return DefaultDB()

    def perform_request(self, context, request_data):
        """
        Process an API request by selecting the appropriate LLM and DB.
        The result is saved only if it is marked as public.
        """
        llm = self.select_llm(context)
        db = self.select_db(context)
        # Execute the LLM request
        result = llm.execute(request_data)
        # Pass only public content to the DB to avoid saving sensitive data
        if result.get("status") == "public":
            db.save(result)
        else:
            logger.warning("Result contains non-public data; not saving to DB.")
        return result

# Public block for testing and demonstration
if __name__ == "__main__":
    manager = APIManager(config={})
    
    # Test a summarization request
    test_request = {"text": "This is a test of the summarization feature."}
    result = manager.perform_request("summarization", test_request)
    print(json.dumps(result, indent=2))
    
    # Test a chat request
    test_chat = {"message": "Hello, how are you?"}
    chat_result = manager.perform_request("chat", test_chat)
    print(json.dumps(chat_result, indent=2))
