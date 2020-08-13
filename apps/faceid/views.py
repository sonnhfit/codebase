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
from django.core.files.storage import default_storage

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
            # liso = FileUpload.objects.filter(user_key=data['name']).first()

            data['name'] = res
            # try:
            #     data['fi'] = liso.path
            # except:
            #     data['fi'] = ""
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


def encode1(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    my_str_as_bytes = str.encode("".join(enc))
    return base64.urlsafe_b64encode(my_str_as_bytes)

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


class IndexViewHome(View):

    def get(self, request):
        return render(request, 'index.html', {'id_name': 'KhongCo'})
    

    def post(self, request):
        global model, graph, detect_fn
        data = {'success': False}
        try:
            print(request.FILES)
            file = request.FILES['file']
            
        except KeyError:
            return render(request, 'index.html', {'mes': 'Khong co file'})

        ar = np.fromstring(file.read(), np.uint8)
        img = cv2.imdecode(ar, cv2.IMREAD_COLOR)
        try:
            face = get_face(img, detect_fn)
        except ValueError:
            return render(request, 'index.html', {'mes': 'ảnh không có mặt'})
        with graph.as_default():
            res = model.classify(face)[0]
            data['success'] = True
            liso = FileUpload.objects.filter(user_key=res)

            data['name'] = res
            # try:
            #     data['fi'] = liso.path
            # except:
            #     data['fi'] = ""
        return render(request, 'index.html', {'id_name': res, 'list_file': liso })


class MaHoaFile(View):
    def get(self, request, id_name):
        return render(request, 'son.html',  {'id_name': id_name })

        
    def post(self, request, id_name):
        print("vafo day neeeee")
        name_id = request.POST['name_id']
        print("vao day name=", name_id)

        print(dir(request.FILES['file2']))

        save_path = os.path.join(settings.MEDIA_ROOT, 'file_upload', request.FILES['file2'].name)
        path = default_storage.save(save_path, request.FILES['file2'])



        # Open a file: file
        fil = open(path, mode='r')

        # read all lines at once
        all_of_it = fil.read()
        print(all_of_it)
        str1 = encode1(name_id, all_of_it)
        print(str1)
        # close the file
        fil.close()
        ph = save_path+'a.txt'
        print("file path la ==", ph)

        f = open(ph, "w")
        my_decoded_str = str1.decode()
        f.write(my_decoded_str)
        f.close()
        g = my_decoded_str.split("/")
        g = g[2:]

        g2 = "/".join(g[2:])
        print(g2)
        FileUpload.objects.create(user_key=name_id, file_up=g2)

        liso = FileUpload.objects.filter(user_key=name_id)

        
        return render(request, 'son.html', {'id_name': name_id, 'list_file': liso })
