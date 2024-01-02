import modules.scripts as scripts
import gradio as gr
import os
from typing import List, Tuple, Union

from modules import script_callbacks


def div_latent_couple(dropdown_row: List[str], div_ratio: float, back_ratio: float, chkbox_back: bool) -> Tuple[str, str, str]:
    # ドロップダウンリストの中で0以外の値を抽出する
    row_column: List[str] = []
    for column in dropdown_row:
        if column != "0":
            row_column.append(column)
    
    # 入力された値の数に応じて分岐する
    if len(row_column) == 0:
        # 入力がない場合
        division: str = "none" 
        position: str = "none"
        weight: str = "none"
    else:
        # 1つ以上入力がある場合
        division: str = ""
        position: str = ""
        weight: str = ""
        # 背景の設定がありの場合
        if chkbox_back is True:
            division += "1:1,"
            position += "0:0,"
            weight += str(clamp_ratio(back_ratio)) + ","
        # 分割領域の設定
        pos_row: int = 0
        pos_col: int = 0
        for col_num in row_column:
            for i in range(int(col_num)):
                division += str(len(row_column)) + ":" + str(col_num) + ","
                position += str(pos_row) + ":" + str(pos_col) + ","
                weight += str(clamp_ratio(div_ratio)) + ","
                pos_col += 1
            pos_col = 0
            pos_row += 1
        # 末尾のコロンを削除
        division = division.rstrip(",")
        position = position.rstrip(",")
        weight = weight.rstrip(",")

    return division, position, weight

def clamp_ratio(ratio: float) -> float:
    return max(0.0, min(1.0, float(ratio)))

def div_regional_prompter(dropdown_row: List[str]) -> Tuple[str, str, str]:
    # ドロップダウンリストの中で0以外の値を抽出する
    row_column: List[str] = []
    for column in dropdown_row:
        if column != "0":
            row_column.append(column)
    
    # 入力された値の数に応じて分岐する
    if len(row_column) == 0:
        # 入力がない場合
        division: str = "none" 
    elif len(row_column) == 1:
        # 1つの値が入力されている場合
        division = "1," * int(row_column[0])
        division = division.rstrip(",")  # 末尾のカンマを削除する
    else:
        # 2つ以上の値が入力されている場合
        division: str = ""
        for col_num in row_column:
            col_str = "1" + (",1" * int(col_num))
            division += col_str + ";"
        division = division.rstrip(";")  # 末尾のセミコロンを削除する

    position: str = "none"
    weight: str = "none"

    return division, position, weight

def division_output(radio_sel: str, dd_row_1: str, dd_row_2: str, dd_row_3: str, dd_row_4: str, dd_row_5: str, div_ratio: float, back_ratio: float, chkbox_back: bool) -> Tuple[str, str, str]:
    # ドロップダウンリストをリストにまとめる
    dropdown_row: List[str] = [dd_row_1, dd_row_2, dd_row_3, dd_row_4, dd_row_5]

    if radio_sel == "latent_couple":
        # latent_coupleの処理
        division, position, weight = div_latent_couple(dropdown_row, div_ratio, back_ratio, chkbox_back)
    elif radio_sel == "regional_prompter":
        # regional_prompterの処理
        division, position, weight = div_regional_prompter(dropdown_row)
    else:
        pass

    return division, position, weight


def on_ui_tabs() -> List[Tuple[gr.Blocks, str, str]]:
    with gr.Blocks(analytics_enabled=False) as ui_component:
        gr.HTML(value='Latent Reagional Helper')
        with gr.Row():
            with gr.Column():  # Add a new column
                # UI画面の作成
                # 入力
                # 拡張機能洗濯用のラジオボタン
                radio_sel: gr.Radio = gr.Radio(
                    ["latent_couple", "regional_prompter"],
                    label="Select latent_couple or regional_prompter",
                    value="latent_couple"  # デフォルト値を指定する
                )
                print(radio_sel)
                # テキストを表示
                gr.HTML(value='Divisions Settings')
                # Divisions Settingのドロップダウンリスト
                dropdown_row: List[gr.Dropdown] = []
                for i in range(5):
                    dropdown_row.append(gr.Dropdown(
                        ["0", "1", "2", "3", "4", "5"],
                        label=f"row{i+1} column num",
                        value="0"  # デフォルト値を指定する
                    ))
                
                with gr.Row():
                    textbox_div_ratio: gr.Textbox = gr.Textbox(
                        label='Divisions Ratio (Latent Only)',
                        interactive=True,
                        value = 0.8
                    )
    
                    textbox_back_ratio: gr.Textbox = gr.Textbox(
                        label='Background Ratio (Latent Only)',
                        interactive=True,
                        value = 0.2
                    )

                    chkbox_back: gr.Checkbox = gr.Checkbox(
                        label="Background Enable (Latent Only)",
                        value=False
                    )

                # 実行ボタン
                button_run: gr.Button = gr.Button(value='run', variant='primary')

                # 出力
                # テキストボックス
                textbox_division: gr.Textbox = gr.Textbox(
                    label='Divisions Ratio',
                    interactive=True
                )
                with gr.Row():
                    textbox_position: gr.Textbox = gr.Textbox(
                        label='Position (Latent Only)',
                        interactive=True
                    )
                    textbox_weight: gr.Textbox = gr.Textbox(
                        label='Weight (Latent Only)',
                        interactive=True
                    )
            with gr.Column():  # Add a new column
                pass

            # btn_run 押したときの処理
            button_run.click(
                # btn_run ボタンを押したときに実行される関数
                fn=division_output,
                # add_str 関数の引数
                # NOTE: dropdown_rowはリスト型で渡すことができない。
                #       gradioブロック型のオブジェクトで渡す必要がある。
                inputs=[
                    radio_sel,
                    dropdown_row[0],
                    dropdown_row[1],
                    dropdown_row[2],
                    dropdown_row[3],
                    dropdown_row[4],
                    textbox_div_ratio,
                    textbox_back_ratio,
                    chkbox_back
                ],
                # add_str 関数の戻り値
                outputs=[
                    textbox_division,
                    textbox_position,
                    textbox_weight
                ]
            )

        return [(ui_component, "LR Helper", "lr_helper_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)