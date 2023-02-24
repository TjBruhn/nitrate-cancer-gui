# -*- coding: utf-8 -*-
"""
geoprocessing script:
    -Run IDW to generate raster from points
        - args Power=distance decay aka "k value"
    -Run Zonal Statistics as Table
    -Run Add Join to join above table to cancer rate tracts
    -Run GLR to model relationship between cancer rates and nitrate
    -Run Remove join
"""
from sys import argv
import arcpy
from layoutExport import expLyt


# set workspace
arcpy.env.workspace = r"..\G777_Proj_1\G777_Proj_1.gdb"


def nitrateCancerModel(Power=1):

    # Allow overwriting outputs
    arcpy.env.overwriteOutput = True

    # Check out extensions
    arcpy.CheckOutExtension("3D")
    arcpy.CheckOutExtension("spatial")
    arcpy.CheckOutExtension("ImageExt")
    arcpy.CheckOutExtension("ImageAnalyst")

    # identify input feature classes
    cancer_tracts = "cancer_tracts"
    well_nitrate = "well_nitrate"

    # Process: IDW -write output to memory
    Idw_py_generated = r"memory\IDW"
    IDW = Idw_py_generated
    Idw_py_generated = arcpy.sa.Idw(in_point_features=well_nitrate,
                                    z_field="nitr_ran",
                                    cell_size="500",
                                    power=Power,
                                    search_radius="VARIABLE 8",
                                    in_barrier_polyline_features="")
    Idw_py_generated.save(IDW)
    print("IDW complete")

    # Process: Zonal Statistics as Table -write output to memory
    ZonalSt_cancer_py = r"memory\ZonalSt_cancer_py"
    with arcpy.EnvManager(cellSize="MINOF"):
        arcpy.sa.ZonalStatisticsAsTable(
            in_zone_data=cancer_tracts,
            zone_field="GEOID10",
            in_value_raster=Idw_py_generated,
            out_table=ZonalSt_cancer_py,
            ignore_nodata="DATA",
            statistics_type="MEAN",
            process_as_multidimensional="CURRENT_SLICE",
            percentile_values=90,
            percentile_interpolation_type="AUTO_DETECT")
    print("zonal stats complete")

    # Process: Add Join
    cancer_tracts_join = arcpy.management.AddJoin(
        in_layer_or_view=cancer_tracts,
        in_field="GEOID10",
        join_table=ZonalSt_cancer_py,
        join_field="GEOID10",
        join_type="KEEP_ALL",
        index_join_fields="NO_INDEX_JOIN_FIELDS")[0]
    print("join complete")

    # Process: Generalized Linear Regression (GLR)
    cancer_tracts_GLR = r"cancer_tracts_GLR"
    arcpy.stats.GeneralizedLinearRegression(
        in_features=cancer_tracts_join,
        dependent_variable="cancer_tracts.canrate",
        model_type="CONTINUOUS",
        output_features=cancer_tracts_GLR,
        explanatory_variables=["ZonalSt_cancer_py.MEAN"],
        distance_features=[], prediction_locations="",
        explanatory_variables_to_match=[],
        explanatory_distance_matching=[],
        output_predicted_features="")
    print("regression complete")

    # Process: Remove Join if GLR succeeds
    if cancer_tracts_GLR:
        arcpy.management.RemoveJoin(
            in_layer_or_view=cancer_tracts_join,
            join_name="ZonalSt_cancer_py")[0]
        memDelete = arcpy.management.Delete("memory")
        print("memory deleted", memDelete)  # delete memory


if __name__ == '__main__':
    # run the model and export the layouts
    nitrateCancerModel(*argv[1:])
    expLyt()
