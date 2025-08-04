# Pyvorg - Automated Video Organizer

## Overview

A Python-based command-line tool designed to automate the organization and enrichment of local video file collections. Pyvorg was developed to solve the tedious and repetitive process of manually organizing movie files, demonstrating a commitment to building efficient and scalable solutions for everyday problems.


## Project History

Pyvorg started as a simple Python script to solve a personal pain point: manually organizing a growing collection of local video files. Recognizing that a manual approach wasn't scalable, I iteratively developed an automated solution. The project evolved from a basic regex script to a robust command-line application that integrates with external APIs (like OMDB) to pull and enrich metadata, ensuring a consistently organized and well-documented video library.

My focus throughout development was on building a reliable and extensible system. I implemented a modular, plug-in-style architecture for data sources, which allows new features to be added without modifying the core application. The next step is to add the same pluggability for internal services. The application utilizes a Command pattern for a stable and predictable user experience, offering a transactional workflow similar to git that allows for logging and command rollbacks. This project demonstrates my commitment to workflow automation, API integration, and designing scalable software architecture to solve real-world problems.


## Key Features

- **Automated File Organization**: Scans directories and organizes video files into a user-defined folder structure (e.g., %title (%year))

- **API-Driven Data Enrichment**: Integrates with external APIs (e.g., OMDB) to pull comprehensive metadata like year, director, and genre, ensuring consistent and complete information for each video

- **Pluggable Architecture**: Designed with a modular, plug-in system that allows for easy integration of new data sources (e.g., IMDB) without modifying the core application logic

- **Reliable Workflow Management**: Utilizes a "transactional" command pattern similar to git to manage and log operations, enabling users to review and roll back changes for a reliable user experience


## Technologies & Design

- **Language**: Python

- **Libraries**: Guessit for file name parsing, requests for API calls

- **Architectural Patterns**: Implemented a Facade pattern to simplify access to core services and a Command pattern for robust command-line operations with history and rollback functionality

- **Data Management**: Utilized nested JSON structures for efficient data storage and seamless integration with external APIs

- **Unit Testing**: The codebase is supported by over 150 unit tests to ensure the reliability and correctness of core functionality, demonstrating a commitment to high-quality code.


## Future Work

**Pluggable services**: The next major architectural goal for Pyvorg is to implement a pluggable system for services, mirroring the current design for data sources. This will allow the command-line interface to dynamically discover new services and their required arguments, making the application even more extensible and maintainable without requiring core code changes.

**Robust error handling**: Having survived re-architecting, error handling needs to be revisted to provide a more reliable and seamless user experience.

## Installation

To install Pyvorg, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/pyvorg.git
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the package**:
    ```bash
    pip install .
    ```

## Usage

Pyvorg operates through a command-line interface, providing a git-like workflow for managing your video collection. Operations are first "staged" in a buffer and then "committed" to ensure user control and provide a history of changes.

### Example Workflow

Let's imagine you have a directory with a few unorganized movie files:

```
/MyVideos/
|-- alien.1979.avi
|-- back.to.the.future.1985.mkv
|-- star.wars.a.new.hope.1977.mp4
```

You can use the following commands to scan, enrich, and organize this collection:

#### 1. Scan the directory:
```bash
$ python main.py scan /MyVideos/
Scanning '/MyVideos/'
```

#### 2. View the staged operation (optional):
```Bash
$ python main.py view
Staged Operations:
- Scan for new videos in '/MyVideos/'
```

#### 3. Fetch metadata using an API:
```Bash
$ python main.py fetch GuessitAPI
Staging fetch from GuessitAPI
```

#### 4. Organize the files:
```Bash
$ python main.py organize /OrganizedVideos/ --dirname "%title (%year)"
Staging files for organization at '/OrganizedVideos/'
```

#### 5. Commit the operations to execute them:
```Bash
$ python main.py commit
Committing staged operations
```

This will execute all staged commands.

After the commands are committed, your directory structure will be transformed into an organized library:

```
/OrganizedVideos/
|-- Alien (1979)/
|   |-- alien.1979.avi
|-- Back to the Future (1985)/
|   |-- back.to.the.future.1985.mkv
|-- Star Wars A New Hope (1977)/
|   |-- star.wars.a.new.hope.1977.mp4
```

This clear, step-by-step example shows the utility of your application and demonstrates your ability to build a reliable, user-friendly, and repeatable workflow.

## Configuration

To run Pyvorg, you must create a configuration file named config.env in the root directory. This file is essential for storing user-specific settings and sensitive information, such as API keys.

A template file, config.env.template, is provided to simplify the setup. Simply copy this file to config.env and fill in the values.

```ini, TOML
# Your OMDB API key.
# A free key can be obtained from http://www.omdbapi.com/apikey.aspx
OMDB_KEY = your_api_key_here

# The default path to scan for video files.
SOURCE_PATH = /path/to/your/video/collection

# The default destination path for organized files.
DEST_PATH = /path/to/your/organized/library

# The default format string for organizing files.
# Examples:
#   %title (%year)
#   %genre/%title
DEFAULT_FORMAT_STRING = %title (%year)
```

## Contributing

Contributions are welcome! If you have suggestions, bug reports, or improvements, please create an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. The software is provided "as is" and the original authors are not liable for any damages or issues arising from its use. Remember, this is a personal project developed by an undergrad ;) - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, you can reach out to:

- **Author**: Brett DeWitt
- **Email**: bdewitt1984@gmail.com
- **GitHub**: [bdewitt84](https://github.com/bdewitt84)

