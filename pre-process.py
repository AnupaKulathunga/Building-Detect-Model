import subprocess
import sys
from osgeo import ogr

def shapefile_to_wkt(shapefile_path):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shapefile_path, 0)
    layer = dataSource.GetLayer()
    feature = layer.GetNextFeature()
    geom = feature.GetGeometryRef()
    return geom.ExportToWkt()

def execute_gpt(input_file, output_name, output_format, wkt):
    graph_file = 'graph.xml'
    gpt_path = '/home/anupa/snap-esa/bin/gpt'  # Update with the correct path to your gpt executable
    cmd = [
        gpt_path,
        graph_file,
        '-PinputFile=' + input_file,
        '-PsubsetRegion=' + wkt,
        '-PoutputName=' + output_name,
        '-Pformat=' + output_format
    ]
    subprocess.run(cmd)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python preprocess.py <input_file> <shapefile> <output_name> <output_format>")
        sys.exit(1)

    input_file = sys.argv[1]
    shapefile = sys.argv[2]
    output_name = sys.argv[3]
    output_format = sys.argv[4]

    wkt = shapefile_to_wkt(shapefile)
    execute_gpt(input_file, output_name, output_format, wkt)
