import streamlit as st
from swarm import Swarm
import json
from agents import coordinator_agent
import os


def pretty_print_messages(messages):
    output = ""
    for message in messages:
        if message["role"] == "user":
            output += f"**User**: {message['content']}\n\n"
        elif message["role"] == "assistant":
            sender = message.get("sender", "Assistant")
            output += f"**{sender}**: "
            if message["content"]:
                output += f"{message['content']}\n\n"

            tool_calls = message.get("tool_calls") or []
            for tool_call in tool_calls:
                f = tool_call["function"]
                name, args = f["name"], f["arguments"]
                arg_str = json.dumps(json.loads(args)).replace(":", "=")
                output += f"*{name}*({arg_str[1:-1]})\n\n"

    return output


def main():
    os.chdir("/home/zebleck/github/Cosmos/Cosmos-FrontEnd")
    st.title("Swarm Chat Interface")

    client = Swarm()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "agent" not in st.session_state:
        st.session_state.agent = coordinator_agent

    # Display current messages
    st.markdown(pretty_print_messages(st.session_state.messages))

    # Input box for user
    user_input = st.text_input("User Input:", key="user_input")

    current_agent = st.session_state.agent
    st.write(f"Current Agent: {current_agent.name}")

    if st.button("Send"):
        if user_input:
            # Add user message to the state
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Get response from Swarm
            response = client.run(
                agent=st.session_state.agent,
                messages=st.session_state.messages,
                context_variables={},
                stream=False,
            )

            # Update messages in the state
            st.session_state.messages.extend(response.messages)
            st.session_state.agent = response.agent

            # Rerun the app to refresh the display
            st.rerun()


if __name__ == "__main__":
    main()
