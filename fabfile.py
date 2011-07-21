from armstrong.dev.tasks import *


settings = {
    'DEBUG': True,
    'INTERNAL_IPS': ('127.0.0.1', ),
    'INSTALLED_APPS': (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'armstrong.core.arm_layout',
        'armstrong.core.arm_layout.tests.arm_layout_support',
        'lettuce.django',
    ),
}

tested_apps = ("arm_layout", )
