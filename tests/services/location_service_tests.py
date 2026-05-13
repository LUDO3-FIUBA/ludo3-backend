from django.test import TestCase

from backend.services.location_service import haversine_distance, is_within_campus, TOLERANCE_METERS


class HaversineDistanceTests(TestCase):
    def test_same_point_is_zero(self):
        self.assertAlmostEqual(haversine_distance(-34.5876, -58.3981, -34.5876, -58.3981), 0.0, places=1)

    def test_known_distance_las_heras_to_paseo_colon(self):
        # These two campuses are roughly 3.5 km apart
        distance = haversine_distance(-34.5876, -58.3981, -34.6179, -58.3683)
        self.assertGreater(distance, 3000)
        self.assertLess(distance, 4500)

    def test_100m_offset_is_approximately_100m(self):
        # ~0.0009 degrees latitude ≈ 100 meters
        distance = haversine_distance(-34.5876, -58.3981, -34.5867, -58.3981)
        self.assertAlmostEqual(distance, 100, delta=15)


class IsWithinCampusTests(TestCase):
    LAS_HERAS_LAT = -34.58881221211288
    LAS_HERAS_LON = -58.39658985864721
    PASEO_COLON_LAT = -34.61756641409776
    PASEO_COLON_LON = -58.3681642316851

    def test_exact_campus_coordinates_are_within(self):
        self.assertTrue(is_within_campus('las_heras', self.LAS_HERAS_LAT, self.LAS_HERAS_LON))
        self.assertTrue(is_within_campus('paseo_colon', self.PASEO_COLON_LAT, self.PASEO_COLON_LON))

    def test_point_100m_away_is_within(self):
        # ~0.0009 degrees latitude ≈ 100 meters (well within 250m tolerance)
        self.assertTrue(is_within_campus('las_heras', self.LAS_HERAS_LAT + 0.0009, self.LAS_HERAS_LON))

    def test_point_400m_away_is_outside(self):
        # ~0.0036 degrees latitude ≈ 400 meters (outside 250m tolerance)
        self.assertFalse(is_within_campus('las_heras', self.LAS_HERAS_LAT + 0.0036, self.LAS_HERAS_LON))

    def test_las_heras_coordinates_fail_paseo_colon_check(self):
        self.assertFalse(is_within_campus('paseo_colon', self.LAS_HERAS_LAT, self.LAS_HERAS_LON))

    def test_tolerance_boundary(self):
        # Point just inside the 250m tolerance
        self.assertTrue(is_within_campus('las_heras', self.LAS_HERAS_LAT + (TOLERANCE_METERS / 111320), self.LAS_HERAS_LON))
