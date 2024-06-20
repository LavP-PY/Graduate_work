"""
Описание работы модуля:
    1. Импорт необходимых модулей:
        - `cv2`: Библиотека OpenCV для компьютерного зрения.
        - `numpy`: Библиотека для работы с массивами.
        - `ContentFile`: Класс Django для работы с файлами.
        - `ImageFeed`, `DetectedObject`: Модели Django для работы с изображениями и обнаруженными объектами.
    2. VOC_LABELS:
        - Список меток классов для объектов, распознаваемых моделью. Эти метки соответствуют классам из набора данных PASCAL VOC.
    3. process_image(image_feed_id):
        - Основная функция для обработки изображения и обнаружения объектов.
    4. Получение записи ImageFeed:
        - Поиск записи ImageFeed по идентификатору image_feed_id. Если запись не найдена, возвращается False.
    5. Загрузка модели и конфигурации:
        - Загрузка модели MobileNet SSD из файлов Caffe (`.caffemodel` и `.prototxt`).
    6. Чтение изображения:
        - Чтение изображения с диска по пути, указанному в image_feed.
    7. Преобразование изображения в формат blob:
        - Преобразование изображения в blob для подачи в модель.
    8. Выполнение прямого прохода через сеть:
        - Установка входных данных для сети и выполнение прямого прохода (inference).
    9. Обработка каждого обнаруженного объекта:
        - Для каждого обнаруженного объекта проверяется уверенность (confidence). Если уверенность выше порога (0.6), объект считается обнаруженным;
        - Получение координат ограничивающего прямоугольника (bounding box);
        - Рисование прямоугольника и метки на изображении;
        - Создание записи DetectedObject в базе данных.
    10. Сохранение обработанного изображения:
        - Кодирование обработанного изображения обратно в формат jpg;
        - Сохранение обработанного изображения в поле processed_image модели ImageFeed.

Этот код позволяет загружать изображение, обрабатывать его с использованием модели MobileNet SSD, обнаруживать объекты на изображении и сохранять результаты в базе данных.
"""
import cv2
import numpy as np
import random
from django.core.files.base import ContentFile
from .models import ImageFeed, DetectedObject
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image

# Список меток классов для объектов, распознаваемых моделью (VOC dataset).
# Эти метки соответствуют классам из набора данных PASCAL VOC
VOC_LABELS = [
    "background", "aeroplane", "bicycle", "bird", "boat", "bottle",
    "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant",
    "sheep", "sofa", "train", "tvmonitor"
]


def process_image(image_feed_id):
    """
    Функция для обработки изображения и обнаружения объектов с использованием модели MobileNet SSD.

    :param image_feed_id: Идентификатор записи ImageFeed, содержащей изображение для обработки.
    :type image_feed_id: int
    :return: True, если изображение успешно обработано, иначе False.
    :rtype: bool

    :raises ImageFeed.DoesNotExist: Если запись ImageFeed с указанным идентификатором не найдена.
    """
    try:
        # Получение записи ImageFeed по идентификатору
        image_feed = ImageFeed.objects.get(id=image_feed_id)
        image_path = image_feed.image.path

        # Пути к файлам модели и конфигурации
        model_path = 'object_detection/mobilenet_iter_73000.caffemodel'
        config_path = 'object_detection/mobilenet_ssd_deploy.prototxt'
        # Загрузка модели из файлов Caffe
        net = cv2.dnn.readNetFromCaffe(config_path, model_path)

        # Чтение изображения с диска
        img = cv2.imread(image_path)
        if img is None:
            print("Failed to load image")
            return False

        # Получение высоты и ширины изображения
        h, w = img.shape[:2]
        # Преобразование изображения в формат blob для подачи в модель
        blob = cv2.dnn.blobFromImage(img, 0.007843, (300, 300), 127.5)

        # Установка входных данных для сети и выполнение прямого прохода (inference)
        net.setInput(blob)
        detections = net.forward()

        # Обработка каждого обнаруженного объекта
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2] # Уверенность распознавания
            if confidence > 0.6:    # Игнорирование слабых распознаваний
                class_id = int(detections[0, 0, i, 1])  # Идентификатор класса
                class_label = VOC_LABELS[class_id]  # Метка класса
                # Координаты ограничивающего прямоугольника (bounding box)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # Рисование прямоугольника и метки на изображении
                cv2.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)
                label = f"{class_label}: {confidence:.2f}"
                cv2.putText(img, label, (startX+5, startY + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Создание записи DetectedObject в базе данных
                DetectedObject.objects.create(
                    image_feed=image_feed,
                    object_type=class_label,
                    location=f"{startX},{startY},{endX},{endY}",
                    confidence=float(confidence)
                )

        # Кодирование обработанного изображения обратно в формат jpg
        result, encoded_img = cv2.imencode('.jpg', img)
        if result:
            # Сохранение обработанного изображения в поле processed_image
            content = ContentFile(encoded_img.tobytes(), f'processed_{image_feed.image.name}')
            image_feed.processed_image.save(content.name, content, save=True)

        return True

    except ImageFeed.DoesNotExist:
        print("ImageFeed not found.")
        return False

def process_alternative_image(image_feed_id):
    """
    Функция для обработки изображения с использованием модели DETR.

    :param image_feed_id: Идентификатор записи ImageFeed, содержащей изображение для обработки.
    :type image_feed_id: int
    :return: Список словарей с результатами обнаружения объектов, каждый из которых содержит метку, уверенность и координаты ограничивающего прямоугольника.
    :rtype: list

    :raises ImageFeed.DoesNotExist: Если запись ImageFeed с указанным идентификатором не найдена.
    """
    try:
        # Получение записи ImageFeed по идентификатору
        image_feed = ImageFeed.objects.get(id=image_feed_id)
        image_path = image_feed.image.path

        # Загрузка изображения
        image = Image.open(image_path).convert("RGB")

        # Загрузка модели Detr
        processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
        model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

        # Обработка изображения
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)

        # Преобразование результатов в формат COCO API
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

        # Загрузка изображения с помощью OpenCV
        img = cv2.imread(image_path)
        if img is None:
            print("Failed to load image")
            return False

        # Получение высоты и ширины изображения
        h, w = img.shape[:2]

        # Обработка результатов
        detections = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i) for i in box.tolist()]
            detection_info = {
                'label': model.config.id2label[label.item()],
                'score': round(score.item(), 3),
                'box': box,
            }
            detections.append(detection_info)

            # Генерация случайного цвета для каждого обнаруженного объекта
            color = generate_random_color()

            # Рисование прямоугольника и метки на изображении
            startX, startY, endX, endY = box
            cv2.rectangle(img, (startX, startY), (endX, endY), color, 2)
            label_text = f"{detection_info['label']}: {detection_info['score']:.2f}"
            print(detection_info, detection_info['label'], label_text)
            cv2.putText(img, label_text, (startX + 5, startY + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Создание записи DetectedObject в базе данных
            DetectedObject.objects.create(
                image_feed=image_feed,
                object_type=detection_info['label'],
                location=f"{startX},{startY},{endX},{endY}",
                confidence=detection_info['score']
            )

        # Кодирование обработанного изображения обратно в формат jpg
        result, encoded_img = cv2.imencode('.jpg', img)
        if result:
            # Сохранение обработанного изображения в поле processed_image
            content = ContentFile(encoded_img.tobytes(), f'processed_{image_feed.image.name}')
            image_feed.processed_image.save(content.name, content, save=True)

        return detections

    except ImageFeed.DoesNotExist:
        print("ImageFeed not found.")
        return []

def generate_random_color():
    """
    Генерирует случайный цвет.

    :return: Случайный цвет в формате (B, G, R).
    :rtype: tuple
    """
    levels = range(32, 256, 32)
    print(levels)
    return tuple(random.choice(levels) for _ in range(3))
