from celery import shared_task
from .utils import process_image

@shared_task
def process_image_task(feed_id):
    process_image(feed_id)
