import json
from pathlib import Path
import pycountry
import os
import geopandas as gpd # Import geopandas

# --- Logger for consistent output ---
class SimpleLogger:
    def info(self, message):
        print(f"INFO: {message}")
    def error(self, message):
        print(f"ERROR: {message}")

logger = SimpleLogger()

# --- Dependency Functions ---

def get_country_name_from_iso_code(iso_code: str) -> str | None:
    """
    Retrieves the common name of a country from its ISO 3166-1 alpha-2 or alpha-3 code.

    This function uses the 'pycountry' library to perform the lookup. It is robust
    to both 2-letter (alpha-2) and 3-letter (alpha-3) country codes.

    Args:
        iso_code (str): The ISO 3166-1 country code (e.g., 'US', 'USA', 'DE', 'DEU').
                        The input is case-insensitive.

    Returns:
        str | None: The common name of the country (e.g., 'United States'), or
                    None if the ISO code is not a valid code or not found.
    """
    # Ensure the input is a string and handle potential leading/trailing whitespace
    iso_code = str(iso_code).strip().upper()

    try:
        # First, try to look up by alpha-2 code
        country = pycountry.countries.get(alpha_2=iso_code)
        if country:
            return country.name

        # If not found, try to look up by alpha-3 code
        country = pycountry.countries.get(alpha_3=iso_code)
        if country:
            return country.name

        # If neither lookup is successful, return None
        return None

    except Exception as e:
        # Catch any other exceptions during the lookup process and return None
        print(f"An error occurred while looking up ISO code '{iso_code}': {e}")
        return None

def get_iso_code_from_country_name(country_name: str) -> str | None:
    """
    Returns the 3-letter ISO code for a given country name using the pycountry library.

    Args:
        country_name (str): The common name of the country (e.g., "United States", "Canada").

    Returns:
        str | None: The 3-letter ISO code (e.g., "USA") if found, otherwise None.
    """
    try:
        country = pycountry.countries.search_fuzzy(country_name)
        if country:
            return country[0].alpha_3
        return None
    except LookupError:
        return None
    except Exception as e:
        logger.error(f"An error occurred while looking up ISO code for '{country_name}': {e}")
        return None

# --- Main Logic Function ---

def load_country_boundaries_to_dict(
    country_names_to_load: list[str],
    target_adm_level: int = 0, # Changed to single integer, default to ADM0
    release_type: str = "gbOpen",
    output_base_folder: str | Path = "geoboundaries_output"
) -> dict[str, gpd.GeoDataFrame]: # Updated return type hint for single-level dict
    """
    Loads administrative boundary data for a list of countries from local GeoJSON files
    into a dictionary, mapping country names to their GeoPandas GeoDataFrames (gdf)
    for a single specified administrative level.

    Args:
        country_names_to_load (list[str]): A list of country names (e.g., ["United States", "Canada"]).
        target_adm_level (int): The single administrative level to load (e.g., 0 for ADM0).
        release_type (str): The release type used when saving the files (e.g., "gbOpen").
        output_base_folder (str | Path): The base directory where the GeoJSON files are cached.

    Returns:
        dict: A dictionary where keys are country names and values are GeoPandas GeoDataFrames
              for the specified administrative level.
    """
    output_base_folder = Path(output_base_folder)
    country_boundaries_dict: dict[str, gpd.GeoDataFrame] = {} # Initialize with single-level type hint

    logger.info(f"\n--- Creating dictionary: country_name -> boundary_gdf (ADM{target_adm_level}) ---")

    for country_name in country_names_to_load:
        iso_code = get_iso_code_from_country_name(country_name)
        if iso_code:
            # Construct the expected cache file path for the single target_adm_level
            cache_file_path = output_base_folder / f"{iso_code}_ADM{target_adm_level}_{release_type}.geojson"
            
            if cache_file_path.exists():
                logger.info(f"Loading boundary data for '{country_name}' (ADM{target_adm_level}) from: {cache_file_path}")
                try:
                    # Use geopandas.read_file to load directly into a GeoDataFrame
                    boundary_gdf = gpd.read_file(cache_file_path)
                    country_boundaries_dict[country_name] = boundary_gdf
                    logger.info(f"Successfully loaded {country_name} (ADM{target_adm_level}) as GeoDataFrame.")
                except Exception as e: # Catch broader exceptions for file reading/GeoDataFrame creation
                    logger.error(f"Error loading GeoDataFrame for {country_name} (ADM{target_adm_level}) from file {cache_file_path}: {e}. Skipping.")
            else:
                logger.info(f"Cache file not found for '{country_name}' (ADM{target_adm_level}) at {cache_file_path}. Please ensure you have run the 'fetch_boundaries' function to download and save the data first.")
        else:
            logger.info(f"Could not find ISO code for '{country_name}'. Skipping this country.")
    
    logger.info("\n--- Contents of the final country_boundaries_dict ---")
    if country_boundaries_dict:
        for country_name, gdf in country_boundaries_dict.items():
            if isinstance(gdf, gpd.GeoDataFrame):
                logger.info(f"'{country_name}': Loaded GeoDataFrame with {len(gdf)} features for ADM{target_adm_level}.")
            else:
                logger.info(f"'{country_name}': Data available but not a valid GeoDataFrame for ADM{target_adm_level}.")
    else:
        logger.info("The dictionary is empty. No boundary data could be loaded.")

    return country_boundaries_dict