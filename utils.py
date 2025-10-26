#!/usr/bin/python -tt
# Project: unified_arp
# Filename: utils.py
# claudiadeluna
# PyCharm

from __future__ import absolute_import, division, print_function
from typing import Optional, Dict, Any, Union, List, Tuple
import os
import requests
import logging
import dotenv
from urllib import parse
from datetime import datetime
import pytz
import pandas as pd

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "10/26/25"
__copyright__ = "Copyright (c) 2023 Claudia"
__license__ = "Python"

# Set up logging
logger = logging.getLogger(__name__)


def load_env():
    """
    Load environment variables from .env file
    """
    dotenv.load_dotenv()


def try_sq_rest_call(
    uri_path: str,
    url_options: str,
    secure: bool = True,
    port: str = "8000",
    debug: bool = True,
) -> Union[Dict[str, Any], bool]:
    """
    SuzieQ API REST Call
    
    Args:
        uri_path: The API endpoint path
        url_options: Query parameters as a string
        secure: Whether to use HTTPS (default: True)
        port: Port number to use (default: 8000)
        debug: Enable debug logging (default: True)
        
    Returns:
        Union[Dict[str, Any], bool]: API response as dict or False on failure
    """
    try:
        API_ACCESS_TOKEN = os.getenv("SQ_API_TOKEN")
        API_ENDPOINT = os.getenv("SQ_ENDPOINT")
        
        if not API_ENDPOINT:
            logger.error("SQ_ENDPOINT environment variable not set")
            return False
            
        if not API_ACCESS_TOKEN:
            logger.error("SQ_API_TOKEN environment variable not set")
            return False

        # Construct the URL
        scheme = "https" if secure else "http"
        port_str = f":{port}" if port else ""
        url = f"{scheme}://{API_ENDPOINT}{port_str}{uri_path}?{url_options}"

        payload = "\r\n"
        headers = {
            "Content-Type": "text/plain",
            "Authorization": f"Bearer {API_ACCESS_TOKEN}",
        }

        if debug:
            logger.debug(f"API URL: {url}")

        # Disable SSL verification warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Make the request with SSL verification disabled
        response = requests.get(
            url, 
            headers=headers, 
            data=payload, 
            verify=False,  # Disable SSL verification
            timeout=30     # Add timeout to prevent hanging
        )

        return response

    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error: {str(e)}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    
    # Debug logging for response
    if debug and 'response' in locals() and response is not None and hasattr(response, 'json'):
        try:
            json_data = response.json()
            if json_data:
                logger.debug(f"Response JSON: {json_data}")
            else:
                logger.debug("No data returned for REST call")
        except Exception as e:
            logger.debug(f"Error parsing JSON response: {str(e)}")
    
    return False


def get_namespace_list() -> List[str]:
    """
    Get a list of namespaces from SuzieQ API.
    
    Returns:
    """
    # Initialize
    namespace_list = []

    try:
        # Get unique namespaces from SuzieQ
        URI_PATH = "/api/v2/device/unique"
        URL_OPTIONS = "columns=namespace&ignore_neverpoll=true"
        ns_response = try_sq_rest_call(URI_PATH, URL_OPTIONS, secure=True, port="")

        # Check if we got a valid response
        if not ns_response:
            logger.error("Failed to get response from SuzieQ API")
            return namespace_list
            
        if not hasattr(ns_response, 'status_code'):
            logger.error(f"Unexpected response type: {type(ns_response)}")
            return namespace_list

        # Process successful response
        if ns_response.status_code == 200:
            try:
                json_data = ns_response.json()
                if json_data and isinstance(json_data, list):
                    # Extract namespaces from response
                    namespace_list = sorted([
                        line["namespace"] 
                        for line in json_data 
                        if isinstance(line, dict) and "namespace" in line
                    ])
            except Exception as e:
                logger.error(f"Error parsing namespace response: {str(e)}")
        else:
            # Handle error response
            error_msg = (
                f"Problem accessing SuzieQ REST API\n"
                f"Status: {ns_response.status_code} {getattr(ns_response, 'reason', '')}"
            )
            try:
                if hasattr(ns_response, 'json'):
                    json_data = ns_response.json()
                    if json_data:
                        error_msg += f"\nResponse: {json_data}"
            except Exception as e:
                logger.error(f"Error parsing error response: {str(e)}")
            
            logger.error(error_msg)
            
    except Exception as e:
        logger.error(f"Unexpected error in get_namespace_list: {str(e)}", exc_info=True)
    
    return namespace_list


def check_arp_ip(
    ipx: str, namespacex: str, view: str = "latest", start_time: str = "3 months ago"
) -> Union[Dict[str, Any], bool]:
    """
    Check ARP information for a specific IP address in a given namespace.

    Args:
        ipx: The IP address to look up
        namespacex: The namespace to search in
        view: The view to use (default: "latest")
        start_time: Time range to search (default: "3 months ago")

    Returns:
        Union[Dict[str, Any], bool]: The API response as a dictionary or False on failure
    """

    # start_time={start_time_url_encoded}&
    start_time_url_encoded = parse.quote(start_time)

    URI_PATH = "/api/v2/arpnd/show"
    URL_OPTIONS = f"view={view}&namespace={namespacex}&columns=default&ipAddress={ipx}"

    sq_api_response = try_sq_rest_call(URI_PATH, URL_OPTIONS, secure=True, port="")

    return sq_api_response


def get_local_timezone() -> str:
    """
    Get the local timezone of the user.
    
    Returns:
        str: IANA timezone string (e.g., 'America/New_York')
    """
    try:
        # Try to get the system timezone
        import tzlocal
        return str(tzlocal.get_localzone())
    except Exception:
        # Fallback to UTC if local timezone detection fails
        return 'UTC'


def format_timestamp(epoch_time: float, timezone_str: str = None) -> Tuple[str, str]:
    """
    Convert epoch timestamp to human-readable format in the specified timezone.
    
    Args:
        epoch_time: Unix timestamp in seconds or milliseconds
        timezone_str: IANA timezone string (e.g., 'America/New_York'). If None, uses local timezone.
        
    Returns:
        Tuple[str, str]: (formatted_date, formatted_time) in the specified timezone
    """
    if not timezone_str:
        timezone_str = get_local_timezone()
    
    try:
        # Convert to seconds if it's in milliseconds
        if epoch_time > 1e10:  # Rough check for milliseconds
            epoch_time = epoch_time / 1000.0
            
        # Create timezone-aware datetime
        tz = pytz.timezone(timezone_str)
        dt = datetime.fromtimestamp(epoch_time, tz)
        
        # Format date and time separately
        formatted_date = dt.strftime('%Y-%m-%d')
        formatted_time = dt.strftime('%H:%M:%S %Z')
        
        return formatted_date, formatted_time
    except Exception as e:
        logger.warning(f"Error formatting timestamp {epoch_time}: {str(e)}")
        return "N/A", "N/A"


def process_arp_data(arp_data: List[Dict], timezone_str: str = None) -> pd.DataFrame:
    """
    Process ARP data and add human-readable timestamps.
    
    Args:
        arp_data: List of ARP entries from the API
        timezone_str: IANA timezone string (e.g., 'America/New_York')
        
    Returns:
        pd.DataFrame: Processed DataFrame with human-readable timestamps
    """
    if not arp_data:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(arp_data)
    
    # Add human-readable timestamps if timestamp columns exist
    time_columns = ['timestamp', 'lastUpdateTime', 'lastPolled']
    for col in time_columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            # Create new columns for date and time
            date_col = f"{col}_date"
            time_col = f"{col}_time"
            
            # Apply formatting to each timestamp
            formatted = df[col].apply(lambda x: format_timestamp(x, timezone_str) if pd.notnull(x) else ("N/A", "N/A"))
            
            # Split into date and time columns
            df[[date_col, time_col]] = pd.DataFrame(formatted.tolist(), index=df.index)
            
            # Reorder columns to keep related fields together
            cols = list(df.columns)
            idx = cols.index(col)
            cols = cols[:idx+1] + [date_col, time_col] + [c for c in cols[idx+1:] if c not in [date_col, time_col]]
            df = df[cols]
    
    return df


def get_unified_arp(
    namespacex: str, view: str = "latest", start_time: str = "now"
) -> Union[List[Dict[str, Any]], bool]:
    """
    Get ARP information for a given namespace and process timestamps.

    Args:
        namespacex: The namespace to search in
        view: The view to use (default: "latest")
        start_time: Time range to search (default: "now")

    Returns:
        Union[List[Dict[str, Any]], bool]: Processed ARP data with human-readable timestamps or False on failure
    """
    start_time_url_encoded = parse.quote(start_time)
    URI_PATH = "/api/v2/arpnd/show"
    URL_OPTIONS = f"view={view}&namespace={namespacex}&columns=*"

    response = try_sq_rest_call(URI_PATH, URL_OPTIONS, secure=True, port="")
    
    if not response or not hasattr(response, 'json'):
        return False
        
    try:
        arp_data = response.json()
        if not isinstance(arp_data, list):
            logger.error(f"Expected list of ARP entries, got {type(arp_data)}")
            return False
            
        # Process the ARP data to add human-readable timestamps
        processed_df = process_arp_data(arp_data)
        
        # Drop the original timestamp columns, keeping only the human-readable ones
        timestamp_columns = ['timestamp', 'lastUpdateTime', 'lastPolled']
        columns_to_drop = [col for col in timestamp_columns if col in processed_df.columns]
        if columns_to_drop:
            processed_df = processed_df.drop(columns=columns_to_drop)
        
        # Convert the processed DataFrame back to a list of dicts
        return processed_df.to_dict('records')
        
    except Exception as e:
        logger.error(f"Error processing ARP data: {str(e)}", exc_info=True)
        return False


def main():
    pass


# Standard call to the main() function.
if __name__ == "__main__":
    main()
