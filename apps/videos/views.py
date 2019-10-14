import logging
import base64
import os
import sys

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.conf import settings
from .serializers import ImageSerializer
from apps.core.utils import validate_data
from datetime import datetime
from ..faceid.mtcnn.load_mtcnn import Detection
import cv2
import os
import numpy as np

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
                'user_id':  user_id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response('upload file error', status=status.HTTP_400_BAD_REQUEST)


class Base64FileUploadView(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):

        valid_data = validate_data(ImageSerializer, request.data)
        data = valid_data.get('img')
        user_id = valid_data.get('user_id')
        try:
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            imgdata = base64.b64decode(imgstr)
            filename = "test_image" + str(datetime.now()) + ".jpg"
            with open(filename, 'wb') as f:
                f.write(imgdata)
            image = cv2.imread(filename)
            detect = Detection()
            faces = detect.faces_crop(np.array(image))
            os.remove(filename)
            mydir = settings.MEDIA_ROOT + '/image_train/' + str(user_id) + '/'
            name = mydir + str(user_id) + str(datetime.now()) + '.' + 'jpg'
            print(name)
            if os.path.exists(mydir):
                os.chmod(mydir, 0o777)
            else:
                os.mkdir(mydir)
                os.chmod(mydir, 0o777)
            name_file = str(datetime.now()) + '.' + 'jpg'
            cv2.imwrite(os.path.join(mydir, name_file), np.asarray(faces))
            path_change = mydir + name_file
            os.chmod(path_change, 0o777)
            result = {
                'user_id': user_id,
                'img': filename
            }
            return Response(result, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response('upload file error', status=status.HTTP_400_BAD_REQUEST)
