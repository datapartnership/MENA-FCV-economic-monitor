import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_conflict_metrics_by_country(
    data: pd.DataFrame,
    metrics_to_plot: list,
    metric_display_info: dict = None,
    sorting_metric: str = None,
    overall_title: str = 'Comparison of Metrics by Country',
    source_text: str = None,
    figsize: tuple = (15, 8)
) -> plt.Figure:
    """
    Generates a horizontally concatenated bar chart for specified metrics by country,
    with text labels for values using matplotlib.

    Args:
        data (pd.DataFrame): The input DataFrame containing 'country' and metric columns.
        metrics_to_plot (list): A list of column names (metrics) to visualize.
        metric_display_info (dict, optional): A dictionary mapping metric names to
            dictionaries with 'title' and 'color' keys.
        sorting_metric (str, optional): The name of the metric to use for sorting.
        overall_title (str, optional): The main title for the concatenated chart.
        source_text (str, optional): Text to be displayed as a subtitle.
        figsize (tuple, optional): Figure size (width, height). Defaults to (15, 8).

    Returns:
        plt.Figure: A matplotlib Figure object.
    """
    
    if metric_display_info is None:
        metric_display_info = {}

    # Sort the data if a sorting_metric is provided
    if sorting_metric and sorting_metric in data.columns:
        if pd.api.types.is_numeric_dtype(data[sorting_metric]):
            data_sorted = data.sort_values(by=sorting_metric, ascending=True).reset_index(drop=True)
            print(f"Sorting countries by '{sorting_metric}' in ascending order.")
        else:
            data_sorted = data.copy()
            print(f"Warning: Sorting metric '{sorting_metric}' is not numeric.")
    else:
        data_sorted = data.copy()
        if sorting_metric:
            print(f"Warning: Sorting metric '{sorting_metric}' not found.")

    # Filter valid metrics
    valid_metrics = [m for m in metrics_to_plot if m in data_sorted.columns]
    if not valid_metrics:
        print("No valid metrics found in the DataFrame.")
        return None

    n_metrics = len(valid_metrics)
    
    # Create figure and subplots
    fig, axes = plt.subplots(1, n_metrics, figsize=figsize, sharey=True)
    
    # Handle single subplot case
    if n_metrics == 1:
        axes = [axes]
    
    # Set overall style
    plt.style.use('default')
    fig.patch.set_facecolor('white')
    
    countries = data_sorted['country'].values
    y_pos = np.arange(len(countries))
    
    for i, metric in enumerate(valid_metrics):
        ax = axes[i]
        
        # Get custom title and color, or use defaults
        display_info = metric_display_info.get(metric, {})
        metric_title = display_info.get('title', metric)
        metric_color = display_info.get('color', '#1f77b4')  # Default blue
        
        values = data_sorted[metric].values
        
        # Create horizontal bar chart
        bars = ax.barh(y_pos, values, color=metric_color, alpha=0.8, 
                       edgecolor='white', linewidth=0.5)
        
        # Add value labels on bars
        for j, (bar, value) in enumerate(zip(bars, values)):
            width = bar.get_width()
            # Position text slightly to the right of bar end
            ax.text(width + max(values) * 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{int(value):,}', ha='left', va='center', fontsize=9, 
                    fontweight='bold', color='black')
        
        # Customize subplot
        ax.set_yticks(y_pos)
        ax.set_xlabel(f'Number of {metric_title}', fontsize=11, fontweight='bold')
        ax.set_title(f'{metric_title} by Country', fontsize=12, fontweight='bold', pad=15)
        
        # # Only show y-axis labels on leftmost subplot
        # if i > 0:
        #     ax.set_yticklabels([])
        # else:
        #     ax.set_yticklabels(countries, fontsize=10)
        #     ax.set_ylabel('Country', fontsize=11, fontweight='bold')
        
        # Style the subplot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#CCCCCC')
        ax.spines['bottom'].set_color('#CCCCCC')
        ax.tick_params(colors='#666666')
        ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set x-axis to start from 0 and add some padding
        ax.set_xlim(0, max(values) * 1.15)
    
    # Add overall title
    fig.suptitle(overall_title, fontsize=16, fontweight='bold', y=0.95)
    
    # Add source text as subtitle
    if source_text:
        fig.text(0.5, 0.02, source_text, ha='center', va='bottom', 
                 fontsize=9, style='italic', color='#666666')
    
    # Adjust layout
    plt.tight_layout()
    # Ensure enough space for y-axis labels on the left
    plt.subplots_adjust(left=0.15, top=0.88, bottom=0.1 if source_text else 0.05)
    
    return fig