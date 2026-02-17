This file is about 400 lines, always read all of it!
# Serendipity Documentation

SERENDIPITY is an app built upon the Valyrian Spellbook framework. 
SERENDIPITY is a chatbot similar to chatGPT.


## HTTP GET Endpoints
GetConversations - Retrieves all conversations
GetConversation - Retrieves a specific conversation by ID
GetFullPrompt - Gets the full prompt of a conversation
GetModels - Retrieves all available models
GetAgents - Retrieves all agents
GetAgent - Retrieves a specific agent by name
GetFolders - Gets all folders for an agent
GetTodo - Gets the todo list for an agent
GetWishlist - Gets the wishlist for an agent
GetVariables - Gets variables for an agent
GetWorkspace - Gets the workspace for an agent
GetWorkflows - Gets all workflows of an agent
GetWorkflow - Gets a specific workflow
GetWorkflowState - Gets a workflow and its state
GetAvailableVoices - Gets all available voices

## HTTP POST Endpoints
AddMessage - Adds a message to a conversation
RunWorkflowAction - Runs a workflow action
SaveSettings - Saves settings for a conversation
MultiQuestion - Handles multiple questions with context
SmartSort - Sorts items based on specified criteria
GenerateList - Generates a list based on keywords
ArchiveConversation - Archives a conversation
DeleteConversation - Deletes a conversation
SimpleRequest - Makes a simple request with a template and placeholders
GenerateAudio - Generates audio for a message
EditConversation - Edits a conversation
CreateFolder - Creates a folder for an agent
MoveToFolder - Moves a conversation to a folder
CreateInvoice - Creates an invoice
CheckInvoice - Checks the status of an invoice
DownloadFile - Downloads a file
StageFile - Stages a file for use
RemoveStagedFile - Removes a staged file
UploadVoice - Uploads a voice file
UploadProfilePicture - Uploads a profile picture
StartWorkflow - Starts a workflow
InitializeWorkflowStep - Initializes a workflow step
SaveWorkflow - Saves a workflow
GenerateWorkflow - Generates a workflow
EditWorkflowStep - Edits a workflow step
UploadMemoryFragment - Uploads a memory fragment
SearchMemory - Searches memories
GenerateMemory - Generates a memory
UpdateKnowledgeBase - Updates the knowledge base
SummarizeConversation - Summarizes a conversation
EditAgent - Edits an agent
EditAgentRole - Edits an agent's role
EditAgentVoice - Edits an agent's voice
SaveLLMConfig - Saves LLM configuration
SaveDefaultLLM - Sets the default LLM
DeleteLLMConfig - Deletes an LLM configuration
InitializeAgentVoices - Initializes agent voices
StopGeneration - Stops the generation process
SaveComfyUIServer - Saves ComfyUI server configuration
ClearStagedFiles - Clears staged files
SplitKnowledgeGraphs - Splits knowledge graphs

## Functions in serendipity_script.py

1. `load_prompt(prompt: str, placeholders: Optional[Dict] = None) -> str` - Loads a prompt from the prompts directory
2. `name_conversation(dialog: str, model_name: str = 'self-hosted') -> str | None` - Generates a name for a conversation based on the dialog
3. `create_workflow(agent: str, name: str, instructions: str, roles: str, tools: str, model_name: str = 'self-hosted') -> dict` - Creates a workflow
4. `generate_workflow(workflow_id: str, instructions: str, flowchart: str, model_name: str = 'self-hosted')` - Generates a workflow
5. `generate_memory(dialog: str, agent: str, model_name='self-hosted')` - Generates memory from dialog
6. `get_default_settings(name: str)` - Gets default settings for a given name
7. `load_scenario(name: str, placeholders: Optional[Dict] = None, roles: Optional[list[str]] = None, enabled_tools: Optional[list[str]] = None)` - Loads a scenario from the scenarios directory
8. `get_voice_filepaths(agent_name: str, voices: list[str])` - Gets voice file paths for an agent
9. `get_available_roles(agent_name: str)` - Gets the list of roles for an agent
10. `get_available_tools(agent_name: str)` - Gets the list of tools for an agent
11. `get_tools(agent_name: str, tool_names: list[str])` - Gets the list of tools with descriptions
12. `parse_use_tool(text, agent=None)` - Parses tool usage from text
13. `get_todo(agent_name: str)` - Gets the list of todo items
14. `get_wishlist(agent_name: str)` - Gets the list of wishlist items
15. `get_variables(agent_name: str)` - Gets the list of variables with their values
16. `get_workspace(agent_name: str)` - Gets the list of all files in the workspace of the agent
17. `get_available_funds(agent_name: str)` - Gets the available funds for an agent
18. `get_available_zaps(agent_name: str)` - Gets the available zaps for an agent
19. `set_available_funds(agent_name: str, funds: int)` - Sets the available funds for an agent
20. `add_available_funds(agent_name: str, funds: int)` - Adds funds to the available funds for an agent
21. `subtract_available_funds(agent_name: str, funds: int)` - Subtracts funds from the available funds for an agent
22. `update_knowledgebase(dialog: str, agent: str, model_name: str = 'self-hosted')` - Updates the knowledge base with dialog
23. `split_knowledgegraph(graph: str, model_name='self-hosted')` - Splits knowledge graphs
24. `get_tool_basename(friendly_name: str, agent_dir: str)` - Gets the basename of a tool
25. `get_enabled_tool_descriptions(agent_name, enabled_tools=None)` - Gets the descriptions of all enabled tools for the agent
26. `load_custom_tool(tool_name, agent_dir=None, **kwargs)` - Loads a custom tool
27. `get_model_context_size(model_name: str)` - Gets the context size for a model

## Classes in serendipity_script.py

### SerendipityScript class (inherits from SpellbookScript)
- `__init__(*args, **kwargs)`
- `run()`
- `cleanup()`

### Workflow class
- `workflow_id: str` - The id of the workflow to be generated
- `flowchart: str` - The flowchart for the workflow written in mermaid syntax
- `nodeIds: list` - A list of all the node ids in the flowchart

# Valyrian Spellbook: SERENDIPITY Reference Document

## Overview
SERENDIPITY is a sophisticated chatbot application built on the Valyrian Spellbook framework. The name stands for "Solutions Enabled through Responsive Empathy, Novelty, and Dynamic Interactions Proving Intelligence and Thoughtful Yields." It provides a comprehensive platform for creating and managing AI-powered conversations with various agents, integrating with Large Language Models (LLMs), and extending functionality through tools and workflows.

## Core Architecture

### Key Components
1. **Serendipity Class** (`serendipity.py`)
   - Main class that initializes the application
   - Manages conversations and the prompt engine
   - Provides methods for creating new conversations and loading messages

2. **Conversation Engine** (`engine/conversation.py`)
   - Manages conversations between multiple participants
   - Stores messages, participants, and conversation metadata
   - Provides methods for saving/loading conversations to/from files
   - Tracks token usage and costs

3. **Prompt Engine** (`engine/prompt_engine.py`)
   - Constructs prompts for LLM inference
   - Manages context, examples, and interactions
   - Handles token limits and formatting

4. **Message System** (`engine/message.py`)
   - Represents individual messages in conversations
   - Stores metadata like sender, timestamp, and content
   - Provides methods for parsing message parts

5. **Agent System** (`agents.py`)
   - Defines different agents with specific configurations
   - Each agent has properties like profile picture, participants, temperature settings, etc.

6. **HTTP Endpoints**
   - Extensive API for managing conversations, agents, workflows, etc.
   - Implemented as individual Python files (e.g., `AddMessage.py`, `GetConversation.py`)
   - Support for both GET and POST operations

7. **Tools System** (`tools/`)
   - Extensible set of tools that agents can use
   - Includes tools for file operations, search, image generation, etc.
   - Custom tools can be created and loaded dynamically

8. **Workflow System** (`tools/workflow.py`)
   - Enables creation and execution of complex workflows
   - Supports both manual tasks and automated actions
   - Includes state management and conditional branching

### Data Storage
- Conversations stored as JSON files
- Agent configurations in the `agents` directory
- Workflows in the `workflows` directory
- Memory fragments in vector databases (Chroma/Milvus)

## Configuration

### Main Configuration File
Located at `SERENDIPITY_DIR/Serendipity.conf`, it includes settings for:
- Notification email
- Log directories
- API keys for external services (Wolfram Alpha, SerpAPI, ElevenLabs)
- Vector database configuration (Milvus)

### Agent Configuration
Agents are defined in `agents.py` with properties like:
- Agent name
- Profile picture
- Public visibility
- Participants
- Temperature settings
- Model preferences
- Memory capabilities

## Key Functionalities

### Conversation Management
- Creating new conversations
- Adding messages to conversations
- Retrieving conversation history
- Archiving/deleting conversations
- Generating conversation summaries

### Agent Interaction
- Multiple agents with different personalities
- Support for multi-participant conversations
- Role-based interactions
- Memory and knowledge base integration

### LLM Integration
- Support for various LLM providers (self-hosted, OpenAI, etc.)
- Model selection and configuration
- Temperature and other parameter control
- Token usage tracking and cost calculation

### Tool Usage
- Agents can use tools to extend their capabilities
- Tool invocation parsing from LLM responses
- Custom tool creation and management
- Tool validation and error handling

### Workflow System
- Creation and execution of complex workflows
- Support for conditional branching
- Integration with external actions
- State management across workflow steps

### Memory and Knowledge Base
- Storing and retrieving memories
- Searching the knowledge base
- Updating the knowledge base with new information
- Vector-based similarity search

### File Operations
- Reading and writing files
- Staging files for use in conversations
- Managing workspaces for agents

## Directory Structure

```
/apps/Serendipity/
├── agents/                 # Agent configurations and data
├── engine/                 # Core components (conversation, prompt, message)
│   ├── chat_engine.py
│   ├── conversation.py
│   ├── message.py
│   ├── prompt_engine.py
│   └── ...
├── prompt_templates/       # Templates for prompts
├── scenarios/              # Predefined conversation scenarios
├── scripts/                # Utility scripts
├── tools/                  # Tool implementations
│   ├── ask_hivemind.py
│   ├── generate_image.py
│   ├── workflow.py
│   └── ...
├── workflows/              # Workflow definitions
├── serendipity.py          # Main application class
├── serendipity_script.py   # Core functionality implementation
└── [HTTP Endpoints]        # Individual files for API endpoints
```

## HTTP Endpoints

### GET Endpoints
- `GetConversations` - Retrieves all conversations
- `GetConversation` - Retrieves a specific conversation
- `GetModels` - Lists available models
- `GetAgents` - Lists available agents
- `GetWorkflows` - Lists available workflows
- And many more...

### POST Endpoints
- `AddMessage` - Adds a message to a conversation
- `RunWorkflowAction` - Executes a workflow action
- `GenerateMemory` - Generates a memory from dialog
- `UpdateKnowledgeBase` - Updates the knowledge base
- And many more...

## Tools System

### Available Tools
- `ask_hivemind.py` - Queries multiple LLMs and aggregates responses
- `generate_image.py` - Creates images using various providers
- `search_memory.py` - Searches the memory/knowledge base
- `workflow.py` - Manages complex workflows
- `read_file.py`/`write_file.py` - File operations
- And many more...

### Tool Implementation
Tools follow a consistent pattern:
1. Define input schema using Pydantic models
2. Implement the tool logic in the `_run` method
3. Register the tool for use by agents

## Workflow System

### Workflow Structure
- Nodes represent tasks or actions
- Edges define the flow between nodes
- Each node can have a tool associated with it
- State is maintained across workflow execution

### Workflow Execution
1. Initialize a workflow step
2. Execute the step (manual or automated)
3. Determine the next step based on output
4. Continue until reaching an end node

## Memory and Knowledge Base

### Memory System
- Memories are stored as vector embeddings
- Retrieval based on semantic similarity
- Integration with conversation context

### Knowledge Base
- Structured information for agents
- Updated through conversations
- Searchable using vector similarity

## Integration Points

### LLM Providers
- Self-hosted models
- OpenAI (GPT models)
- Other providers (configuration available)

### External Services
- Wolfram Alpha for computations
- SerpAPI for web search
- ElevenLabs for voice generation
- Vector databases (Milvus/Chroma)

## Development Considerations

### Adding New Tools
1. Create a new tool file in the `tools` directory
2. Define the input schema using Pydantic
3. Implement the tool logic
4. Register the tool for use by agents

### Creating New Agents
1. Create agent directory structure
2. Configure agent properties (roles, tools, etc.)

### Extending Workflows
1. Define new workflow nodes
2. Implement any required actions
3. Configure the workflow flow

### MCP Client Integration (In Progress)
The MCP (Model Control Protocol) client is currently under development. It will enable:
- Connection to MCP servers
- Session initialization
- Tool invocation through the MCP protocol
- Message handling via HTTP+SSE

## Best Practices

1. **Conversation Management**
   - Always save conversations after modifications
   - Handle token limits appropriately
   - Consider memory integration for context

2. **Tool Development**
   - Validate inputs thoroughly
   - Handle errors gracefully
   - Document tool functionality clearly

3. **Workflow Design**
   - Break complex tasks into manageable steps
   - Use appropriate branching logic
   - Consider both automated and manual steps

4. **Agent Configuration**
   - Set appropriate temperature for the agent's purpose
   - Configure memory capabilities based on needs
   - Select appropriate tools for the agent's role

5. **Security Considerations**
   - Validate user inputs
   - Handle API keys securely
   - Implement appropriate access controls
