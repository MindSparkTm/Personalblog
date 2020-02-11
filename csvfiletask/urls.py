from django.conf.urls import url
from .views import FileView,CustomerListByYear,CustomerListByQty,TotalInvoiceTrxPer30\
  ,TotalInvoiceTrxPerMonth,FileUploadView,ThirtyDayTranxPlot,CustomerByTotalPlot
app_name='csvfile'
urlpatterns = [
  url(r'^upload/$', FileView.as_view(), name='file-upload'),
  url(r'^file-upload/$', FileUploadView.as_view(), name='csv-upload'),
  url('^top-five-customers/(?P<year>.+)/$', CustomerListByYear.as_view(),name='top-five-customers'),
  url('^top-five-customers-qty/$', CustomerListByQty.as_view(),name='top-five-customer-by-qty'),
  url('^total-invoice-daily/(?P<date>\d{4}-\d{2}-\d{2})/$', TotalInvoiceTrxPer30.as_view()),
  url('^total-transaction-monthly/$', TotalInvoiceTrxPerMonth.as_view()),
  url('^plot-customer-total/$',CustomerByTotalPlot,name='plot-customer-total'),
  url('^plot-invoice-thirty/(?P<user_date>\d{4}-\d{2}-\d{2})/$',ThirtyDayTranxPlot,name='plot-invoice-thirty'),

]