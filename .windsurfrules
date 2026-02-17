# Valyrian Spellbook System Documentation
The Valyrian Spellbook (formerly Bitcoin Spellbook) is an open platform developed by Valyrian Tech that provides a comprehensive framework for creating and managing Bitcoin-related applications and integrating with Large Language Models (LLMs). The platform is designed to simplify development, enhance automation, and enable users with minimal coding experience to deploy sophisticated cryptocurrency applications.
## Core Architecture
The Valyrian Spellbook is built around a modular architecture with several key components:
1. **REST API Server**: Implemented in `spellbookserver.py`, this is the central component that handles HTTP requests and provides endpoints for all Spellbook functionality.
2. **CLI Interface**: Implemented in `spellbook.py`, this provides command-line access to all Spellbook features for configuration and management.
3. **Triggers System**: A mechanism that monitors specific conditions and activates actions when those conditions are met.
4. **Actions System**: A collection of executable tasks that can be triggered manually or by triggers.
5. **Blockchain Data Access**: Components for retrieving and processing data from the Bitcoin blockchain through various explorers.
6. **LLM Integration**: Components for integrating with and managing various Large Language Models.
## Key Components
### Spellbook Server (`spellbookserver.py`)
The server component is built using the Bottle web framework and provides a RESTful API for all Spellbook functionality. Key features include:
- API endpoints for managing blockchain explorers, LLMs, triggers, and actions, Authentication system for secure API access, Endpoints for retrieving blockchain data, Support for SSL/TLS encryption, Integration with various blockchain explorers, File upload and transcription capabilities, CORS support for web applications
### CLI Interface (`spellbook.py`)
The command-line interface provides access to all Spellbook functionality through a structured command system. Key features include:
- Managing LLM configurations, Managing blockchain explorers, Retrieving blockchain data, Managing triggers and actions, Signing messages, Checking trigger status, Running actions
### Triggers System
Triggers are conditions that, when met, activate one or more actions. The base `Trigger` class is extended by various trigger types:
Trigger Types: BalanceTrigger, BlockHeightTrigger, DeadMansSwitchTrigger, HTTPRequestTriggers, ManualTrigger, ReceivedTrigger, SentTrigger, SignedMessageTrigger, TimestampTrigger, RecurringTrigger, TriggerStatusTrigger, TxConfirmationTrigger
Triggers can be configured with scripts that run when the trigger activates, providing additional flexibility.
### Actions System
Actions are tasks that can be executed when triggered. The base `Action` class is extended by various action types:
- **CommandAction**: Executes a system command
- **SpawnProcessAction**: Spawns a new process
- **RevealSecretAction**: Reveals a pre-configured secret
- **SendMailAction**: Sends an email
- **SendTransactionAction**: Sends a Bitcoin transaction
- **WebhookAction**: Sends data to a webhook
- **Twitter Actions**: Various actions for interacting with Twitter (create/delete tweets, follow/unfollow, etc.)
- **DeleteTriggerAction**: Deletes a trigger
### Blockchain Data Access
The system supports multiple blockchain explorers for retrieving data. Explorers can be configured with priorities, so if one fails, the system falls back to the next one.
### LLM Integration
The system provides integration with various Large Language Models:
- **Self-hosted models**: Through Oobabooga or vLLM servers
- **Cloud-based models**: OpenAI, Together.ai, Anthropic, Groq, DeepSeek
- **Auto-routing**: Capability to route prompts to the most suitable model
The LLM system includes:
- Model configuration management, Cost tracking, Streaming capabilities, Mixture of experts approach, Websocket integration for real-time communication
## Security Features
- API key authentication, Signature verification for API requests, Hot wallet management for secure private key storage, SSL/TLS support
## Configuration
Configuration is managed through:
- JSON files in the `json/` directory
- Configuration files in the `configuration/` directory
- Command-line interface (`spellbook.py`)
## Extensibility
The system is designed to be extensible through:
- **Custom Scripts**: Python scripts that can be executed by triggers
- **Custom Actions**: New action types can be added by extending the base Action class
- **Custom Triggers**: New trigger types can be added by extending the base Trigger class
## Example Applications
The `apps/` directory contains example applications built with the Spellbook, including:
- Payment processors, Notary services, Lottery systems, SERENDIPITY, and more
## Directory Structure
- `action/`: Action implementations
- `apps/`: Example applications
- `bips/`: Bitcoin Improvement Proposal implementations
- `configuration/`: Configuration files
- `data/`: Blockchain data access components
- `helpers/`: Utility functions
- `inputs/`: Input processing components
- `json/`: JSON data storage
- `linker/`: Linked list implementations
- `listeners/`: Blockchain event listeners
- `models/`: Model definitions
- `randomaddress/`: Random address selection utilities
- `spellbookscripts/`: Script execution framework
- `trigger/`: Trigger implementations
- `validators/`: Data validation utilities
## Conclusion
The Valyrian Spellbook provides a comprehensive platform for building Bitcoin applications and integrating with LLMs. Its modular architecture, extensive feature set, and flexible configuration options make it suitable for a wide range of use cases, from simple automation tasks to complex distributed applications.
## Notes
- When working on the SERENDIPITY app, always read the file `serendipity.md` first!
- Each app in the apps directory is a standalone repository and should be treated as such, so when commiting changes, always remember to cd into the app directory before commiting!
