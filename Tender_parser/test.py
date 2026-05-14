import main
from tender_db import data_base_creation
from fz223_db import creation as fz223_creation

data_base_creation.db_initialise()
fz223_creation.db_initialise()

pdf_file_path, excel_file_path = main.parser.parse_all(
                '1',
                'зопиклон',
                2022,
                2024,
                1,
                1,
                1,
                1,
                0
            )
