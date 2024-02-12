"""Script that defines the UI and processing for Latent Regional Helper."""
from typing import List, Tuple

# NOTE: gradio is available in the StableDiffusion environment (no separate installation required)
import gradio as gr

from modules import generation_parameters_copypaste as params_copypaste
from modules import script_callbacks

# import modules.scripts as scripts

# Default values for weight
default_div_weight: float = 0.8
default_back_weight: float = 0.2
# Minimum/maximum values for weight
weight_threshold_min: float = 0.0
weight_threshold_max: float = 1.0


def div_latent_couple(exist_col_num_list: List[str], div_weight: float, back_weight: float,
                      chkbox_back: bool) -> Tuple[str, str, str, str]:
    """
    Create division parameters for Latent Couple.

    Args:
        exist_col_num_list (List[str]): List of column numbers for existing divisions.
        div_weight (float): weight for divided regions setting.
        back_weight (float): weight for the background setting.
        chkbox_back (bool): Flag indicating whether the background setting is enabled.

    Returns:
        Tuple[str, str, str, str]: A tuple containing the division, position, weight, and prompt.
    """
    division: str = ''
    position: str = ''
    weight: str = ''
    prompt: str = ''
    # If background setting is enabled
    if chkbox_back is True:
        division += '1:1,'
        position += '0:0,'
        weight += str(clamp_value(back_weight, weight_threshold_min, weight_threshold_max)) + ','
        prompt += '\nAND '
    else:
        pass
    # Setting for divided regions
    pos_row: int = 0
    pos_col: int = 0
    for col_num in exist_col_num_list:
        for _ in range(int(col_num)):
            # Add division, position, and weight
            division += str(len(exist_col_num_list)) + ':' + str(col_num) + ','
            position += str(pos_row) + ':' + str(pos_col) + ','
            weight += str(clamp_value(div_weight, weight_threshold_min, weight_threshold_max)) + ','
            pos_col += 1
        # Add prompt
        prompt += '\nAND ' * (int(col_num) - 1)  # Add AND for each column
        prompt += '\nAND '  # Add AND for each row
        pos_col = 0
        pos_row += 1
    # remove trailing commas and AND
    division = division.rstrip(',')
    position = position.rstrip(',')
    weight = weight.rstrip(',')
    prompt = prompt[:prompt.rfind('\nAND ')]  # Remove last occurrence of '\nAND '

    return division, position, weight, prompt


def div_regional_prompter(exist_col_num_list: List[str], chkbox_base_prompt: bool,
                          chkbox_common_prompt: bool) -> Tuple[str, str, str, str]:
    """
    Generate division, position, weight, and prompt based on the given parameters.

    Args:
        exist_col_num_list (List[str]): A list of column numbers.
        chkbox_base_prompt (bool): A boolean indicating whether the base prompt checkbox is checked.
        chkbox_common_prompt (bool):
            A boolean indicating whether the common prompt checkbox is checked.

    Returns:
        Tuple[str, str, str, str]: A tuple containing the division, position, weight, and prompt.

    """
    division: str = ''
    prompt: str = ''

    # Add base and common prompt settings
    if chkbox_common_prompt:
        prompt += ' ADDCOMM\n'
    if chkbox_base_prompt:
        prompt += ' ADDBASE\n'

    # Add division settings
    if len(exist_col_num_list) >= 1:
        for col_num in exist_col_num_list:
            # Add division settings
            division += '1' + (',1' * int(col_num))
            division += ';'
            # Add prompt settings
            prompt += ' ADDCOL\n' * (int(col_num) - 1)
            prompt += ' ADDROW\n'
        # Remove trailing semicolons and ADDROW
        division = division.rstrip(';')  # Remove trailing semicolons
        prompt = prompt[:prompt.rfind(' ADDROW\n')]  # Remove last occurrence of ' ADDROW\n'
    else:
        division = '(Not used)'
        prompt = '(Not used)'

    position: str = '(Not used)'
    weight: str = '(Not used)'

    return division, position, weight, prompt


def division_output(radio_sel: str, col_num_1: str, col_num_2: str, col_num_3: str, col_num_4: str,
                    col_num_5: str, div_weight: str, back_weight: str, chkbox_back: bool,
                    chkbox_base_prompt: bool,
                    chkbox_common_prompt: bool) -> Tuple[str, str, str, str]:
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
        Tuple[str, str, str]: A tuple containing the division, position, weight and prompt.
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
        prompt = '(No divisions settings)'
    else:
        if radio_sel == 'Latent Couple':
            # Parse weight values
            div_weight_f = parse_float(div_weight, default_div_weight)
            back_weight_f = parse_float(back_weight, default_back_weight)
            # Process for Latent Couple
            division, position, weight, prompt = div_latent_couple(exist_col_num_list, div_weight_f,
                                                                   back_weight_f, chkbox_back)
        elif radio_sel == 'Regional Prompter':
            # Process for Regional Prompter
            division, position, weight, prompt = div_regional_prompter(
                exist_col_num_list, chkbox_base_prompt, chkbox_common_prompt)
        else:
            # Error handling: If an invalid selection is made
            division = '(Latent selection error)'
            position = '(Latent selection error)'
            weight = '(Latent selection error)'
            prompt = '(Latent selection error)'

    return division, position, weight, prompt


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
        with gr.Column():
            # Input
            gr.HTML(value='Common Settings')
            # Radio buttons for extension selection
            radio_sel: gr.Radio = gr.Radio(
                ['Latent Couple', 'Regional Prompter'],
                label='Select output format \'Latent Couple\' or \'Regional Prompter\'',
                value='Latent Couple'  # Specify default value
            )
            # Dropdown list for Divisions Setting
            gr.HTML(value='Divisions')
            dropdown_col_num_list: List[gr.Dropdown] = []
            for i in range(5):
                dropdown_col_num_list.append(
                    gr.Dropdown(
                        ['0', '1', '2', '3', '4', '5'],
                        label=f'row{i+1} column num',
                        value='0'  # Specify default value
                    ))
            gr.HTML(value='Individual Settings')
            with gr.Row():
                with gr.Column(variant='panel'):  # Add a new column
                    gr.HTML(value='Latent Couple Settings')
                    gr.HTML(value='Weight and Background')
                    with gr.Row():
                        textbox_div_weight: gr.Textbox = gr.Textbox(label='Divisions Weight',
                                                                    interactive=True,
                                                                    value=str(default_div_weight))
                        textbox_back_weight: gr.Textbox = gr.Textbox(label='Background Weight',
                                                                     interactive=True,
                                                                     value=str(default_back_weight))
                        chkbox_back: gr.Checkbox = gr.Checkbox(label='Enable Background',
                                                               value=False)
                with gr.Column(variant='panel'):  # Add a new column
                    gr.HTML(value='Regional Prompter Settings')
                    gr.HTML(value='Base and Common Prompt Settings')
                    with gr.Row():
                        # Checkbox for Use base prompt
                        chkbox_base_prompt: gr.Checkbox = gr.Checkbox(label='Use base prompt',
                                                                      value=False)

                        # Checkbox for Use common prompt
                        chkbox_common_prompt: gr.Checkbox = gr.Checkbox(label='Use common prompt',
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
            # Textbox for prompt template output
            textbox_prompt_output: gr.Textbox = gr.Textbox(label='Prompt Template',
                                                           interactive=True)
            # Button to copy the contents of prompt_output to txt2img and img2img
            gr.HTML(value='Send to Prompt Template to txt2img or img2img')
            with gr.Row():
                buttons = params_copypaste.create_buttons(['txt2img', 'img2img'])
            params_copypaste.bind_buttons(buttons, None, textbox_prompt_output)

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
                    textbox_div_weight, textbox_back_weight, chkbox_back, chkbox_base_prompt,
                    chkbox_common_prompt
                ],
                # Return values of the division_output function
                outputs=[textbox_division, textbox_position, textbox_weight, textbox_prompt_output])

        return [(ui_component, 'LR Helper', 'lr_helper_tab')]


script_callbacks.on_ui_tabs(on_ui_tabs)
