<div align="center">
  <img src="assets/EIA Logo FINAL small_Dark Background.png" alt="EIA Logo" width="300">
  <h1>Unified ARP Tool</h1>
</div>
## GOAL

This repository serves as an example of:

- some handy "ready to use" functions to extract ARP (and ultimately other) data from your SuzieQ Enterprise server. 
  - The `try_sq_rest_call` function in utils.py can serve as a foundation for all your REST calls to SuzieQ.  Division of labor has the rest call handling things like crafting the call itself, and other functions can provide the API endpoints. We use this strategy in production environments
- an example of using Solara as a user (or network engineer) front end to share your scripts
  - I do like the "cleaner" Solara front end but there is a steeper learning cuve with Solara. I could have created this repository in about 20 minutes using Streamlit (Note: I am more familiar with Streamlit but instead I spent several frustrating hours with my basic Solara knowledge and AI "help" learning absolutely nothing to create this)

This little APP does nothing different than the SuzieQ GUI or CLI does ... but think about what you could do with your own scripts and workflows with this data.   

- What if you had to track the history of a particular MAC over the last week or months?
- What if you needed to know if a device was configured to use DHCP?
- What if you had other find a MAC that fell off the network (last seen), find the last switch and interface it was connected to and determine what MAC is on that interface now?

The possibilities are endless...

🎥 [SuzieQ Enterprise and the Unified ARP Table](http://https://vimeo.com/1130738176?fl=ml&fe=ec "SuzieQ Enterprise and the Unified ARP Table") ~15min

📝 [A Unified ARP Table (and how to get one when you don’t have one)](https://gratuitous-arp.net/a-unified-arp-table-how-to-get-one-when-you-dont-have-one/)

## Features

- View ARP tables across multiple network devices (multi-vendor) at a locaton (namespace)
- Responsive design that works on desktop and mobile

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver
- Network access (API Token) to your SuzieQ Enterprise Server

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



## Troubleshooting the APP

- **No namespaces found**: Verify your SuzieQ server is running and accessible
- **Connection errors**: Check your `.env` file for correct API credentials
- **UI issues**: Clear your browser cache if the UI doesn't update

---

## Solara vs Streamlit

### Advantages of Solara
- **Performance**: Built on React, offering better performance for complex UIs
- **Component-based**: More flexible and reusable UI components
- **State Management**: Better state management for complex applications <--This is where Solara wins in my view
- **Custom Styling**: More control over the look and feel

### Disadvantages of Solara
- **Learning Curve**: Steeper learning curve compared to Streamlit
- **Smaller Community**: Fewer resources and community examples
- **Less Batteries-Included**: Requires more manual setup for common features

### When to Use Solara
- Building complex, production-grade applications, which require lots of "state" management
- Need for custom UI components
- Performance is a critical requirement
- You're comfortable with React-like components

### When to Use Streamlit
- Quick prototypes
- Simpler applications with standard UI components
- When development speed is more important than customization 
- When you want access to a larger ecosystem of components and support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.