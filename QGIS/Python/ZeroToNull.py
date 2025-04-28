import os

input_layer = iface.activeLayer()
input_path = input_layer.dataProvider().dataSourceUri().split("|")[0]
output_path = os.path.splitext(input_path)[0] + "_zeros_to_null.gpkg"
output_layer_name = "zero_to_null"

# Get all decimal field names
decimal_fields = [field.name() for field in input_layer.fields()
                  if field.typeName().lower() in ['real', 'double', 'decimal']]

# Create output layer
writer = QgsVectorFileWriter(
    output_path,
    'UTF-8',
    input_layer.fields(),
    input_layer.wkbType(),
    input_layer.sourceCrs(),
    'GPKG',
    layerOptions=['LAYERS=output_layer']  # 👈 this ensures the internal name is set
)


# Write features with 0 replaced by NULL
for feature in input_layer.getFeatures():
    attrs = feature.attributes()
    for i, field in enumerate(input_layer.fields()):
        if field.name() in decimal_fields and attrs[i] == 0:
            attrs[i] = None
    new_feat = QgsFeature()
    new_feat.setGeometry(feature.geometry())
    new_feat.setAttributes(attrs)
    writer.addFeature(new_feat)

del writer  # Save and finalize

# Load the new layer into the QGIS project
iface.addVectorLayer(output_path + "|layername=" + output_layer_name, output_layer_name, "ogr")

print(f"New layer '{output_layer_name}' created at:\n{output_path}")
