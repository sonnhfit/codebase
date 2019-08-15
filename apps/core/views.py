from django.shortcuts import render
from rest_framework.views import exception_handler as drf_exception_handler
from django.views import View
# Create your views here.


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    return response


class IndexView(View):

    def get(self, request):
        return render(request, 'index.html')
