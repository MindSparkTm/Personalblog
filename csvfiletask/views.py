from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileSerializer, InvoiceSerializer, InvoiceDateSerializer \
    , InvoiceMonthSerializer
from .parsers import FileParser
from .models import Invoice, Month
from django.db.models import Sum
from django.views.generic import CreateView
from .forms import FileUploadForm
from django.urls import reverse_lazy
from plotly.offline import plot
from plotly.graph_objs import Scatter
import datetime


class FileView(APIView):
    '''
    APIVIEW to handle File Upload through API POST
    '''
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            instance = file_serializer.save()
            file_parser = FileParser(instance)
            file_parser.parse()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerListByYear(ListAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        """
        This view should return a list of Top Five customers according
        Total amount (quantity *unitAmount) due for a given year.
        """
        year = self.kwargs['year']
        return Invoice.objects.filter(date__year=year).order_by('-total')[:5]


class CustomerListByQty(ListAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        """
        This view should return a list of
        Top Five customers, according to Quantity bought.
        """
        return Invoice.objects.order_by('-quantity')[:5]


class TotalInvoiceTrxPer30(ListAPIView):
    serializer_class = InvoiceDateSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        import datetime
        today = self.kwargs['date']
        today = datetime.datetime.strptime(today, '%Y-%m-%d')
        thirty_days = today + datetime.timedelta(days=30)
        invoice_list = Invoice.objects.filter(date__range=[today, thirty_days]) \
            .extra(select={'day': 'date(date)'}) \
            .values('date') \
            .annotate(total=Sum('total'))
        return invoice_list


class TotalInvoiceTrxPerMonth(ListAPIView):
    serializer_class = InvoiceMonthSerializer

    def get_queryset(self):
        """
        This view should return total invoice transaction per day
        for all transactions that took place 30days from a given date..
        """
        return Invoice.objects.annotate(month=Month('date')) \
            .values('month') \
            .annotate(total=Sum('total')) \
            .order_by('month')


def CustomerByTotalPlot(request):
    '''
    Plot Top Five Customers according Total amount due
    '''
    q1 = Invoice.objects.values('customer__name', 'total').order_by('-total')[:5]
    customer_name = []
    total = []
    for i in range(len(q1)):
        customer_name.append(q1[i]['customer__name'])
        total.append(q1[i]['total'])
    plot_div = plot([Scatter(x=total, y=customer_name,
                             mode='lines', name='Top Five Customers',
                             opacity=0.8, marker_color='green')],
                    output_type='div')
    return render(request, "csvfiletask/index.html",
                  context={'plot_div': plot_div,'title':'Top Five Customers'})


def ThirtyDayTranxPlot(request, user_date):
    '''
       Plot Thirty day transaction plot based on user defined
       date
       '''
    today = datetime.datetime.strptime(user_date, '%Y-%m-%d')
    thirty_days = today + datetime.timedelta(days=30)
    invoice_list = Invoice.objects.filter(date__range=[today, thirty_days]) \
        .extra(select={'day': 'date(date)'}) \
        .values('date') \
        .annotate(total=Sum('total'))
    print(invoice_list)
    total_transx = []
    tranx_date = []
    for i in range(len(invoice_list)):
        total_transx.append(invoice_list[i]['total'])
        tranx_date.append(invoice_list[i]['date'])

    plot_div = plot([Scatter(x=tranx_date, y=total_transx,
                             mode='lines', name='Thirty day transaction plot',
                             opacity=0.8, marker_color='green')],
                    output_type='div')
    return render(request, "csvfiletask/index.html",
                  context={'plot_div': plot_div,'title':'Thirty day transaction plot'})


class FileUploadView(CreateView):
    '''
    View that handles file upload
    '''
    form_class = FileUploadForm
    template_name = 'csvfiletask/file_upload_form.html'
    success_url = reverse_lazy('csvfile:plot-customer-total')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        self.object = form.save()
        file_parser = FileParser(self.object)
        file_parser.parse()
        return super(FileUploadView, self).form_valid(form)
