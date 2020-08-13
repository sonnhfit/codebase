import os
import pickle
import base64
import cv2
import numpy as np
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import permissions
from apps.core.utils import validate_data
from django.contrib.auth import authenticate
from apps.core.exceptions import HTTP401AuthenticationError, HTTP404NotFoundError, HTTP409ConflictError
from . import models as user_models
from .mtcnn.load_mtcnn import Detection
import tensorflow as tf
from .utils import Model, get_face
from django.conf import settings
from .models import FileUpload
from django.views import View

from django.shortcuts import render

detect_fn = Detection().find_faces

model = Model()
graph = tf.get_default_graph()


class PredictAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        global model, graph, detect_fn
        data = {'success': False}
        try:
            file = request.data['file']
        except KeyError:
            return Response({'file': ['no file']}, status=status.HTTP_400_BAD_REQUEST)

        ar = np.fromstring(file.read(), np.uint8)
        img = cv2.imdecode(ar, cv2.IMREAD_COLOR)
        try:
            face = get_face(img, detect_fn)
        except ValueError:
            Response({'message': ["can't detect this face"]}, status=status.HTTP_400_BAD_REQUEST)
        with graph.as_default():
            res = model.classify(face)[0]
            data['success'] = True
            liso = FileUpload.objects.filter(user_key=data['name']).first()

            data['name'] = res
            try:
                data['fi'] = liso.path
            except:
                data['fi'] = ""
        return Response(data, status=status.HTTP_200_OK)


class TrainingModel(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        global model, graph
        with graph.as_default():
            model.train_classifier(settings.MEDIA_ROOT + '/')
        return Response({'success': True}, status=status.HTTP_200_OK)


class ViewFile(View):
    def get(self, request, link_url):
        return render(request, 'son.html')