import inspect
from datetime import datetime


def debug_print(debug: bool, *args: str) -> None:
    if not debug:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = " ".join(map(str, args))
    print(f"\033[97m[\033[90m{timestamp}\033[97m]\033[90m {message}\033[0m")


def merge_fields(target, source):
    for key, value in source.items():
        if isinstance(value, str):
            target[key] += value
        elif value is not None and isinstance(value, dict):
            merge_fields(target[key], value)


def merge_chunk(final_response: dict, delta: dict) -> None:
    delta.pop("role", None)
    merge_fields(final_response, delta)

    tool_calls = delta.get("tool_calls")
    if tool_calls and len(tool_calls) > 0:
        index = tool_calls[0].pop("index")
        merge_fields(final_response["tool_calls"][index], tool_calls[0])


def function_to_json(func) -> dict:
    """
    Converts a Python function into a JSON-serializable dictionary
    that describes the function's signature, including its name,
    description, and parameters.

    Args:
        func: The function to be converted.

    Returns:
        A dictionary representing the function's signature in JSON format.
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }


def openai_to_anthropic_function(openai_function):
    """
    Convert an OpenAI function schema to Anthropic function schema format.

    Args:
        openai_function (dict): The OpenAI function schema.

    Returns:
        dict: The Anthropic function schema.
    """

    anthropic_function = {
        "name": openai_function["function"]["name"],
        "description": openai_function["function"]["description"],
        "input_schema": {
            "type": "object",
            "properties": openai_function["function"]["parameters"]["properties"],
            "required": openai_function["function"]["parameters"].get("required", []),
        },
    }
    return anthropic_function


def openai_to_anthropic_message(openai_message):
    """
    Convert an OpenAI message to Anthropic message format.

    Args:
        openai_message (dict): The OpenAI message.

    Returns:
        dict: The Anthropic message.
    """
    anthropic_message = {
        "role": "user" if openai_message["role"] in ["user", "system"] else "assistant",
        "content": openai_message["content"] or "",
    }

    # Handle tool calls
    if "tool_calls" in openai_message and openai_message["tool_calls"]:
        tool_calls = openai_message["tool_calls"]
        for tool_call in tool_calls:
            anthropic_message[
                "content"
            ] += f"\n\nFunction call: {tool_call['function']['name']}"
            if tool_call["function"]["arguments"]:
                anthropic_message[
                    "content"
                ] += f"\nArguments: {tool_call['function']['arguments']}"

    # Handle function results
    if openai_message["role"] == "tool":
        anthropic_message[
            "content"
        ] = f"Function result for {openai_message['tool_name']}: {openai_message['content']}"

    return anthropic_message
