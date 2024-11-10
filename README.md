```sh
pip install <FILE>.whl
```

Add settings.py
```py
os.environ['PATH'] = os.path.join(BASE_DIR, '.marketplace\Lib\site-packages\osgeo') + ';' + os.environ['PATH']
os.environ['PROJ_LIB'] = os.path.join(BASE_DIR, '.marketplace\Lib\site-packages\osgeo\data\proj') + ';' + os.environ['PATH']
GDAL_LIBRARY_PATH = os.path.join(BASE_DIR, '.marketplace\Lib\site-packages\osgeo\gdal.dll')
```
