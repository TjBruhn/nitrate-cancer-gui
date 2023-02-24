# -*- coding: utf-8 -*-
import arcpy
import subprocess


# export layout from an .aprx as JPG and PDF
def expLyt():
    # set the .aprx
    aprx = arcpy.mp.ArcGISProject(r"..\G777_Proj_1\G777_Proj_1.aprx")
    # access layout named "Layout"
    lyt = aprx.listLayouts("Layout")[0]
    pdfFile = "glrMap.pdf"
    jpgFile = "glrMap.jpg"
    try:
        lyt.exportToPDF(pdfFile)
        lyt.exportToJPEG(jpgFile)
        print("JPG and PDF exported")
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
        raise


if __name__ == '__main__':
    expLyt()
    # open exported layout
    try:
        subprocess.call(["Test_outpt.pdf"], shell=True)
    except Exception as err:
        print(f"Subprocess: Unexpected {err}, {type(err)}")
        raise
