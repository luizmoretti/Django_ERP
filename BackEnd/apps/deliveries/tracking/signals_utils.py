def get_formatted_address(location_object):
    """
    Formats an address from an object (warehouse or customer).
    Uses the get_formatted_address method if available on the object,
    otherwise tries to construct an address from the common fields.

    Args:
        location_object: Object containing address information

    Returns:
        str: Address formatted for use with the Google Maps API
    """
    # Check if the object has a get_formatted_address method
    if hasattr(location_object, 'get_formatted_address') and callable(getattr(location_object, 'get_formatted_address')):
        return location_object.get_formatted_address()
    
    # Otherwise, try to build on common fields
    address_parts = []
    
    # Add common address fields
    if hasattr(location_object, 'address') and location_object.address:
        address_parts.append(location_object.address)
    
    # City and State
    city_state = []
    if hasattr(location_object, 'city') and location_object.city:
        city_state.append(location_object.city)
    if hasattr(location_object, 'state') and location_object.state:
        city_state.append(location_object.state)
    
    if city_state:
        address_parts.append(", ".join(city_state))
    
    # Zip Code
    if hasattr(location_object, 'zip_code') and location_object.zip_code:
        address_parts.append(location_object.zip_code)
    
    # Country
    if hasattr(location_object, 'country') and location_object.country:
        address_parts.append(location_object.country)
    
    # Juntar todas as partes com vírgulas
    return ", ".join(filter(None, address_parts))

def calculate_distance(origin_point, destination_point):
    """
    Calcula a distância entre dois pontos usando a fórmula de Haversine.
    
    Args:
        origin_point (tuple): Coordenadas de origem (latitude, longitude)
        destination_point (tuple): Coordenadas de destino (latitude, longitude)
        
    Returns:
        float: Distância em quilômetros
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Raio da Terra em km
    R = 6371.0
    
    lat1, lon1 = radians(origin_point[0]), radians(origin_point[1])
    lat2, lon2 = radians(destination_point[0]), radians(destination_point[1])
    
    # Diferença entre latitudes e longitudes
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Distância em quilômetros
    distance = R * c
    
    return distance

def get_destination_coordinates(delivery):
    """
    Obtém as coordenadas do destino de uma entrega.
    
    Args:
        delivery: Objeto Delivery
        
    Returns:
        tuple: Coordenadas (latitude, longitude) do destino ou None se não for possível obter
    """
    import googlemaps
    from django.conf import settings
    
    try:
        # Se o destino já tem coordenadas armazenadas
        if hasattr(delivery.destiny, 'latitude') and hasattr(delivery.destiny, 'longitude'):
            if delivery.destiny.latitude and delivery.destiny.longitude:
                return (float(delivery.destiny.latitude), float(delivery.destiny.longitude))
        
        # Caso contrário, geocodificar o endereço
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        
        # Obter endereço formatado
        address = get_formatted_address(delivery.destiny)
        
        if not address:
            return None
            
        # Geocodificar o endereço
        geocode_result = gmaps.geocode(address)
        
        if geocode_result and len(geocode_result) > 0:
            location = geocode_result[0]['geometry']['location']
            return (location['lat'], location['lng'])
            
        return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting destination coordinates: {str(e)}")
        return None

def calculate_eta_with_google_maps(origin_coords, destination_coords, departure_time=None):
    """
    Calcula o tempo estimado de chegada usando a API do Google Maps.
    
    Args:
        origin_coords (tuple): Coordenadas de origem (latitude, longitude)
        destination_coords (tuple): Coordenadas de destino (latitude, longitude)
        departure_time: Horário de partida (default: agora)
        
    Returns:
        tuple: (duração em segundos, distância em metros) ou (None, None) em caso de erro
    """
    import googlemaps
    from django.conf import settings
    from django.utils import timezone
    
    try:
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        
        # Converter coordenadas para strings
        origin = f"{origin_coords[0]},{origin_coords[1]}"
        destination = f"{destination_coords[0]},{destination_coords[1]}"
        
        # Definir horário de partida
        if not departure_time:
            departure_time = timezone.now()
        
        # Obter direções
        directions_result = gmaps.directions(
            origin,
            destination,
            mode="driving",
            departure_time=departure_time
        )
        
        if directions_result and len(directions_result) > 0:
            leg = directions_result[0]['legs'][0]
            duration_seconds = leg['duration']['value']
            distance_meters = leg['distance']['value']
            
            return (duration_seconds, distance_meters)
            
        return (None, None)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calculating ETA with Google Maps: {str(e)}")
        return (None, None)

def calculate_eta_with_speed(current_location, destination_coords, speed_kmh):
    """
    Calcula o tempo estimado de chegada com base na velocidade atual.
    
    Args:
        current_location: Ponto GeoDjango com a localização atual
        destination_coords (tuple): Coordenadas de destino (latitude, longitude)
        speed_kmh (float): Velocidade em km/h
        
    Returns:
        int: Tempo estimado em segundos ou None em caso de erro
    """
    try:
        # Extrair coordenadas da localização atual
        current_coords = (current_location.y, current_location.x)  # (latitude, longitude)
        
        # Calcular distância em km
        distance_km = calculate_distance(current_coords, destination_coords)
        
        # Calcular tempo em horas (distância / velocidade)
        if speed_kmh > 0:
            time_hours = distance_km / speed_kmh
            # Converter para segundos
            time_seconds = int(time_hours * 3600)
            return time_seconds
            
        return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calculating ETA with speed: {str(e)}")
        return None