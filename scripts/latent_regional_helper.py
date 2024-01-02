import modules.scripts as scripts
import gradio as gr
import os

from modules import script_callbacks

def div_latent_couple(dropdown_row):
    # ドロップダウンリストの中で0以外の値を抽出する
    row_column = []
    for column in dropdown_row:
        if column != "0":
            row_column.append(column)
    
    # 入力された値の数に応じて分岐する
    if len(row_column) == 0:
        # 入力がない場合
        division = "none" 
        position = "none"
        weight = "none"
    else:
        # 2つ以上の値が入力されている場合
        division = ""
        position = ""
        weight = ""
        pos_row = 0
        pos_col = 0
        for col_num in row_column:
            for i in range(int(col_num)):
                division += str(len(row_column)) + ":" + str(col_num) + ","
                position += str(pos_row) + ":" + str(pos_col) + ","
                weight += "0.8,"
                pos_col += 1
            pos_col = 0
            pos_row += 1
        # 末尾のコロンを削除する
        division = division.rstrip(",")
        position = position.rstrip(",")
        weight = weight.rstrip(",")

    return division, position, weight


def div_regional_prompter(dropdown_row):
    # ドロップダウンリストの中で0以外の値を抽出する
    row_column = []
    for column in dropdown_row:
        if column != "0":
            row_column.append(column)
    
    # 入力された値の数に応じて分岐する
    if len(row_column) == 0:
        # 入力がない場合
        division = "none" 
    elif len(row_column) == 1:
        # 1つの値が入力されている場合
        division = "1," * int(row_column[0])
        division = division.rstrip(",")  # 末尾のカンマを削除する
    else:
        # 2つ以上の値が入力されている場合
        division = ""
        for col_num in row_column:
            col_str = "1" + (",1" * int(col_num))
            division += col_str + ";"
        division = division.rstrip(";")  # 末尾のセミコロンを削除する

    position = "none"
    weight = "none"

    return division, position, weight

def division_output(radio_sel, dd_row_1, dd_row_2, dd_row_3, dd_row_4, dd_row_5):
    # ドロップダウンリストをリストにまとめる
    dropdown_row = [dd_row_1, dd_row_2, dd_row_3, dd_row_4, dd_row_5]

    if radio_sel == "latent_couple":
        # latent_coupleの処理
        division, position, weight = div_latent_couple(dropdown_row)
    elif radio_sel == "regional_prompter":
        # regional_prompterの処理
        division, position, weight = div_regional_prompter(dropdown_row)
    else:
        pass

    return division, position, weight


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        gr.HTML(value='Latent Reagional Helper')
        with gr.Row():
            with gr.Column():  # Add a new column
                # UI画面の作成
                # 入力
                # 拡張機能洗濯用のラジオボタン
                radio_sel = gr.Radio(
                    ["latent_couple", "regional_prompter"],
                    label="Select latent_couple or regional_prompter",
                    value="latent_couple"  # デフォルト値を指定する
                )
                print(radio_sel)
                # テキストを表示
                gr.HTML(value='Divisions Settings')
                # Divisions Settingのドロップダウンリスト
                dropdown_row = []
                for i in range(5):
                    dropdown_row.append(gr.Dropdown(
                        ["0", "1", "2", "3", "4", "5"],
                        label=f"row{i+1} column num",
                        value="0"  # デフォルト値を指定する
                    ))
                # 実行ボタン
                button_run = gr.Button(value='run', variant='primary')

                # 出力
                # テキストボックス
                textbox_division = gr.Textbox(
                    label='Divisions Ratio',
                    interactive=True
                )
                with gr.Row():
                    textbox_position = gr.Textbox(
                        label='Position (Latent Only)',
                        interactive=True
                    )
                    textbox_weight = gr.Textbox(
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
                    dropdown_row[4]
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