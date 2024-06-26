# Этот модуль предназначен для определения асинхронных задач с использованием библиотеки Celery.
# Celery используется для выполнения фоновых задач, которые могут занимать много времени,
# вне основного потока выполнения приложения.

import logging
from celery import shared_task
# Декоратор, который регистрирует функцию как задачу Celery. Это позволяет вызывать её асинхронно

from .utils import process_image
# Функция, которая выполняет обработку изображения. Она определена в модуле utils.

logger = logging.getLogger(__name__)

@shared_task
def process_image_task(feed_id: int) -> None:
    """
    Функциональность:
        - Функция process_image_task объявляется как асинхронная задача с помощью декоратора @shared_task. Э
        то означает, что её можно вызывать асинхронно через Celery.
        - Внутри функции вызывается `process_image(feed_id)`, которая выполняет реальную работу по обработке
        изображения, используя идентификатор записи в модели ImageFeed.
    Когда задача `process_image_task` ставится в очередь на выполнение через Celery, она будет выполняться
    фоновым воркером, что позволяет основному приложению продолжать работать без ожидания завершения задачи.

    Args:
        feed_id (int): Идентификатор записи в модели `ImageFeed`,
        для которой необходимо выполнить обработку изображения.
    """
    try:
        process_image(feed_id)
        logger.info(f"Successfully processed image for feed_id: {feed_id}")
    except Exception as e:
        logger.error(f"Error processing image for feed_id: {feed_id}: {e}")
