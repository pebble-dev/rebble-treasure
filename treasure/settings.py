from os import environ

domain_root = environ.get('DOMAIN_ROOT')
http_protocol = environ.get('HTTP_PROTOCOL', 'https')

config = {
    'SECRET_KEY': environ['SECRET_KEY'],
    'HONEYCOMB_KEY': environ.get('HONEYCOMB_KEY', None),
    'HONEYCOMB_DATASET': environ.get('HONEYCOMB_DATASET', 'rws'),
    'HONEYCOMB_CLIENT_DATASET': environ.get('HONEYCOMB_CLIENT_DATASET', 'mobile-apps'),
}
