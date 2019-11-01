import logging
from celery import Celery
from celery.signals import worker_shutdown

from bdc_scripts.config import Config

app = Celery(__name__,
             backend='rpc://',
             broker=Config.RABBIT_MQ_URL)


@worker_shutdown.connect
def on_shutdown_release_locks(sender, **kwargs):
    from bdc_scripts.celery.cache import lock_handler

    logging.info('Turning off Celery...')
    lock_handler.release_all()