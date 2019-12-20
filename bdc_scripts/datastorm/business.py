from bdc_db.models.base_sql import BaseModel
from bdc_db.models import Band, Collection
from .forms import CollectionForm


class CubeBusiness:
    @classmethod
    def create(cls, params: dict):
        # add WARPED type if not send 
        if 'WARPED' not in [func.upper() for func in params['composite_function_list']]:
            params['composite_function_list'].append('WARPED')

        # generate cubes metadata
        cubes_db = Collection.query().filter().all()
        cubes = []
        cubes_serealized = []

        for composite_function in params['composite_function_list']:
            c_function_id = composite_function.upper()
            cube_id = '{}{}'.format(params['datacube'], c_function_id)

            raster_size_id = '{}-{}'.format(params['grs'], int(params['resolution']))

            # add cube
            if not list(filter(lambda x: x.id == cube_id, cubes)) and not list(filter(lambda x: x.id == cube_id, cubes_db)):
                cube = Collection(
                    id=cube_id,
                    temporal_composition_schema_id=params['temporal_schema'],
                    raster_size_schema_id=raster_size_id,
                    composite_function_schema_id=c_function_id,
                    grs_schema_id=params['grs'],
                    description=params['description'],
                    radiometric_processing=None,
                    geometry_processing=None,
                    sensor=None,
                    is_cube=True,
                    oauth_scope=None,
                    bands_quicklook=','.join(params['bands_quicklook'])
                )

                cubes.append(cube)
                cubes_serealized.append(CollectionForm().dump(cube))

        BaseModel.save_all(cubes)

        bands = []

        for cube in cubes:
            # save bands
            for band in params['bands']['names']:
                band = band.strip()
                bands.append(Band(
                    name=band,
                    collection_id=cube.id,
                    min=params['bands']['min'],
                    max=params['bands']['max'],
                    fill=params['bands']['fill'],
                    scale=params['bands']['scale'],
                    data_type=params['bands']['data_type'],
                    common_name=band,
                    resolution_x=params['resolution'],
                    resolution_y=params['resolution'],
                    resolution_unit='m',
                    description='',
                    mime_type='image/tiff'
                ))

        BaseModel.save_all(bands)

        return cubes_serealized, 201

    @classmethod
    def process(cls, collection, tiles=None, start_date=None, end_date=None):
        pass
