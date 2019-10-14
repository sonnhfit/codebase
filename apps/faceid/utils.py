import os
import cv2
import numpy as np
from tqdm import tqdm
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from keras.models import load_model
from django.conf import settings


class Model:
    def __init__(self):
        self.model = load_model('/code/apps/faceid/model_data/model.h5')
        self.le = None
        self.clf = None
        self.y = None
        self.get_le(settings.MEDIA_ROOT + '/image_train/')
        self.train_classifier(settings.MEDIA_ROOT + '/image_train/')

    def calculate_embeddings(self, file, mode='single', batch_size=32):
        """
        inference function
        returns 128x1 vector
        """
        modes = ['single', 'folder', 'batch']
        if mode == modes[0]:
            if type(file) is str:
                img = cv2.imread(file)
            else:
                img = file
            if not img.shape:
                raise ValueError("Image path '{}' does not exist".format(file))
            img = mean_image_subtraction(img)
            if len(img.shape) == 3:
                img = img[np.newaxis]
            return self.model.predict(img)
        elif mode == modes[1]:
            img = stack_images(file)
            pred = []
            for start in tqdm(range(0, len(img), batch_size)):
                pred.append(self.model.predict_on_batch(img[start:start + batch_size]))
            embs = l2_normalize(np.concatenate(pred))
            return embs
        elif mode == modes[2]:
            aligned = []
            pd = []
            for path in file:
                img = cv2.imread(path)
                aligned.append(img)
            aligned = np.array(aligned)
            for start in range(0, len(aligned), batch_size):
                pd.append(self.model.predict_on_batch(aligned[start:start + batch_size]))
            embs = l2_normalize(np.concatenate(pd))
            return embs
        else:
            raise ValueError("Invalid mode. Expected one of: %s" % modes)

    def get_le(self, basepath):
        """
        label encoder contains class of images in train folder
        """
        labels = []
        if not os.path.exists(basepath):
            self.le = None
        names = read_names(basepath)
        for name in names:
            labels.extend([name] * len(os.listdir(basepath + '/' + name)))
        self.le = LabelEncoder().fit(labels)
        self.y = self.le.transform(labels)
        return self.le, self.y

    def train_classifier(self, basepath):
        if os.path.exists(basepath):
            embs = self.calculate_embeddings(basepath, mode='folder')
            self.y = self.get_le(basepath)[1]
            self.clf = SVC(kernel='linear', probability=True).fit(embs, self.y)
        return self.clf

    def classify(self, image):
        if type(image) is str:
            image = cv2.imread(image)
        image = cv2.resize(image, (160, 160))
        emb = self.calculate_embeddings(image[np.newaxis], mode='single')
        try:
            name = self.le.inverse_transform(self.clf.predict(emb))
        except:
            name = 'None'
        return name


def mean_image_subtraction(x):
    """
    preprocessing step: subtract image mean
    must apply before both training and inference
    """
    if x.ndim == 4:
        axis = (1, 2, 3)
        size = x[0].size
    elif x.ndim == 3:
        axis = (0, 1, 2)
        size = x.size
    else:
        raise ValueError('Dimension should be 3 or 4')

    mean = np.mean(x, axis=axis, keepdims=True)
    std = np.std(x, axis=axis, keepdims=True)
    std_adj = np.maximum(std, 1.0 / np.sqrt(size))
    y = (x - mean) / std_adj
    return y


def stack_images(path):
    stack = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.split('.')[-1] == 'jpg' or file.split('.')[-1] == 'png':
                img = cv2.imread(os.path.join(root, file))
                img = cv2.resize(img, (160, 160))
                img = mean_image_subtraction(img)
                stack.append(img)
    print('Stacked {} images'.format(len(stack)))
    return np.stack(stack)


def l2_normalize(x, axis=-1, epsilon=1e-10):
    output = x / np.sqrt(np.maximum(np.sum(np.square(x), axis=axis, keepdims=True), epsilon))
    return output


def read_names(path):
    names = []
    for root, dirs, files in os.walk(path):
        for name in dirs:
            names.append(name)
    return names


def draw(img, mode='mtcnn', detect_fn=None):
    modes = ['haar', 'mtcnn']
    if mode == modes[0]:
        box = []
        haar = cv2.CascadeClassifier("model_data/haarcascade_frontalface_default.xml")
        faces = haar.detectMultiScale(img, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            box.append((x, y, w, h))
        return box
    elif mode == modes[1]:
        box = []
        faces = detect_fn(img)
        for face in faces:
            box.append(face.bounding_box)
            x, y, w, h = face.bounding_box
            cv2.rectangle(img, (x, y), (w, h), (0, 255, 0), 2)
        return box
    else:
        raise ValueError("Invalid mode. Expected one of: %s" % modes)


def get_face(img, detect_fn):
    box = detect_fn(img)[0].bounding_box
    face = img[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
    return face
