import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ServiceClient:
    """Client để gọi các microservices"""
    
    SERVICES = {
        'customer': settings.CUSTOMER_SERVICE_URL,
        'book': settings.BOOK_SERVICE_URL,
        'cart': settings.CART_SERVICE_URL,
        'order': settings.ORDER_SERVICE_URL,
        'pay': settings.PAY_SERVICE_URL,
        'ship': settings.SHIP_SERVICE_URL,
        'comment': settings.COMMENT_RATE_SERVICE_URL,
        'staff': settings.STAFF_SERVICE_URL,
    }
    
    @classmethod
    def get(cls, service, endpoint, params=None, timeout=10):
        url = f"{cls.SERVICES[service]}/api/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=timeout)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Service {service} error: {e}")
            return None
    
    @classmethod
    def post(cls, service, endpoint, data=None, timeout=10):
        url = f"{cls.SERVICES[service]}/api/{endpoint}"
        try:
            response = requests.post(url, json=data, timeout=timeout)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"Service {service} error: {e}")
            return None, 500
    
    @classmethod
    def put(cls, service, endpoint, data=None, timeout=10):
        url = f"{cls.SERVICES[service]}/api/{endpoint}"
        try:
            response = requests.put(url, json=data, timeout=timeout)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"Service {service} error: {e}")
            return None, 500
    
    @classmethod
    def delete(cls, service, endpoint, timeout=10):
        url = f"{cls.SERVICES[service]}/api/{endpoint}"
        try:
            response = requests.delete(url, timeout=timeout)
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Service {service} error: {e}")
            return False
