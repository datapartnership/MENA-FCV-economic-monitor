import requests
import json
import pycountry
import os
from pathlib import Path # Use pathlib as requested by user's snippet for cache_dir

# Define a specific GitHub commit hash for raw data access if needed.
# This can be updated if the 'main' branch doesn't contain the desired data
# or if you need to target a specific historical version.
# NOTE: This is no longer used directly in fetch_boundaries to align with user's snippet,
# but kept here for reference if a GitHub fallback is explicitly re-requested.
GITHUB_COMMIT_HASH = "b7dd6a55701c76a330500ad9d9240f2b9997c6a8"

# Placeholder for logger (since actual logger setup isn't in this environment)
class SimpleLogger:
    def info(self, message):
        print(f"INFO: {message}")
    def error(self, message):
        print(f"ERROR: {message}")

logger = SimpleLogger()

# Placeholder for load_geojson_to_ee (since Earth Engine isn't in this environment)
def load_geojson_to_ee(file_path):
    logger.info(f"Placeholder: Loading {file_path} into Earth Engine (not implemented in this environment).")
    # In a real EE environment, this would be something like:
    # return ee.FeatureCollection(str(file_path))
    return None # Return None as a placeholder since EE is not available

def get_iso_code_from_country_name(country_name: str) -> str | None:
    """
    Returns the 3-letter ISO code for a given country name using the pycountry library.

    Args:
        country_name (str): The common name of the country (e.g., "United States", "Canada").

    Returns:
        str | None: The 3-letter ISO code (e.g., "USA") if found, otherwise None.
    """
    try:
        # Search for the country by its common name
        country = pycountry.countries.search_fuzzy(country_name)
        if country:
            # pycountry.countries.search_fuzzy returns a list, take the first match
            return country[0].alpha_3
        return None
    except LookupError:
        # Handle cases where the country name is not found
        return None
    except Exception as e:
        logger.error(f"An error occurred while looking up ISO code for '{country_name}': {e}")
        return None

def fetch_boundaries(
    iso3_code: str,
    adm_level: int,
    release_type: str = "gbOpen",
    output_dir: str | Path = "../../data/boundaries", # Changed default to match example
):
    """
    Fetch administrative boundaries from GeoBoundaries API and save them to a cache.
    Adapts the user's provided function signature and caching logic.

    Args:
        iso3_code: ISO3 code of the country.
        adm_level: Administrative level (0, 1, 2, etc.).
        release_type: Release type (e.g., "gbOpen", "gbCurrent").
        output_dir: Directory to save the downloaded GeoJSON file.

    Returns:
        The GeoJSON data as a Python dictionary. Returns None if data cannot be fetched.
        (Note: The original request for ee.FeatureCollection is not supported in this environment)
    """
    # Ensure output_dir is a Path object
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Construct cache file path as per user's snippet
    cache_file = output_dir / f"{iso3_code}_ADM{adm_level}_{release_type}.geojson"

    if cache_file.exists():
        logger.info(f"Loading boundaries from cache: {cache_file}")
        # load_geojson_to_ee(cache_file) is a placeholder
        with open(cache_file, 'r') as f:
            try:
                return json.load(f) # Return the JSON content directly
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from cache file {cache_file}: {e}")
                os.remove(cache_file) # Remove corrupted cache file
                logger.info(f"Removed corrupted cache file: {cache_file}. Will attempt to re-download.")
                return None # Indicate failure to load from cache

    # API URL construction
    url = f"https://www.geoboundaries.org/api/current/{release_type}/{iso3_code}/ADM{adm_level}"
    logger.info(f"Fetching metadata from API: {url}")

    geojson_content = None
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        metadata = response.json()

        download_url = None

        if isinstance(metadata, list):
            # If metadata is a list (common for geoBoundaries API)
            if metadata:
                for item in metadata:
                    if not isinstance(item, dict):
                        logger.error(f"Unexpected item type in metadata list for {iso3_code}. Expected dict, got {type(item)}. Item: {item}")
                        continue
                    # Prioritize 'geojson' as per geoBoundaries API documentation
                    if 'geojson' in item:
                        download_url = item['geojson']
                        break
                    # Fallback to 'gjDownloadURL' if 'geojson' not found, as per user's snippet
                    elif 'gjDownloadURL' in item:
                        download_url = item['gjDownloadURL']
                        logger.info(f"Found 'gjDownloadURL' in metadata for {iso3_code}. Using it.")
                        break
        elif isinstance(metadata, dict):
            # If metadata is a single dictionary (as implied by user's original snippet)
            # Prioritize 'geojson' as per geoBoundaries API documentation
            if 'geojson' in metadata:
                download_url = metadata['geojson']
            elif 'gjDownloadURL' in metadata: # Fallback as per user's snippet
                download_url = metadata['gjDownloadURL']
                logger.info(f"Found 'gjDownloadURL' in metadata for {iso3_code}. Using it.")
        else:
            logger.error(f"API response for {iso3_code} is neither a list nor a dictionary. Type: {type(metadata)}. Content: {metadata}")


        if download_url:
            logger.info(f"Downloading GeoJSON from: {download_url}")
            geojson_response = requests.get(download_url, timeout=30)
            geojson_response.raise_for_status()
            geojson_content = geojson_response.json()
            logger.info(f"Successfully downloaded GeoJSON for {iso3_code}.")

            # Save to cache
            with open(cache_file, "w") as f:
                json.dump(geojson_content, f, indent=2)
            logger.info(f"Boundaries saved to cache: {cache_file}")

        else:
            logger.info(f"No GeoJSON download URL ('geojson' or 'gjDownloadURL') found in metadata for {iso3_code} at ADM level {adm_level}.")
            # Removed GitHub fallback to align with user's provided function structure.

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred for {iso3_code}: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Connection error occurred for {iso3_code}: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Timeout error occurred for {iso3_code}: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"An error occurred during the request for {iso3_code}: {req_err}")
    except json.JSONDecodeError as json_err:
        logger.error(f"JSON decode error for {iso3_code}: {json_err}. Response content: {response.text[:200]}...")
    except Exception as e: # Catch-all for other unexpected errors
        logger.error(f"An unexpected error occurred for {iso3_code}: {e}")

    # load_geojson_to_ee(cache_file) is a placeholder in the original snippet.
    # We return the raw geojson_content here.
    return geojson_content

if __name__ == "__main__":
    # --- IMPORTANT: Install pycountry first: pip install pycountry ---

    output_base_folder = "../../data/boundaries/" # Define your desired output folder
    
    # List of country names to fetch boundaries for
    country_names_to_fetch = ["Bolivia"]#[
    # "Afghanistan","Pakistan","Algeria","Morocco","Libya","Yemen","Iran", "Iraq",
    # "Syria","Egypt","Lebanon","Djibouti","United Arab Emirates","Jordan","Israel","Palestine",
    # "Oman", "Malta", "Qatar", "Saudi Arabia", "Kuwait", "Tunisia", "Bahrain"]
    
    # Convert country names to ISO codes
    countries_iso_codes = []
    logger.info("--- Converting country names to ISO codes ---")
    for country_name in country_names_to_fetch:
        iso_code = get_iso_code_from_country_name(country_name)
        if iso_code:
            countries_iso_codes.append(iso_code)
            logger.info(f"'{country_name}' -> '{iso_code}'")
        else:
            logger.info(f"Could not find ISO code for '{country_name}'. Skipping.")

    adm_levels_to_fetch = [0, 1] # Fetch both ADM0 and ADM1 (using int as per new function signature)

    logger.info(f"\n--- Fetching and saving boundaries to '{output_base_folder}' for {countries_iso_codes} ---")

    for adm_level in adm_levels_to_fetch:
        logger.info(f"\n--- Processing ADM level: ADM{adm_level} ---")
        for iso_code in countries_iso_codes:
            boundaries_data = fetch_boundaries(iso_code, adm_level=adm_level, output_dir=output_base_folder)

            logger.info(f"\n--- Summary for {iso_code} (ADM{adm_level}) ---")
            if boundaries_data and 'features' in boundaries_data:
                logger.info(f"Type: {boundaries_data.get('type')}")
                logger.info(f"Number of features: {len(boundaries_data['features'])}")
            else:
                logger.info("No features or invalid GeoJSON structure.")

 
