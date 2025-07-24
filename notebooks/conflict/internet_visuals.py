from bokeh.plotting import figure, show
from bokeh.models import TabPanel, Tabs, LinearAxis, Range1d
from bokeh.layouts import column
from bokeh.io import output_notebook
import pandas as pd

def create_dual_axis_country_tabs(df):
    """
    Creates a Bokeh plot with tabs for each country, showing dual-axis plots
    with conflict metrics on left axis and download speed on right axis.
    
    Args:
        df (pd.DataFrame): DataFrame with columns: 'date', 'index', 'population', 
                          'country', 'download_speed', 'conflict_intensity_index', 
                          'nrFatalities', 'nrEvents'
    
    Returns:
        Tabs: Bokeh Tabs widget with country plots
    """
    
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Get unique countries
    countries = df['country'].unique()
    
    tab_panels = []
    
    for country in countries:
        # Filter data for this country
        country_data = df[df['country'] == country].sort_values('date')
        
        if country_data.empty:
            continue
            
        # Create figure with left y-axis for conflict metrics
        p = figure(
            title=f"Conflict Metrics vs Download Speed - {country}",
            x_axis_label='Date',
            y_axis_label='Conflict Intensity Index',
            x_axis_type='datetime',
            width=800,
            height=400,
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        # Plot conflict intensity on left axis (primary)
        conflict_line = p.line(
            country_data['date'], 
            country_data['conflict_intensity_index'],
            line_width=2,
            color='red',
            alpha=0.8,
            legend_label='Conflict Intensity'
        )
        
        conflict_circle = p.scatter(
            country_data['date'],
            country_data['conflict_intensity_index'],
            size=6,
            color='red',
            alpha=0.6
        )
        
        # Set up right y-axis for download speed
        # First, determine the range for download speed
        download_min = country_data['download_speed'].min()
        download_max = country_data['download_speed'].max()
        download_range = download_max - download_min
        download_padding = download_range * 0.1
        
        # Create right y-axis
        p.extra_y_ranges = {
            "download": Range1d(
                start=download_min - download_padding,
                end=download_max + download_padding
            )
        }
        
        # Add right y-axis
        p.add_layout(
            LinearAxis(
                y_range_name="download",
                axis_label="Download Speed (Mbps)"
            ), 
            'right'
        )
        
        # Plot download speed on right axis
        download_line = p.line(
            country_data['date'],
            country_data['download_speed'],
            line_width=2,
            color='blue',
            alpha=0.8,
            y_range_name="download",
            legend_label='Download Speed'
        )
        
        download_circle = p.scatter(
            country_data['date'],
            country_data['download_speed'],
            size=6,
            color='blue',
            alpha=0.6,
            y_range_name="download"
        )
        
        # Customize the plot
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
        p.title.text_font_size = "14pt"
        p.xaxis.axis_label_text_font_size = "12pt"
        p.yaxis.axis_label_text_font_size = "12pt"
        
        # Add grid
        p.grid.grid_line_alpha = 0.3
        
        # Create tab panel for this country
        tab_panel = TabPanel(child=p, title=country)
        tab_panels.append(tab_panel)
    
    # Create tabs widget
    tabs = Tabs(tabs=tab_panels)
    
    return tabs

# Alternative version with fatalities instead of conflict intensity
def create_dual_axis_country_tabs_fatalities(df):
    """
    Creates a Bokeh plot with tabs for each country, showing dual-axis plots
    with fatalities on left axis and download speed on right axis.
    """
    
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Get unique countries
    countries = df['country'].unique()
    
    tab_panels = []
    
    for country in countries:
        # Filter data for this country
        country_data = df[df['country'] == country].sort_values('date')
        
        if country_data.empty:
            continue
            
        # Create figure with left y-axis for fatalities
        p = figure(
            title=f"Fatalities vs Download Speed - {country}",
            x_axis_label='Date',
            y_axis_label='Number of Fatalities',
            x_axis_type='datetime',
            width=800,
            height=400,
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        # Plot fatalities on left axis (primary)
        fatalities_line = p.line(
            country_data['date'], 
            country_data['nrFatalities'],
            line_width=2,
            color='darkred',
            alpha=0.8,
            legend_label='Fatalities'
        )
        
        fatalities_circle = p.circle(
            country_data['date'],
            country_data['nrFatalities'],
            size=6,
            color='darkred',
            alpha=0.6
        )
        
        # Set up right y-axis for download speed
        download_min = country_data['download_speed'].min()
        download_max = country_data['download_speed'].max()
        download_range = download_max - download_min
        download_padding = download_range * 0.1
        
        # Create right y-axis
        p.extra_y_ranges = {
            "download": Range1d(
                start=download_min - download_padding,
                end=download_max + download_padding
            )
        }
        
        # Add right y-axis
        p.add_layout(
            LinearAxis(
                y_range_name="download",
                axis_label="Download Speed (Mbps)"
            ), 
            'right'
        )
        
        # Plot download speed on right axis
        download_line = p.line(
            country_data['date'],
            country_data['download_speed'],
            line_width=2,
            color='steelblue',
            alpha=0.8,
            y_range_name="download",
            legend_label='Download Speed'
        )
        
        download_circle = p.circle(
            country_data['date'],
            country_data['download_speed'],
            size=6,
            color='steelblue',
            alpha=0.6,
            y_range_name="download"
        )
        
        # Customize the plot
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
        p.title.text_font_size = "14pt"
        p.xaxis.axis_label_text_font_size = "12pt"
        p.yaxis.axis_label_text_font_size = "12pt"
        
        # Add grid
        p.grid.grid_line_alpha = 0.3
        
        # Create tab panel for this country
        tab_panel = TabPanel(child=p, title=country)
        tab_panels.append(tab_panel)
    
    # Create tabs widget
    tabs = Tabs(tabs=tab_panels)
    
    return tabs
