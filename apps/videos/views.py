import logging
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from django.core.files.storage import FileSystemStorage


_logger = logging.getLogger(__name__)


class FileUploadView(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            myfile = request.data['file']
            user_id = request.data['user_id']
            print('user id la: ', user_id)
        except KeyError:
            return Response({'file': ['no file']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fs = FileSystemStorage()
            filename = fs.save(str(user_id)+'/'+myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            data = {
                'file': uploaded_file_url,
                'user_id' :  user_id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except:
            return Response('upload file error', status=status.HTTP_400_BAD_REQUEST)

