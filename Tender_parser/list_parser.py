from purchases_parsing import parser
from tender_db import data_base_creation
from fz223_db import creation as fz223_creation

import os
import time
import shutil

import pandas as pd
import argparse

import main


def process_csv(file_name: str, archive_folder: str):
    year_start = 2022
    year_end = 2022
    df = pd.read_csv(file_name)

    if 'ready' not in df.columns:
        df['ready'] = 0
        df.to_csv(file_name, index=False)

    continue_processing = True

    while continue_processing:
        df = pd.read_csv(file_name)
        continue_processing = False

        for index, row in df.iterrows():
            ready = row['ready']
            if ready == 0:
                data_base_creation.db_initialise()
                fz223_creation.db_initialise()

                text = row['medication']

                pdf_file_path, excel_file_path = parser.parse_all(
                    text,
                    text,
                    year_start,
                    year_end,
                    0, 0, 0, 0, 1
                )

                # Копируем excel файл в архивную папку
                if os.path.exists(excel_file_path):
                    shutil.copy(excel_file_path, archive_folder)

                df.at[index, 'ready'] = 1

                df.to_csv(file_name, index=False)

                os.remove(pdf_file_path)
                os.remove(excel_file_path)
                os.remove("RusTenderDataBase.db")
                os.remove("RusTenderDataBase223FZ.db")

                continue_processing = True
                break


def start():
    argparser = argparse.ArgumentParser(description="Process a CSV file and run a parser function.")
    argparser.add_argument('--data-file', default='order_data.csv', help='Path to the CSV file')
    args = argparser.parse_args()

    # Замените 'your_parser_object' на объект вашего парсера.
    process_csv(args.data_file, "./proceeded_data")

    shutil.make_archive("list_data", 'zip', "./proceeded_data")

    res = False
    while not res:
        res = main.send_email_with_attachments("mycuuuk@gmail.com",
                                      subject="Выгрузка данных по государственным торгам",
                                      body=f"Уважаемый, повелитель ваша выгрузка готова, результаты "
                                           f"приложены к "
                                           f"письму. \n\n Надеемся на дальнейшее сотрудничество! \n"
                                           f"С уважением, Gosparsick!",
                                      pdf_file_path="list_data.zip",
                                      excel_file_path=args.data_file)
                                      
        time.sleep(1000000000)


if __name__ == "__main__":
    start()
