# Developer Agent

This example demonstrates a Swarm containing a developer agent that can browse the file system, view, and edit files.

## Setup

1. Run the developer agent Swarm:

```shell
python3 run.py
```

## Usage

The developer agent can perform the following actions:
- List files and directories
- Read file contents
- Edit file contents
- Create new files
- Delete files

Example queries:
- "List files in the current directory"
- "Show me the contents of file.txt"
- "Edit file.txt and add a new line at the end"
- "Create a new file called new_file.py"
- "Delete temp.txt"

## Note

Be cautious when using this agent, as it has the ability to modify your file system. Always double-check before performing destructive actions.
