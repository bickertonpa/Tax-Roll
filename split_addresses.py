import os
import processing

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
)

# --------------------------------------------------
# User settings
# --------------------------------------------------

# Relative to QGIS project home folder
POINTS_PATH = os.path.join("Addresses", "Municipal_Address_Point_joined_20260419.gpkg")
POINTS_LAYER_NAME = "Joined layer"

POLYGONS_PATH = os.path.join("Wards", "Wards.gpkg")
POLYGONS_LAYER_NAME = "wards__quartiers_municipaux"

# Field in polygon layer used to name each output file
WARD_NAME_FIELD = "WARD_EN"

# Output folder relative to project home
OUTPUT_FOLDER = os.path.join("Addresses", "Raw")

# Spatial predicate: use "intersects"
PREDICATE = [0]

# Set True if you want to delete the intermediate gpkg after csv export
DELETE_TEMP_GPKG = True


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def project_path(*parts):
    base = QgsProject.instance().homePath()
    return os.path.join(base, *parts)

def sanitize_filename(value):
    text = str(value).strip()
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        text = text.replace(ch, "_")
    text = text.replace(" ", "_")
    return text

def load_layer(path_relative, layer_name):
    full_path = project_path(path_relative)
    uri = f"{full_path}|layername={layer_name}" if full_path.lower().endswith(".gpkg") else full_path
    layer = QgsVectorLayer(uri, layer_name, "ogr")
    if not layer.isValid():
        raise ValueError(f"Could not load layer: {uri}")
    return layer

def extract_by_location(points_layer, polygon_layer, output_path):
    return processing.run(
        "native:extractbylocation",
        {
            "INPUT": points_layer,
            "PREDICATE": PREDICATE,
            "INTERSECT": polygon_layer,
            "OUTPUT": output_path
        }
    )

def export_layer_to_csv(layer, output_csv_path):
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "CSV"
    options.fileEncoding = "UTF-8"
    options.layerOptions = ["GEOMETRY=AS_XY"]

    result = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer,
        output_csv_path,
        QgsProject.instance().transformContext(),
        options
    )

    if result[0] != QgsVectorFileWriter.NoError:
        raise RuntimeError(f"Failed to write CSV: {output_csv_path}")


# --------------------------------------------------
# Main
# --------------------------------------------------

points = load_layer(POINTS_PATH, POINTS_LAYER_NAME)
polygons = load_layer(POLYGONS_PATH, POLYGONS_LAYER_NAME)

output_dir = project_path(OUTPUT_FOLDER)
os.makedirs(output_dir, exist_ok=True)

print(f"Points layer: {points.name()}")
print(f"Polygon layer: {polygons.name()}")
print(f"Output folder: {output_dir}")

# Reproject warning
if points.crs() != polygons.crs():
    print("WARNING: Point and polygon CRS differ.")
    print(f"Points CRS:   {points.crs().authid()}")
    print(f"Polygons CRS: {polygons.crs().authid()}")
    print("QGIS processing usually handles this, but matching CRS is safer.")

for poly_feat in polygons.getFeatures():
    ward_value = poly_feat[WARD_NAME_FIELD]

    if ward_value is None or str(ward_value).strip() == "":
        print(f"Skipping polygon FID {poly_feat.id()} because {WARD_NAME_FIELD} is empty.")
        continue

    ward_name = sanitize_filename(ward_value)

    # temporary working geopackage
    temp_gpkg_path = os.path.join(output_dir, f"{ward_name}.gpkg")

    # final csv output
    csv_output_path = os.path.join(output_dir, f"{ward_name}.csv")

    # Create a temporary single-feature layer using extract by expression
    polygon_layer_result = processing.run(
        "native:extractbyexpression",
        {
            "INPUT": polygons,
            "EXPRESSION": f"$id = {poly_feat.id()}",
            "OUTPUT": "TEMPORARY_OUTPUT"
        }
    )
    single_polygon = polygon_layer_result["OUTPUT"]

    # Extract intersecting points to temporary gpkg
    result = extract_by_location(points, single_polygon, temp_gpkg_path)

    # Load the temp gpkg output
    out_layer = QgsVectorLayer(result["OUTPUT"], ward_name, "ogr")
    if not out_layer.isValid():
        raise ValueError(f"Could not load extracted output: {result['OUTPUT']}")

    count = out_layer.featureCount()

    # Export that working output to CSV
    export_layer_to_csv(out_layer, csv_output_path)

    print(f"Wrote {csv_output_path} ({count} features)")

    # Optionally remove the temporary gpkg
    if DELETE_TEMP_GPKG and os.path.exists(temp_gpkg_path):
        try:
            os.remove(temp_gpkg_path)
        except Exception as e:
            print(f"Could not delete temp file {temp_gpkg_path}: {e}")

print("Done.")