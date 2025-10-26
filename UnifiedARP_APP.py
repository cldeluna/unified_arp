#!/usr/bin/python -tt
# Project: unified_arp
# Filename: UnifiedARP_APP.py
# claudiadeluna
# PyCharm

"""
Solara Application for Unified ARP Tool

This application demonstrates how to build an interactive web interface using Solara.
It connects to a SuzieQ API to fetch and display network namespaces.

Key Concepts:
- Reactive variables: Automatically update the UI when values change
- Components: Reusable UI elements with their own state
- Layout: How to structure the page with proper spacing and styling
- State Management: How to handle and share state between components
"""

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "10/26/25"
__copyright__ = "Copyright (c) 2023 Claudia"
__license__ = "Python"

# Standard library imports
import logging
import os
from typing import List, Dict, Any, Optional

# Third-party imports
import solara

# Local imports
import utils

# Define the desired column order for the ARP table
DESIRED_COLUMNS = [
    'hostname', 'ipAddress', 'macaddr', 'oif', 'vlan', 'namespace',
    'lastUpdateTime_date', 'lastUpdateTime_time',
    'lastPolled_date', 'lastPolled_time'
]

# Define the desired column order for the ARP table
DESIRED_COLUMNS = [
    'hostname', 'ipAddress', 'macaddr', 'oif', 'vlan', 'namespace',
    'lastUpdateTime_date', 'lastUpdateTime_time',
    'lastPolled_date', 'lastPolled_time'
]

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ====================
# Reactive State
# ====================
# In Solara, we use reactive variables to manage state. When these variables change,
# any component that depends on them will automatically update.
namespace_list = solara.reactive([])  # Stores the list of available namespaces
selected_namespace = solara.reactive("")  # Tracks the currently selected namespace
arp_data = solara.reactive(None)  # Stores the ARP data for the selected namespace
loading = solara.reactive({"namespaces": False, "arp": False})  # Track loading states separately
error = solara.reactive("")  # Stores error messages if any occur

# Default column order
DEFAULT_COLUMNS = [
    'hostname', 'ipAddress', 'macaddr', 'oif', 'remote', 'state',
    'timestamp_date', 'timestamp_time',
    'lastUpdateTime_date', 'lastUpdateTime_time',
    'lastPolled_date', 'lastPolled_time',
    'namespace',  'vrf', 'vlan', 'mackey'
]

# This will be set inside the component
column_order = solara.reactive(DEFAULT_COLUMNS)

def reset_column_order():
    """Reset column order to default"""
    column_order.set(DEFAULT_COLUMNS.copy())


def load_arp_data(namespace: str) -> None:
    """
    Fetch ARP data for the selected namespace
    
    Args:
        namespace: The namespace to fetch ARP data for
    """
    if not namespace:
        return
        
    try:
        loading.value = {"namespaces": loading.value["namespaces"], "arp": True}
        error.value = ""
        logger.info(f"Loading ARP data for namespace: {namespace}")
        
        # Fetch ARP data from the API
        arp_result = utils.get_unified_arp(namespace)
        
        if arp_result is False:
            error_msg = "Failed to fetch or process ARP data. Check the logs for more details."
            error.value = error_msg
            logger.error(error_msg)
            arp_data.set(None)
            return
            
        if not arp_result:
            error_msg = "No ARP data available for the selected namespace."
            error.value = error_msg
            logger.info(error_msg)
            arp_data.set([])
            return
            
        # Set the ARP data
        logger.info(f"Successfully loaded {len(arp_result)} ARP entries for {namespace}")
        arp_data.set(arp_result)
        error.value = ""
        
    except Exception as e:
        error_msg = f"Error loading ARP data: {str(e)}"
        error.value = error_msg
        logger.error(error_msg, exc_info=True)
        arp_data.set(None)
    finally:
        loading.value = {"namespaces": loading.value["namespaces"], "arp": False}


def load_namespaces() -> None:
    """
    Fetch the list of namespaces from the SuzieQ API.
    
    This function:
    1. Sets the loading state to True to show a loading indicator
    2. Clears any previous errors
    3. Loads environment variables (API credentials)
    4. Fetches namespaces from the API
    5. Updates the UI state with the results
    """
    try:
        # Indicate that we're loading data
        loading.value = {"namespaces": True, "arp": loading.value["arp"]}
        error.value = ""  # Clear any previous errors
        logger.info("Loading namespaces...")
        
        # Load environment variables (API credentials)
        utils.load_env()
        
        # Fetch namespaces from the API
        namespaces = utils.get_namespace_list()
        
        # Check if we got any namespaces back
        if not namespaces:
            error_msg = "No namespaces found. Please check your SuzieQ configuration."
            error.value = error_msg
            logger.warning(error_msg)
            return
            
        # Update the reactive variable with the new namespaces
        namespace_list.set(namespaces)
        logger.info(f"Loaded {len(namespaces)} namespaces")
        
        # Don't select a namespace by default
        # User must explicitly select a namespace
        
    except Exception as e:
        # Handle any errors that occur during the API call
        error_msg = f"Error loading namespaces: {str(e)}"
        error.value = error_msg
        logger.error(error_msg, exc_info=True)
    finally:
        # Always ensure loading is set to False when done
        loading.value = {"namespaces": False, "arp": loading.value["arp"]}


@solara.component
def NamespaceSelector():
    """
    A reusable component that displays a dropdown for namespace selection.
    
    This component demonstrates several Solara concepts:
    - Component lifecycle (using use_effect)
    - Conditional rendering
    - Event handling
    - Working with reactive variables
    """
    # Display a section header
    solara.Markdown("## Select a Location (Namespace)")
    
    # Load namespaces when the component is first rendered
    # The empty dependency array [] means this effect runs once when the component mounts
    solara.use_effect(load_namespaces, [])
    
    # Load ARP data when selected_namespace changes
    solara.use_effect(
        lambda: load_arp_data(selected_namespace.value) if selected_namespace.value else None,
        [selected_namespace.value]
    )
    
    # ===========================
    # Loading State
    # ===========================
    if loading.value["namespaces"]:
        with solara.Card("Loading..."):
            solara.ProgressLinear()
        return
    
    # ===========================
    # Error State
    # ===========================
    if error.value:
        with solara.Card():
            solara.Markdown(f"**Error:** {error.value}", style={"color": "red"})
            solara.Button("Retry", on_click=load_namespaces, color="error")
        return
    
    # ===========================
    # Empty State
    # ===========================
    if not namespace_list.value:
        with solara.Card():
            solara.Markdown("**Warning:** No namespaces available", style={"color": "orange"})
            solara.Button("Reload", on_click=load_namespaces, color="primary")
        return
    
    # ===========================
    # Success State
    # ===========================
    with solara.Card(style={"margin-bottom": "24px"}):
        solara.Select(
            label="Select a namespace to view ARP data for that location",
            values=[""] + namespace_list.value,  # Add empty option
            value=selected_namespace,
            on_value=selected_namespace.set,
        )
        
        # Show message when no namespace is selected
        if not selected_namespace.value:
            with solara.Card():
                solara.Markdown("Please select a namespace from the dropdown above to view ARP data.", 
                              style={"color": "#666", "font-style": "italic"})
            return  # Don't show ARP data section
                
        # Show ARP data loading state
        if loading.value["arp"]:
            with solara.Card("Loading ARP data..."):
                solara.ProgressLinear()
            return  # Don't show ARP data while loading
        
        # Show ARP data if available
        if arp_data.value:
            with solara.Card("ARP Data", style={"margin-top": "16px"}):
                if isinstance(arp_data.value, list) and arp_data.value:
                    import pandas as pd
                    
                    # Convert to DataFrame if it's not already
                    df = pd.DataFrame(arp_data.value)
                    
                    # Reorder and select columns to show
                    display_columns = []
                    
                    # Add timestamp columns if they exist
                    time_columns = []
                    for col in ['timestamp', 'lastUpdateTime', 'lastPolled']:
                        if f"{col}_date" in df.columns and f"{col}_time" in df.columns:
                            time_columns.extend([f"{col}_date", f"{col}_time"])
                    
                    # Define the preferred column order
                    preferred_order = [
                        'ipAddress', 'macaddr', 'oif', 'remote', 'state',
                        'timestamp_date', 'timestamp_time',
                        'lastUpdateTime_date', 'lastUpdateTime_time',
                        'lastPolled_date', 'lastPolled_time',
                        'namespace', 'hostname', 'vrf', 'vlan', 'mackey'
                    ]
                    
                    # Filter to only include columns that exist in the DataFrame
                    display_columns = [col for col in preferred_order if col in df.columns]
                    
                    # Add any remaining columns that weren't in our preferred order
                    remaining_columns = [col for col in df.columns if col not in display_columns]
                    display_columns.extend(remaining_columns)
                    
                    # Create a styled DataFrame with better column headers
                    styled_df = df[display_columns].copy()
                    
                    # First, reorder the columns before renaming
                    desired_columns = ['hostname', 'ipAddress', 'macaddr', 'oui', 'oif', 'vlan', 'namespace',
                                     'lastUpdateTime_date', 'lastUpdateTime_time',
                                     'lastPolled_date', 'lastPolled_time']
                    
                    # Get columns that exist in both the DataFrame and our desired columns
                    ordered_columns = [col for col in desired_columns if col in styled_df.columns]
                    # Add any remaining columns
                    remaining_columns = [col for col in styled_df.columns if col not in ordered_columns]
                    # Apply the order
                    styled_df = styled_df[ordered_columns + remaining_columns]
                    
                    # Now rename the columns for better readability
                    column_renames = {
                        'ipAddress': 'IP Address',
                        'macaddr': 'MAC Address',
                        'oif': 'Interface',
                        'remote': 'Remote',
                        'state': 'State',
                        'namespace': 'Namespace',
                        'hostname': 'Hostname',
                        'vrf': 'VRF',
                        'vlan': 'VLAN',
                        'mackey': 'MAC Key',
                        'timestamp_date': 'Date',
                        'timestamp_time': 'Time',
                        'lastUpdateTime_date': 'Last Update Date',
                        'lastUpdateTime_time': 'Last Update Time',
                        'lastPolled_date': 'Last Polled Date',
                        'lastPolled_time': 'Last Polled Time'
                    }
                    
                    # Apply the renames
                    styled_df = styled_df.rename(columns=column_renames)
                    
                    # Display the ARP table
                    with solara.Card(style={"overflow-x": "auto"}):
                        solara.Markdown("### ARP Table")
                        
                        # Display the data grid
                        solara.DataFrame(
                            styled_df,
                            items_per_page=20
                        )
                else:
                    solara.Markdown("No ARP data available for the selected namespace.")


@solara.component
def Page():
    """
    The main page component that defines the overall layout.
    
    This component demonstrates:
    - Page layout with header and content areas
    - Styling with CSS-in-JS
    - Component composition
    """
    # ====================
    # Page Layout
    # ====================
    # The main container takes up the full viewport height
    with solara.Column(style={
        "min-height": "100vh",  # At least full viewport height
        "background-color": "#f5f5f5"  # Light gray background
    }):
        # ====================
        # Header Section
        # ====================
        with solara.Row(style={
            "background-color": "#d32f2f",  # Red 700 from Material Design
            "color": "white",
            "padding": "10px 24px",
            "margin-bottom": "24px",
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "center"
        }):
            # Logo with right margin
            solara.Image("assets/EIA Logo FINAL small_Dark Background.png",
                        width="200px",
                        classes=["mr-4"])
            
            # Title
            solara.Markdown("# Unified ARP Tool", 
                          style={
                              "margin": "0",
                              "color": "white",
                              "flex-grow": "1",
                              "text-align": "center"
                          })
            
            # Placeholder to balance the layout (same width as logo for symmetry)
            solara.HTML("div", style={"width": "200px"})
            
            # Set the browser tab title
            solara.Title("Unified ARP Tool")
        
        # ====================
        # Main Content Area
        # ====================
        with solara.Column(style={
            "max-width": "1200px",  # Maximum width for better readability
            "width": "100%",         # Full width up to max-width
            "margin": "0 auto",      # Center the content
            "padding": "0 24px"      # Horizontal padding on small screens
        }):
            # Content card with shadow and rounded corners
            with solara.Card(style={
                "margin": "16px 0",
                "padding": "24px",
                "border-radius": "8px",
                "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
                "background-color": "white"
            }):
                # Render the NamespaceSelector component
                # This is an example of component composition
                NamespaceSelector()


# For development with `solara run UnifiedARP_APP.py`
if __name__ == "__main__":
    # Initialize the app with a default layout
    Page()
