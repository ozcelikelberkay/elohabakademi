"""
Logging konfigürasyonu için yardımcı modül
"""

import os
import logging.config
from datetime import datetime

def setup_logging_config():
    """Logging konfigürasyonunu yapılandır"""
    
    # Logs klasörünü oluştur
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Logging konfigürasyonu
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'security': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(ip)s - %(user)s - %(action)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'payment': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(user_id)s - %(package)s - %(amount)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'file_upload': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(user_id)s - %(file_type)s - %(filename)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'app_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'security',
                'filename': 'logs/security.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'payment_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'payment',
                'filename': 'logs/payment.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'file_upload_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'file_upload',
                'filename': 'logs/file_upload.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            'app': {
                'level': 'INFO',
                'handlers': ['console', 'app_file'],
                'propagate': False
            },
            'error': {
                'level': 'ERROR',
                'handlers': ['console', 'error_file'],
                'propagate': False
            },
            'security': {
                'level': 'WARNING',
                'handlers': ['console', 'security_file'],
                'propagate': False
            },
            'payment': {
                'level': 'INFO',
                'handlers': ['console', 'payment_file'],
                'propagate': False
            },
            'file_upload': {
                'level': 'INFO',
                'handlers': ['console', 'file_upload_file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        }
    }
    
    # Logging konfigürasyonunu uygula
    logging.config.dictConfig(logging_config)
    
    # Başlangıç log mesajı
    logger = logging.getLogger('app')
    logger.info(f"Logging system initialized at {datetime.now()}")

def get_logger(name):
    """Belirtilen isimde logger döndür"""
    return logging.getLogger(name)

def log_security_event(level, message, ip=None, user=None, action=None):
    """Güvenlik olayını logla"""
    logger = logging.getLogger('security')
    
    extra = {
        'ip': ip or 'Unknown',
        'user': user or 'Anonymous',
        'action': action or 'Unknown'
    }
    
    if level.upper() == 'INFO':
        logger.info(message, extra=extra)
    elif level.upper() == 'WARNING':
        logger.warning(message, extra=extra)
    elif level.upper() == 'ERROR':
        logger.error(message, extra=extra)
    else:
        logger.info(message, extra=extra)

def log_payment_event(level, message, user_id=None, package=None, amount=None):
    """Ödeme olayını logla"""
    logger = logging.getLogger('payment')
    
    extra = {
        'user_id': user_id or 'Unknown',
        'package': package or 'Unknown',
        'amount': amount or 'Unknown'
    }
    
    if level.upper() == 'INFO':
        logger.info(message, extra=extra)
    elif level.upper() == 'WARNING':
        logger.warning(message, extra=extra)
    elif level.upper() == 'ERROR':
        logger.error(message, extra=extra)
    else:
        logger.info(message, extra=extra)

def log_file_upload_event(level, message, user_id=None, file_type=None, filename=None):
    """Dosya yükleme olayını logla"""
    logger = logging.getLogger('file_upload')
    
    extra = {
        'user_id': user_id or 'Unknown',
        'file_type': file_type or 'Unknown',
        'filename': filename or 'Unknown'
    }
    
    if level.upper() == 'INFO':
        logger.info(message, extra=extra)
    elif level.upper() == 'WARNING':
        logger.warning(message, extra=extra)
    elif level.upper() == 'ERROR':
        logger.error(message, extra=extra)
    else:
        logger.info(message, extra=extra)
