# Unified ARP Tool

A modern web application built with Solara for viewing and analyzing ARP (Address Resolution Protocol) data across network namespaces. This tool provides a user-friendly interface to monitor and troubleshoot network connectivity issues.

## Features

- View ARP tables across multiple network namespaces
- Real-time data visualization
- Responsive design that works on desktop and mobile
- Dark theme with professional styling
- Easy-to-use interface for network administrators

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver
- Network access to your SuzieQ Enterprise Server

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd unified_arp
   ```

2. Create and activate a virtual environment using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3a. Install the package in development mode with dependencies:
   ```bash
   uv pip install -e .
   ```
   
   This will install all the dependencies listed in `pyproject.toml` in development mode.

   - Installs the package in development/editable mode
   - Changes to the source code are immediately reflected without reinstallation
   - Includes all development dependencies (like black, ruff) from pyproject.toml
   - Best for active development and testing


3b. Production Installation (Minimal Dependencies):
   ```bash
   uv pip install "solara>=1.54.0" "python-dotenv>=1.2.1" "pandas>=2.3.3"
   ```
   
   This will install all the dependencies listed in `pyproject.toml` in development mode.

    - Installs only the essential runtime dependencies
    - More lightweight installation
    - Better for production deployments
    - Doesn't include development tools


## Configuration

1. Copy the example environment file:
   ```bash
   cp .env_sample .env
   ```

2. Edit the `.env` file with your SuzieQ server details:
   ```env
   SQ_API_TOKEN=your_api_token_here
   SQ_ENDPOINT=your.suzieq.server
   SQ_PORT=8000  # Optional, defaults to 8000
   ```

## Running the Application

Start the Solara development server:

```bash
uv run solara run UnifiedARP_APP.py
```

The application will be available at: http://localhost:8765

## Solara vs Streamlit

### Advantages of Solara
- **Performance**: Built on React, offering better performance for complex UIs
- **Component-based**: More flexible and reusable UI components
- **State Management**: Better state management for complex applications
- **Custom Styling**: More control over the look and feel

### Disadvantages of Solara
- **Learning Curve**: Steeper learning curve compared to Streamlit
- **Smaller Community**: Fewer resources and community examples
- **Less Batteries-Included**: Requires more manual setup for common features

### When to Use Solara
- Building complex, production-grade applications
- Need for custom UI components
- Performance is a critical requirement
- You're comfortable with React-like components

### When to Use Streamlit
- Quick prototypes and MVPs
- Simpler applications with standard UI components
- When development speed is more important than customization
- When you want access to a larger ecosystem of components

## Troubleshooting

- **No namespaces found**: Verify your SuzieQ server is running and accessible
- **Connection errors**: Check your `.env` file for correct API credentials
- **UI issues**: Clear your browser cache if the UI doesn't update

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.