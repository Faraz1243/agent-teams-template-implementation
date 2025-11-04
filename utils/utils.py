import inspect
from functools import wraps

def log_with_config(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        params = dict(bound_args.arguments)

        # Print the config parameter if it exists
        config = params.get("config")
        print("Config parameter:", config)
        
        if config is None: 
            print("Wrapper Error ❌ No configuration provided.")
            return "Wrapper Error ❌ No configuration provided."    
        # Extract thread_id and user_id from config
        configurable = config.get("configurable", {})
        thread_id = configurable.get("thread_id", "unknown")
        user_id = configurable.get("user_id", "unknown")
        request_logs = configurable.get("request_logs", [])
        

        result = await func(*args, **kwargs)


        current_log_entry = {
            "tool": func.__name__,
            "input": {k: v for k, v in params.items() if k != "config"},
            "output": str(result),
            "thread_id": str(thread_id),
            "user_id": str(user_id)
        }

        request_logs.append(current_log_entry)
        
        return result
    return async_wrapper