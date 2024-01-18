BEEG: A Configurable Multi-Agent LLM Framework (Work in progress)

Overview

BEEG is an innovative, open-source framework designed for the development and deployment of multi-agent Large Language Models (LLMs). Emphasizing flexibility, scalability, and user accessibility, BEEG stands at the forefront of democratizing AI by enabling users from diverse backgrounds to build, modify, and enhance AI-driven applications. Our approach revolves around a configuration-based system, where key components like agents, tools, tasks, and crew settings are defined in JSON format, fostering a community-driven environment for AI development.

Features

Configuration-Driven Design

Dynamic Configuration: Central to BEEG is the ability to define and modify the behavior of agents and system components dynamically using JSON configuration files. This design allows for on-the-fly adjustments and scalability without the need to alter the core codebase.

ConfigLoader Module: At the heart of our configuration system is configloader.py, a versatile module responsible for loading, merging, and managing configurations from various sources, including default and user-contributed configurations.

Modular and Scalable Architecture

Structured Project Directory: BEEG's architecture is carefully structured to ensure clear organization and maintainability. The directory includes separate modules for agents, tools, tasks, utilities, and configuration files, ensuring a clean separation of concerns.

User-Centric Configurations: The configuration files for agents, tools, tasks, and crews are crafted with user-friendliness in mind, making it easy for users to add new components or modify existing ones.

Enhanced ConfigLoader Functionalities

Nested Directory Support: Recognizing the complexity of real-world applications, our configloader.py supports loading configurations from nested folder structures, providing flexibility in organizing configuration files.

Conflict Resolution and Prioritization: The ConfigLoader is equipped with mechanisms for resolving conflicts between configuration files and prioritizing certain configurations over others, giving users control over the system's behavior.

Verbose Output for Debugging: A verbose output option is included in the ConfigLoader, offering detailed insights during the configuration loading process, aiding in debugging and system analysis.

BEEG/
│
├── configloader/             # Module for configuration loading
│   ├── __init__.py
│   └── configloader.py
│
├── configs/                  # Root folder for all configurations
│   ├── default/              # Default configuration files
│   │   ├── agents.json
│   │   ├── tools.json
│   │   ├── tasks.json
│   │   └── crew.json
│   └── custom/               # Folder for custom/user-provided configurations
│
├── agents/                   # Folder for agent-related modules
│   └── ...                   # Other files/modules related to agents
│
├── tools/                    # Folder for tool-related modules
│   └── ...                   # Other files/modules related to tools
│
├── tasks/                    # Folder for task-related modules
│   └── ...                   # Other files/modules related to tasks
│
├── utils/                    # Utility modules
│   └── ...                   # Other utility files/modules
│
├── main.py                   # Main entry point of the application
├── requirements.txt          # Required Python packages
└── README.md                 # Project documentation
