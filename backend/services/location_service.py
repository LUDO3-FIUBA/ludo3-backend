import math

CAMPUS_COORDINATES = {
    'las_heras': {'lat': -34.58881221211288, 'lon': -58.39658985864721},
    'paseo_colon': {'lat': -34.61756641409776, 'lon': -58.3681642316851},
}

TOLERANCE_METERS = 250


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def is_within_campus(campus: str, lat: float, lon: float) -> bool:
    coords = CAMPUS_COORDINATES[campus]
    distance = haversine_distance(lat, lon, coords['lat'], coords['lon'])
    return distance <= TOLERANCE_METERS
