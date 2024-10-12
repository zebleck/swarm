# Standard library imports
import copy
import json
from collections import defaultdict
from typing import List, Callable, Union, Dict, Any, Optional
import os
from anthropic import AnthropicVertex
from dotenv import load_dotenv
import logging

load_dotenv()

# Package/library imports
from openai import AzureOpenAI
import google.generativeai as genai


# Local imports
from .util import (
    function_to_json,
    debug_print,
    merge_chunk,
    openai_to_anthropic_function,
    openai_to_anthropic_message,
)
from .types import (
    Agent,
    AgentFunction,
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
    Function,
    Response,
    Result,
)

__CTX_VARS_NAME__ = "context_variables"


class Swarm:
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-05-01-preview",
        )
        # Initialize Anthropic client
        self.anthropic_client = AnthropicVertex(
            region=os.getenv("LOCATION"), project_id=os.getenv("PROJECT_ID")
        )
        self.openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.anthropic_deployment_name = os.getenv(
            "ANTHROPIC_MODEL_NAME"
        )  # e.g., 'claude-v1'

    def get_chat_completion(
        self,
        agent: Agent,
        history: List,
        context_variables: dict,
        model_override: str,
        stream: bool,
        debug: bool,
    ) -> Union[ChatCompletionMessage, Any]:
        context_variables = defaultdict(str, context_variables)
        instructions = (
            agent.instructions(context_variables)
            if callable(agent.instructions)
            else agent.instructions
        )
        system_message = {"role": "system", "content": instructions}
        messages = [system_message] + history
        debug_print(debug, "Getting chat completion for...:", messages)

        if agent.provider.lower() == "openai":
            tools = [function_to_json(f) for f in agent.functions]
            # Hide context_variables from model
            for tool in tools:
                params = tool["function"]["parameters"]
                params.pop(__CTX_VARS_NAME__, None)
                if __CTX_VARS_NAME__ in params.get("required", []):
                    params["required"].remove(__CTX_VARS_NAME__)

            create_params = {
                "model": model_override or agent.model,
                "messages": messages,
                "tools": tools or None,
                "tool_choice": agent.tool_choice,
                "stream": stream,
            }

            if tools:
                create_params["parallel_tool_calls"] = agent.parallel_tool_calls

            logging.warning(
                f"Creating OpenAI chat completion with params: {create_params}"
            )

            return self.openai_client.chat.completions.create(**create_params)

        elif agent.provider.lower() == "anthropic":
            # Convert OpenAI messages to Anthropic format if necessary
            anthropic_system_message = instructions
            anthropic_messages = [openai_to_anthropic_message(m) for m in messages]
            # Ensure the last message's role is 'user'
            anthropic_messages[-1]["role"] = "user"

            # Convert functions to Anthropic-compatible schema
            tools = [
                openai_to_anthropic_function(function_to_json(f))
                for f in agent.functions
            ]
            tools = [t for t in tools if t is not None]

            anthropic_params = {
                "model": model_override or agent.model,
                "system": anthropic_system_message,
                "messages": anthropic_messages,
                "tools": tools or None,
                "stream": stream,
                "max_tokens": 4096,
            }

            logging.info(
                f"Creating Anthropic chat completion with params: {anthropic_params}"
            )

            return self.anthropic_client.messages.create(**anthropic_params)

        else:
            raise ValueError(f"Unsupported provider: {agent.provider}")

    def handle_function_result(self, result, debug) -> Result:
        match result:
            case Result() as result:
                return result

            case Agent() as agent:
                return Result(
                    value=json.dumps({"assistant": agent.name}),
                    agent=agent,
                )
            case _:
                try:
                    return Result(value=str(result))
                except Exception as e:
                    error_message = f"Failed to cast response to string: {result}. Make sure agent functions return a string or Result object. Error: {str(e)}"
                    debug_print(debug, error_message)
                    raise TypeError(error_message)

    def handle_tool_calls(
        self,
        tool_calls: List[Union[ChatCompletionMessageToolCall, Dict]],
        functions: List[AgentFunction],
        context_variables: dict,
        debug: bool,
    ) -> Response:
        function_map = {f.__name__: f for f in functions}
        partial_response = Response(messages=[], agent=None, context_variables={})
        logging.info(f"Handling tool calls: {tool_calls}")

        for tool_call in tool_calls:
            # Handle both object and dictionary formats
            if isinstance(tool_call, dict):
                name = tool_call["function"]["name"]
                tool_call_id = tool_call["id"]
                arguments = tool_call["function"]["arguments"]
            else:
                name = tool_call.function.name
                tool_call_id = tool_call.id
                arguments = tool_call.function.arguments

            # Handle missing tool case, skip to next tool
            if name not in function_map:
                debug_print(debug, f"Tool {name} not found in function map.")
                partial_response.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "tool_name": name,
                        "content": f"Error: Tool {name} not found.",
                    }
                )
                continue

            try:
                args = json.loads(arguments)
            except json.JSONDecodeError as e:
                error_message = f"Error decoding JSON for function {name}: {str(e)}"
                logging.error(tool_call)
                logging.error(arguments)
                logging.error(error_message)
                debug_print(debug, error_message)
                partial_response.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "tool_name": name,
                        "content": f"Error: Invalid function arguments. {error_message}",
                    }
                )
                continue

            debug_print(debug, f"Processing tool call: {name} with arguments {args}")

            func = function_map[name]
            # Pass context_variables to agent functions
            if __CTX_VARS_NAME__ in func.__code__.co_varnames:
                args[__CTX_VARS_NAME__] = context_variables

            try:
                raw_result = function_map[name](**args)
            except Exception as e:
                error_message = f"Error executing function {name}: {str(e)}"
                logging.error(error_message)
                debug_print(debug, error_message)
                partial_response.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "tool_name": name,
                        "content": f"Error: Function execution failed. {error_message}",
                    }
                )
                continue

            result: Result = self.handle_function_result(raw_result, debug)
            partial_response.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "tool_name": name,
                    "content": result.value,
                }
            )
            partial_response.context_variables.update(result.context_variables)
            if result.agent:
                partial_response.agent = result.agent

        return partial_response

    def run_and_stream(
        self,
        agent: Agent,
        messages: List,
        context_variables: dict = {},
        model_override: str = None,
        debug: bool = False,
        max_turns: int = float("inf"),
        execute_tools: bool = True,
    ):
        pass
        """
        # Streaming implementation remains similar,
        # Ensure provider-specific streaming is handled appropriately.
        """

    def run(
        self,
        agent: Agent,
        messages: List,
        context_variables: dict = {},
        model_override: str = None,
        stream: bool = False,
        debug: bool = False,
        max_turns: int = float("inf"),
        execute_tools: bool = True,
    ) -> Response:
        if stream:
            return self.run_and_stream(
                agent=agent,
                messages=messages,
                context_variables=context_variables,
                model_override=model_override,
                debug=debug,
                max_turns=max_turns,
                execute_tools=execute_tools,
            )
        active_agent = agent
        context_variables = copy.deepcopy(context_variables)
        history = copy.deepcopy(messages)
        init_len = len(messages)

        while len(history) - init_len < max_turns and active_agent:
            logging.info(f"Starting turn with agent: {active_agent.name}")

            # Get completion with current history and agent
            completion = self.get_chat_completion(
                agent=active_agent,
                history=history,
                context_variables=context_variables,
                model_override=model_override,
                stream=stream,
                debug=debug,
            )
            logging.info(f"Received completion: {completion}")

            if active_agent.provider.lower() == "openai":
                message = completion.choices[0].message
                debug_print(debug, "Received completion:", message)
                message_dict = json.loads(message.model_dump_json())
                message_dict["sender"] = active_agent.name
                print("message_dict:", message_dict)
                history.append(message_dict)

            elif active_agent.provider.lower() == "anthropic":
                message_content = next(
                    (
                        block.text
                        for block in completion.content
                        if block.type == "text"
                    ),
                    "",
                )
                tool_calls = []
                for block in completion.content:
                    if block.type == "tool_use":
                        tool_calls.append(
                            {
                                "id": block.id,
                                "type": "function",
                                "function": {
                                    "name": block.name,
                                    "arguments": json.dumps(block.input),
                                },
                            }
                        )

                message_dict = {
                    "role": "assistant",
                    "content": message_content,
                    "sender": active_agent.name,
                    "tool_calls": tool_calls if tool_calls else None,
                }
                debug_print(debug, "Received completion:", message_dict)
                history.append(message_dict)

            else:
                raise ValueError(f"Unsupported provider: {active_agent.provider}")

            print("message:", message_dict)

            if not message_dict["tool_calls"] or not execute_tools:
                debug_print(debug, "Ending turn.")
                break

            # Handle function calls, updating context_variables, and switching agents
            tool_calls = message_dict["tool_calls"]

            partial_response = self.handle_tool_calls(
                tool_calls, active_agent.functions, context_variables, debug
            )
            history.extend(partial_response.messages)
            context_variables.update(partial_response.context_variables)
            if partial_response.agent:
                active_agent = partial_response.agent

        logging.info("Finished run method")
        return Response(
            messages=history[init_len:],
            agent=active_agent,
            context_variables=context_variables,
        )
