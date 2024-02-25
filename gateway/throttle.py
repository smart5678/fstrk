from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.throttling import SimpleRateThrottle


class DuplicateError(APIException):
    status_code = status.HTTP_201_CREATED
    default_detail = 'Duplicate request'
    default_code = 'duplicate'


class DuplicateThrottle(SimpleRateThrottle):
    """Ограничивает дублирующиеся запросы"""
    scope = 'duplicate'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

    def get_ident(self, request):
        """
        Запросы определяются дублирующими на основе хэша тела запроса.
        TODO: Этого достаточно для данных типов запроса?
        """
        return hash(frozenset(request.data.items()))

    def parse_rate(self, rate):
        """
        Разрешается только один запрос в интервал времени.
        `количество/время` делит единицу времени на указанное количество запросов.
        Интервал считается в секундах, поэтому для `n/sec` (некритично для задачи) будет разрешать 1 запрос.
        """
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]] // num_requests
        return (1, duration)
