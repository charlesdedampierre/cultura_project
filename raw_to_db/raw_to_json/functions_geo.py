import geopandas as gpd
from data_model_region import Country
from shapely.geometry import Point


def point_to_coordonate(point):
    try:
        longitude = point.split(" ")[0].split("(")[1]
        latitude = point.split(" ")[1].split(")")[0]
        res = (longitude, latitude)

    except:
        res = None

    return res


df_world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))


def get_country_model(point, world=df_world):
    try:
        coordinate = point_to_coordonate(point)
        lon = float(coordinate[0])
        lat = float(coordinate[1])

        # Create a GeoSeries with the point
        point = gpd.GeoSeries([Point(lon, lat)])

        point = gpd.GeoSeries([Point(lon, lat)])
        result = world[world.geometry.intersects(point.unary_union)]
        country_code = result.iso_a3.iloc[0]
        country_name = result.name.iloc[0]
        res = Country(name=country_name, iso_a3=country_code)

    except:
        res = None

    return res
