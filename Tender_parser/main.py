import os
import time

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from purchases_parsing import parser
from tender_db import data_base_creation
from fz223_db import creation as fz223db_creation

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


class EMAIL:
    email = "mycuuk@yandex.ru"
    password = "ysjpskeqemafnubg"
    smtp_server = "smtp.yandex.com"
    smtp_port = 465


def send_email_with_attachments(recipient_email, subject, body,
                                pdf_file_path, excel_file_path, retry_depth: int = 0) -> bool:
    if retry_depth == 10:
        return False

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = EMAIL.email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Add the body to the email
    message.attach(MIMEText(body, "plain"))

    # Attach PDF file
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_part = MIMEBase("application", "octet-stream")
        pdf_part.set_payload(pdf_file.read())
        encoders.encode_base64(pdf_part)
        pdf_part.add_header("Content-Disposition", f"attachment; filename= {pdf_file_path}")
        message.attach(pdf_part)

    # Attach Excel file
    with open(excel_file_path, "rb") as excel_file:
        excel_part = MIMEBase("application", "octet-stream")
        excel_part.set_payload(excel_file.read())
        encoders.encode_base64(excel_part)
        excel_part.add_header("Content-Disposition", f"attachment; filename= {excel_file_path}")
        message.attach(excel_part)

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL(f"{EMAIL.smtp_server}", EMAIL.smtp_port) as server:
            server.login(EMAIL.email, EMAIL.password)
            server.send_message(message)
    except:
        time.sleep(10)
        return send_email_with_attachments(recipient_email, subject, body, pdf_file_path, excel_file_path,
                                           retry_depth + 1)
    finally:
        return True


Base = declarative_base()


def create_engine_from_env():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_port = os.getenv('DB_PORT')


    if all([db_user, db_password, db_host, db_name, db_port]):
        connection_string = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        # Локальный dev-режим без Docker/MySQL: используем SQLite Django-проекта.
        sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api_django", "db.sqlite3"))
        connection_string = f"sqlite:///{sqlite_path}"

    return create_engine(connection_string)


class Order(Base):
    __tablename__ = 'api_order'

    id = Column(Integer, primary_key=True)
    request = Column(String)
    year_start = Column(Integer)
    year_end = Column(Integer)
    ktru_plots = Column(Integer)
    customers_plots = Column(Integer)
    regions_plots = Column(Integer)
    mnn_plots = Column(Integer)
    parse_data = Column(Integer)
    username = Column(String)
    email = Column(String)
    is_ready_id = Column(Integer)
    result_pdf = Column(String, default='')
    result_excel = Column(String, default='')


def select_task_by_priority(session, is_ready_id):
    return session.query(Order).filter(Order.is_ready_id == is_ready_id).first()


def switch_status(session, order, is_ready_id):
    order.is_ready_id = is_ready_id
    session.commit()


RESULTS_DIR = '/home/results'


def save_results(order_id, pdf_src, excel_src):
    """Копирует готовые файлы в общий том и возвращает имена файлов."""
    import shutil
    os.makedirs(RESULTS_DIR, exist_ok=True)
    pdf_name = f"{order_id}.pdf"
    excel_name = f"{order_id}.xlsx"
    shutil.copy2(pdf_src, os.path.join(RESULTS_DIR, pdf_name))
    shutil.copy2(excel_src, os.path.join(RESULTS_DIR, excel_name))
    return pdf_name, excel_name


def parsing_queue(engine):
    while True:
        Session = sessionmaker(bind=engine)
        s = Session()
        s.expire_all()

        order = select_task_by_priority(s, 1)

        if order:
            switch_status(s, order, 2)

            pdf_file_path, excel_file_path = parser.parse_all(
                order.id,
                order.request,
                int(order.year_start),
                int(order.year_end),
                int(order.ktru_plots),
                int(order.customers_plots),
                int(order.regions_plots),
                int(order.mnn_plots),
                1
            )

            # Сохраняем файлы в общий том — пользователь сможет скачать с сайта.
            try:
                pdf_name, excel_name = save_results(order.id, pdf_file_path, excel_file_path)
                order.result_pdf = pdf_name
                order.result_excel = excel_name
                s.commit()
                print(f"Results saved: {pdf_name}, {excel_name}")
            except Exception as e:
                print(f"Error saving results to shared volume: {e}")

            # Пробуем отправить письмо, но его провал не блокирует завершение заказа.
            try:
                send_email_with_attachments(
                    order.email,
                    subject="Выгрузка данных по государственным торгам",
                    body=f"Уважаемый, {order.username}, ваша выгрузка готова.\n\n"
                         f"Файлы также доступны для скачивания в личном кабинете на сайте.\n\n"
                         f"С уважением, Gosparsick!",
                    pdf_file_path=pdf_file_path,
                    excel_file_path=excel_file_path,
                )
            except Exception as e:
                print(f"Email send failed (files available for download on site): {e}")

            os.remove(pdf_file_path)
            os.remove(excel_file_path)

            if not int(os.getenv("DEBUG", "1")):
                print("Deleting data base")
                os.remove("RusTenderDataBase.db")
                os.remove("RusTenderDataBase223FZ.db")
                data_base_creation.db_initialise()
                fz223db_creation.db_initialise()

            switch_status(s, order, 3)

        s.close()
        time.sleep(5)


if __name__ == "__main__":
    data_base_creation.db_initialise()  # Создаем базу для хранения данных по торгам (RusTenderDataBase)
    fz223db_creation.db_initialise()
    e = create_engine_from_env()

    while True:
        parsing_queue(e)
