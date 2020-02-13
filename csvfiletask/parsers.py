import pandas as pd
from .models import Invoice, Customer, File
from django.db import transaction
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class FileParser:
    def __init__(self, upload):
        self.upload = upload
        self.clear_results()

    def __get_header(self):
        header = ['ContactName', 'InvoiceNumber', 'InvoiceDate', 'DueDate', 'Description', 'Quantity', 'UnitAmount']
        return header

    def __parse_header(self):
        '''
        Parsing the header of the file
        '''
        logger.info('Parsing header')
        try:
            self.clear_results()
            self.upload.status = File.STARTED
            self.upload.save()
            file_data = pd.read_csv(self.upload.file.path, nrows=1).columns
            header_rows = self.__get_header()
            for row in header_rows:
                if row not in file_data:
                    message = u'{row} missing in header'.format(row=row)
                    self.add_error('header', message, 0)
            if len(self.errors) > 0:
                self.upload.status = File.FAILED
                self.upload.validation_results = u'{}'.format(self.errors)
                self.upload.save()
                return False
            else:
                return True
        except Exception as ex:
            logger.exception('Parsers:Exception in parsing header %s', str(ex))
            return

    def parse(self):
        '''
        Parse function to parse the body of the file
        '''
        logger.info('Parsers:File body Parsing initiated')
        if self.__parse_header():
            file_data = pd.read_csv(self.upload.file.path, sep=",")
            row_iter = file_data.iterrows()
            for index, row in row_iter:
                # only commit non empty rows for compulsory header #
                if not pd.isna(row['ContactName']) and not pd.isna(row['InvoiceNumber']) \
                        and not pd.isna(row['InvoiceDate']) and not pd.isna(row['DueDate']) \
                        and not pd.isna(row['Description']) and not pd.isna(row['Quantity']) \
                        and not pd.isna(row['UnitAmount']):
                    customer, _ = Customer.objects.get_or_create(name=row['ContactName'])
                    objs = [
                        Invoice(

                            file=self.upload,
                            customer=customer,
                            number=row['InvoiceNumber'],
                            date=row['InvoiceDate'],
                            due_date=row['DueDate'],
                            description=row['Description'],
                            quantity=row['Quantity'],
                            unit_amount=row['UnitAmount']
                        )
                    ]
                    try:
                        with transaction.atomic():
                            Invoice.objects.bulk_create(objs)
                    except Exception as ex:
                        logging.exception('Parsers:Exception while committing records %s', str(ex))
                        self.upload.status = File.IN_PROGRESS
                        self.upload.append_validation_result(u'FileParser', u'{}{}'.format(ex,'\n'))
                        self.upload.save()
                        continue
            self.upload.status = File.COMPLETED
            self.upload.save()
            return True
        else:
            self.upload.status = File.FAILED
            self.upload.save()
            return False

    def clear_results(self):
        self.errors = []
        self.error_counts = {}
        self.total_errors = 0

    def add_error(self, value, message, line=None, name=None):
        counts = self.error_counts.get(value, 0)
        counts += 1
        self.total_errors += 1
        self.error_counts[value] = counts
        error = {'message': message, 'value': value}
        if line:
            error['line'] = line
        if name:
            error['name'] = name
        logger.debug(u'Parsers:add_error - {} ({},{}).'.format(message, line, name))
        self.errors.append(error)
