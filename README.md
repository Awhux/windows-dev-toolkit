# Windows Developer Utilities Toolkit

A comprehensive toolkit for Windows development teams to automate routine tasks and streamline their development workflow.

## Features

- **Windows Configuration**
  - Enable Developer Mode
  - Configure Windows Features for development
  - Optimize system performance
  - Configure Windows Defender exceptions for development directories

- **Office LTSC Management**
  - Download and use the official Office Deployment Tool
  - Configure Office LTSC deployment
  - Deploy Office LTSC using volume licensing
  - Remove Office installations

- **Development Environment Setup**
  - Install essential development tools
  - Configure Python development environment
  - Configure Node.js development environment
  - Configure .NET development environment

## Requirements

- Windows 10 or Windows 11
- Administrator privileges
- Internet connection for downloading tools and packages

## Installation

### Option 1: Download the pre-built executable

1. Download the latest release from the releases page
2. Run the executable as administrator

### Option 2: Build from source

```bash
# Clone the repository
git clone https://github.com/Awhux/windows-dev-toolkit.git
cd windows-dev-toolkit

# Install dependencies
pip install -e ".[dev]"

# Build the executable
make build
```

The executable will be created in the `dist/` directory.

## Usage

1. Launch the application with administrator privileges
2. Navigate the menu to select the desired functionality
3. Follow the on-screen prompts

## Development

### Setup development environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linters
make lint

# Run tests
make test

# Run the application directly (without building)
make run
```

### Project Structure

```
windows-dev-toolkit/
├── src/      # Main package
│   ├── __init__.py
│   ├── main.py               # Entry point
│   ├── modules/              # Feature modules
│   │   ├── __init__.py
│   │   ├── environment_setup.py
│   │   ├── office_deployment.py
│   │   └── windows_config.py
│   └── utils/                # Utility modules
│       ├── __init__.py
│       ├── admin_check.py
│       ├── cleanup.py
│       └── ui.py
├── tests/                    # Test suite
├── Makefile                  # Build tasks
├── pyproject.toml            # Project metadata
├── Dockerfile                # For building in container
└── README.md                 # This file
```

## Security and Ethics

This toolkit is designed for legitimate development purposes only. It requires administrator privileges and implements safeguards:

- Clear warnings about potential misuse
- Explicit confirmation before any system modification
- Technical safeguards against unintended use

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request