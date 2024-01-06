import gradio as gr
from typing import List, Tuple
# import modules.scripts as scripts

from modules import script_callbacks

# ratioデフォルト値
default_div_ratio: float = 0.8
default_back_ratio: float = 0.2
# ratioの最小/最大値
ratio_sreshold_min: float = 0.0
ratio_sreshold_max: float = 1.0


def div_latent_couple(exist_col_num_list: List[str], div_ratio: float, back_ratio: float,
                      chkbox_back: bool) -> Tuple[str, str, str]:

    # 1つ以上入力がある場合
    division: str = ''
    position: str = ''
    weight: str = ''
    # 背景の設定がありの場合
    if chkbox_back is True:
        division += '1:1,'
        position += '0:0,'
        weight += str(clamp_ratio(back_ratio)) + ','
    # 分割領域の設定
    pos_row: int = 0
    pos_col: int = 0
    for col_num in exist_col_num_list:
        for _ in range(int(col_num)):
            division += str(len(exist_col_num_list)) + ':' + str(col_num) + ','
            position += str(pos_row) + ':' + str(pos_col) + ','
            weight += str(clamp_ratio(div_ratio)) + ','
            pos_col += 1
        pos_col = 0
        pos_row += 1
    # 末尾のコロンを削除
    division = division.rstrip(',')
    position = position.rstrip(',')
    weight = weight.rstrip(',')

    return division, position, weight


def clamp_ratio(ratio: float) -> float:
    return max(ratio_sreshold_min, min(ratio_sreshold_max, float(ratio)))


def div_regional_prompter(exist_col_num_list: List[str]) -> Tuple[str, str, str]:

    division: str = ''
    # 入力された値の数に応じて分岐する
    if len(exist_col_num_list) == 1:
        # 1つの値が入力されている場合
        division = '1,' * int(exist_col_num_list[0])
        division = division.rstrip(',')  # 末尾のカンマを削除する
    else:
        # 2つ以上の値が入力されている場合
        for col_num in exist_col_num_list:
            col_num_str = '1' + (',1' * int(col_num))
            division += col_num_str + ';'
        division = division.rstrip(';')  # 末尾のセミコロンを削除する

    position: str = '(Not used)'
    weight: str = '(Not used)'

    return division, position, weight


def division_output(radio_sel: str, col_num_1: str, col_num_2: str, col_num_3: str, col_num_4: str,
                    col_num_5: str, div_ratio: str, back_ratio: str,
                    chkbox_back: bool) -> Tuple[str, str, str]:
    # ドロップダウンリストをリストにまとめる
    col_num_list: List[str] = [col_num_1, col_num_2, col_num_3, col_num_4, col_num_5]

    # ドロップダウンリストの中で0以外の値を抽出する
    exist_col_num_list: List[str] = []
    for col_num in col_num_list:
        if col_num != '0':
            exist_col_num_list.append(col_num)

    if len(exist_col_num_list) == 0:
        # 入力がない場合
        division = '(No division settings)'
        position = '(No division settings)'
        weight = '(No division settings)'
    else:
        if radio_sel == 'Latent Couple':
            # 入力値のチェック
            try:
                div_ratio_f = float(div_ratio)
            except ValueError:
                div_ratio_f = default_div_ratio
            try:
                back_ratio_f = float(back_ratio)
            except ValueError:
                back_ratio_f = default_back_ratio
            # Latent Coupleの処理
            division, position, weight = div_latent_couple(exist_col_num_list, div_ratio_f,
                                                           back_ratio_f, chkbox_back)
        elif radio_sel == 'Regional Prompter':
            # Regional Prompterの処理
            division, position, weight = div_regional_prompter(exist_col_num_list)
        else:
            # エラー処理: 不正な選択がされた場合
            division = '(Latent selection error)'
            position = '(Latent selection error)'
            weight = '(Latent selection error)'

    return division, position, weight


def on_ui_tabs() -> List[Tuple[gr.Blocks, str, str]]:
    with gr.Blocks(analytics_enabled=False) as ui_component:
        gr.HTML(value='Latent Regional Helper')
        with gr.Row():
            with gr.Column():  # Add a new column
                # UI画面の作成
                # 入力
                # 拡張機能洗濯用のラジオボタン
                radio_sel: gr.Radio = gr.Radio(
                    ['Latent Couple', 'Regional Prompter'],
                    label='Select \'Latent Couple\' or \'Regional Prompter\'',
                    value='Latent Couple'  # デフォルト値を指定する
                )
                # テキストを表示
                gr.HTML(value='Divisions Settings')
                # Divisions Settingのドロップダウンリスト
                dropdown_col_num_list: List[gr.Dropdown] = []
                for i in range(5):
                    dropdown_col_num_list.append(
                        gr.Dropdown(
                            ['0', '1', '2', '3', '4', '5'],
                            label=f'row{i+1} column num',
                            value='0'  # デフォルト値を指定する
                        ))

                # テキストを表示
                gr.HTML(value='Ratio and Background Settings')
                with gr.Row():
                    textbox_div_ratio: gr.Textbox = gr.Textbox(
                        label='Divisions Ratio (Latent Only)',
                        interactive=True,
                        value=str(default_div_ratio))

                    textbox_back_ratio: gr.Textbox = gr.Textbox(
                        label='Background Ratio (Latent Only)',
                        interactive=True,
                        value=str(default_back_ratio))

                    chkbox_back: gr.Checkbox = gr.Checkbox(label='Background Enable (Latent Only)',
                                                           value=False)

                # 実行ボタン
                button_run: gr.Button = gr.Button(value='run', variant='primary')

                # 出力
                # テキストボックス
                textbox_division: gr.Textbox = gr.Textbox(label='Divisions Ratio', interactive=True)
                with gr.Row():
                    textbox_position: gr.Textbox = gr.Textbox(label='Position (Latent Only)',
                                                              interactive=True)
                    textbox_weight: gr.Textbox = gr.Textbox(label='Weight (Latent Only)',
                                                            interactive=True)
            with gr.Column():  # Add a new column
                pass

            # button_run 押したときの処理
            button_run.click(
                # button_run ボタンを押したときに実行される関数
                fn=division_output,
                # division_output 関数の引数
                # NOTE: column_num_row_listはリスト型で渡すことができない。
                #       gradioブロック型のオブジェクトで渡す必要がある。
                inputs=[
                    radio_sel, dropdown_col_num_list[0], dropdown_col_num_list[1],
                    dropdown_col_num_list[2], dropdown_col_num_list[3], dropdown_col_num_list[4],
                    textbox_div_ratio, textbox_back_ratio, chkbox_back
                ],
                # division_output 関数の戻り値
                outputs=[textbox_division, textbox_position, textbox_weight])

        return [(ui_component, 'LR Helper', 'lr_helper_tab')]


script_callbacks.on_ui_tabs(on_ui_tabs)
