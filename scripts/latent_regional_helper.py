"""Script that defines the UI and processing for Latent Regional Helper."""
from typing import List, Tuple

# NOTE: gradio is available in the StableDiffusion environment (no separate installation required)
import gradio as gr

from modules import script_callbacks

# import modules.scripts as scripts

# Default values for weight
default_div_weight: float = 0.8
default_back_weight: float = 0.2
# Minimum/maximum values for weight
weight_threshold_min: float = 0.0
weight_threshold_max: float = 1.0


def div_latent_couple(exist_col_num_list: List[str], div_weight: float, back_weight: float,
                      chkbox_back: bool) -> Tuple[str, str, str]:
    """
    Create division parameters for Latent Couple.

    Args:
        exist_col_num_list (List[str]): List of column numbers for existing divisions.
        div_weight (float): weight for divided regions setting.
        back_weight (float): weight for the background setting.
        chkbox_back (bool): Flag indicating whether the background setting is enabled.

    Returns:
        Tuple[str, str, str]: A tuple containing the division, position, and weight.
    """
    division: str = ''
    position: str = ''
    weight: str = ''
    # If background setting is enabled
    if chkbox_back is True:
        division += '1:1,'
        position += '0:0,'
        weight += str(clamp_value(back_weight, weight_threshold_min, weight_threshold_max)) + ','
    else:
        pass
    # Setting for divided regions
    pos_row: int = 0
    pos_col: int = 0
    for col_num in exist_col_num_list:
        for _ in range(int(col_num)):
            division += str(len(exist_col_num_list)) + ':' + str(col_num) + ','
            position += str(pos_row) + ':' + str(pos_col) + ','
            weight += str(clamp_value(div_weight, weight_threshold_min, weight_threshold_max)) + ','
            pos_col += 1
        pos_col = 0
        pos_row += 1
    # Remove trailing commas
    division = division.rstrip(',')
    position = position.rstrip(',')
    weight = weight.rstrip(',')

    return division, position, weight


def div_regional_prompter(exist_col_num_list: List[str]) -> Tuple[str, str, str]:
    """
    Create division parameters for Regional Prompter.

    Args:
        exist_col_num_list (List[str]): List of column numbers for existing divisions.

    Returns:
        Tuple[str, str, str]: A tuple containing the division, position, and weight.
    """
    division: str = ''
    if len(exist_col_num_list) == 1:
        # If only one value is input
        division = '1,' * int(exist_col_num_list[0])
        division = division.rstrip(',')  # Remove trailing commas
    elif len(exist_col_num_list) >= 2:
        # If two or more values are input
        for col_num in exist_col_num_list:
            col_num_str = '1' + (',1' * int(col_num))
            division += col_num_str + ';'
        division = division.rstrip(';')  # Remove trailing semicolons
    else:
        # If there is no input (However, it has been checked in the calling function)
        division = '(Not used)'

    position: str = '(Not used)'
    weight: str = '(Not used)'

    return division, position, weight


def division_output(radio_sel: str, col_num_1: str, col_num_2: str, col_num_3: str, col_num_4: str,
                    col_num_5: str, div_weight: str, back_weight: str,
                    chkbox_back: bool) -> Tuple[str, str, str]:
    """
    Create division parameters.

    Args:
        radio_sel (str): The selected radio button value.
        col_num_1 (str): The column number for row 1.
        col_num_2 (str): The column number for row 2.
        col_num_3 (str): The column number for row 3.
        col_num_4 (str): The column number for row 4.
        col_num_5 (str): The column number for row 5.
        div_weight (str): The division weight.
        back_weight (str): The background weight.
        chkbox_back (bool): Flag indicating whether the background setting is enabled.

    Returns:
        Tuple[str, str, str]: A tuple containing the division, position, and weight.
    """
    # Combine dropdown list into a list
    col_num_list: List[str] = [col_num_1, col_num_2, col_num_3, col_num_4, col_num_5]

    # Extract non-zero and non-empty values from the dropdown list
    exist_col_num_list: List[str] = []
    for col_num in col_num_list:
        if isinstance(col_num, str) and col_num != '0' and col_num != '':
            exist_col_num_list.append(col_num)

    if len(exist_col_num_list) == 0:
        # If there is no input
        division = '(No divisions settings)'
        position = '(No divisions settings)'
        weight = '(No divisions settings)'
    else:
        if radio_sel == 'Latent Couple':
            # Parse weight values
            div_weight_f = parse_float(div_weight, default_div_weight)
            back_weight_f = parse_float(back_weight, default_back_weight)
            # Process for Latent Couple
            division, position, weight = div_latent_couple(exist_col_num_list, div_weight_f,
                                                           back_weight_f, chkbox_back)
        elif radio_sel == 'Regional Prompter':
            # Process for Regional Prompter
            division, position, weight = div_regional_prompter(exist_col_num_list)
        else:
            # Error handling: If an invalid selection is made
            division = '(Latent selection error)'
            position = '(Latent selection error)'
            weight = '(Latent selection error)'

    return division, position, weight


def parse_float(value: str, default_value: float) -> float:
    """
    Parse a string value to float.

    Args:
        value (str): The value to be parsed.
        default_value (float): The default value to be returned if parsing fails.

    Returns:
        float: The parsed float value or the default value.
    """
    try:
        return float(value)
    except ValueError:
        return default_value


def clamp_value(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between a minimum and maximum value.

    Args:
        value (float): The value to be clamped.
        min_value (float): The minimum value.
        max_value (float): The maximum value.

    Returns:
        float: The clamped value.
    """
    return max(min_value, min(max_value, float(value)))


def on_ui_tabs() -> List[Tuple[gr.Blocks, str, str]]:
    """
    Define the UI components and their behavior.

    Returns:
        List[Tuple[gr.Blocks, str, str]]: A list of tuples containing the UI components,
                                          tab name, and tab ID.
    """
    # Create UI screen
    with gr.Blocks(analytics_enabled=False) as ui_component:
        gr.HTML(value='Latent Regional Helper')
        gr.HTML(value='Input')
        with gr.Row():
            with gr.Column():  # Add a new column
                # Input
                # Radio buttons for extension selection
                radio_sel: gr.Radio = gr.Radio(
                    ['Latent Couple', 'Regional Prompter'],
                    label='Select output format \'Latent Couple\' or \'Regional Prompter\'',
                    value='Latent Couple'  # Specify default value
                )
                # Dropdown list for Divisions Setting
                gr.HTML(value='Divisions Settings')
                dropdown_col_num_list: List[gr.Dropdown] = []
                for i in range(5):
                    dropdown_col_num_list.append(
                        gr.Dropdown(
                            ['0', '1', '2', '3', '4', '5'],
                            label=f'row{i+1} column num',
                            value='0'  # Specify default value
                        ))

                # weight and Background Settings
                gr.HTML(value='Weight and Background Settings')
                with gr.Row():
                    textbox_div_weight: gr.Textbox = gr.Textbox(
                        label='Divisions Weight (Latent Only)',
                        interactive=True,
                        value=str(default_div_weight))

                    textbox_back_weight: gr.Textbox = gr.Textbox(
                        label='Background Weight (Latent Only)',
                        interactive=True,
                        value=str(default_back_weight))

                    chkbox_back: gr.Checkbox = gr.Checkbox(label='Background Enable (Latent Only)',
                                                           value=False)

                # Run button
                button_execute: gr.Button = gr.Button(value='execute', variant='primary')

                # Output
                gr.HTML(value='Output')
                # Textbox for output
                textbox_division: gr.Textbox = gr.Textbox(label='Divisions Ratio', interactive=True)
                with gr.Row():
                    textbox_weight: gr.Textbox = gr.Textbox(label='Weight (Latent Only)',
                                                            interactive=True)
                    textbox_position: gr.Textbox = gr.Textbox(label='Position (Latent Only)',
                                                              interactive=True)
            with gr.Column():  # Add a new column
                pass

            # Processing when button_execute is clicked
            button_execute.click(
                # Function to be executed when button_execute is clicked
                fn=division_output,
                # Arguments for the division_output function
                # NOTE: column_num_row_list cannot be passed as a list.
                #       It needs to be passed as a gradio block object.
                inputs=[
                    radio_sel, dropdown_col_num_list[0], dropdown_col_num_list[1],
                    dropdown_col_num_list[2], dropdown_col_num_list[3], dropdown_col_num_list[4],
                    textbox_div_weight, textbox_back_weight, chkbox_back
                ],
                # Return values of the division_output function
                outputs=[textbox_division, textbox_position, textbox_weight])

        return [(ui_component, 'LR Helper', 'lr_helper_tab')]


script_callbacks.on_ui_tabs(on_ui_tabs)
