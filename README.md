# csvfileparser
A simple CSV file app
API endpoints
1. /csvfile/upload/ - Uploading File using API from 
2. /csvfile/top-five-customers-qty/ - API listing top 5 customers based on quantity 
3. /csvfile/total-invoice-daily/2019-07-09/ - Listing total invoice daily based on a user entered date
4. /csvfile/total-transaction-monthly/ - Total transactions monthly
Endpoint to upload file
5. /csvfile/file-upload - To upload a file using an interface
Graphical Endpoints
6./csvfile/plot-customer-total/ - To plot top five customers based on due amount
7./csvfile/plot-invoice-thirty/2019-07-09/ - Plot 30 day + transactions based on an entered date

The project is built using
1. Python3
2. Django 1.11
3. Mysql
4. Django Rest Framework
5. Pandas for Csv parsing
6. Plotly for Graph

FileUpload flow explained
When a file is uploaded through the REST API/User interface endpoint, the file is saved in a File Model which generates an instance
for the uploaded file. The instance is then sent to the parser module. The FileParser module is a module that basically
has the methods for parsing the header and body of the file. First, the header is checked and it must fit into the compulsory
header fields that is required for the header check to succeed. If the header is valid then the parse() function proceeds to 
parse through the rows. For parsing, the pandas library is used. In order to make sure of data integrity only rows with 
complete data for compulsory headers is committed. Invoice number is used as Primary key and is indexed. The rows are parsed
and saved in a Python list. The bulk_create method is called to commit the rows in the Database instead of adding each rows
individually for better performance. In order to calculate the total column based on unit_amount*quantity, django built in 
post_save signal is used. The bulk_create method doesn't call the built in model save() method and so in order to trigger it 
manually, we had to write a customer manager through which the post_save method is trigerred. The update_invoice_total() method
is to used to calculate the total amount and F expression is used to update in order to avoid race conditions and have a 
database lock while a particular record is being updated.

Possible Improvements
1. Celery can be used to handle the upload in the background for large file size
2. Since, I am only using 40 records based on the sample csv file, I parsed the entire file and saved in a Python list and then committed the rows in one DB call. This is highly inefficient when it comes to file size which exceeds >4-5 GB as loading all the records in the memory will cause system breakdown. In such a case, a class BulkUploadManager can be built
which will handle chunks of data of specific size loaded from a list and will commit to the DB. 
