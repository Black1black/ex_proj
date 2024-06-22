from geoalchemy2.elements import WKTElement

from src.users.schemas import SLocation


def create_point(location: SLocation) -> WKTElement:
    '''
       Создает геометрический POINT из заданных широты и долготы и возвращает WKTElement для работы с PostGIS
    '''
    return WKTElement(f'POINT({location.longitude} {location.latitude})')