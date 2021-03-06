#
# This file is part of Brazil Data Cube Collection Builder.
# Copyright (C) 2019-2020 INPE.
#
# Brazil Data Cube Collection Builder is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Define Brazil Data Cube command line utilities.

Creates a python click context and inject it to the global flask commands.
"""

import click
from bdc_catalog.models import Band, Collection, db
from bdc_catalog.cli import cli
from flask.cli import with_appcontext, FlaskGroup

from . import create_app
from .collections.sentinel.utils import Sentinel2SR
from .collections.utils import get_or_create_model


# Create bdc-collection-builder cli from bdc-db
@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Command line for Collection Builder."""


@cli.group()
@with_appcontext
def scenes():
    """Handle collection images"""


@scenes.command()
@click.option('--scene-ids', required=True, help='Given scene id to download')
@with_appcontext
def download(scene_ids):
    """Download the Landsat-8 products using scene id.

    TODO: Support Sentinel 2 and Landsat 5/7.
    """
    from bdc_catalog.models import Collection
    from .collections.business import RadcorBusiness
    from .collections.landsat.utils import LandsatSurfaceReflectance08, factory
    from .collections.utils import get_earth_explorer_api, EARTH_EXPLORER_DOWNLOAD_URI, EARTH_EXPLORER_PRODUCT_ID
    from .utils import initialize_factories

    initialize_factories()

    scenes = scene_ids.split(',')

    api = get_earth_explorer_api()

    dataset = 'LANDSAT_8_C1'

    collection = Collection.query().filter(Collection.name == LandsatSurfaceReflectance08.id).first_or_404()

    for scene in scenes:
        landsat_scene_level_1 = factory.get_from_sceneid(scene_id=scene, level=1)

        formal = api.lookup(dataset, [scene], inverse=True)

        link = EARTH_EXPLORER_DOWNLOAD_URI.format(folder=EARTH_EXPLORER_PRODUCT_ID[dataset], sid=formal[0])

        activity = dict(
            collection_id=collection.id,
            activity_type='downloadLC8',
            tags=[],
            sceneid=scene,
            scene_type='SCENE',
            args=dict(link=link)
        )

        _ = RadcorBusiness.create_activity(activity)

        RadcorBusiness.start(activity)


@cli.command('load-collections')
@with_appcontext
def load_collections():
    """Load initial collections for Sentinel 2 on Collection Builder."""
    with db.session.begin_nested():
        defaults = dict(
            id='S2_MSI_L2_SR_LASRC',
            grs_schema_id='MGRS',
            description='Sentinel 2A/2B Surface Reflectance using laSRC 2.0 and Fmask 4',
            geometry_processing='ortho',
            is_cube=False,
            radiometric_processing='SR',
            sensor='MSI',
            bands_quicklook='red,green,blue',
            composite_function_schema_id='IDENTITY',
        )

        collection, _ = get_or_create_model(Collection, defaults=defaults, id=defaults['id'])

        bands = Sentinel2SR.get_band_map(None)

        bands['EVI'] = 'evi'
        bands['NDVI'] = 'ndvi'

        for band_name, common_name in bands.items():
            where = dict(
                name=band_name, common_name=common_name, collection_id=collection.id
            )

            resolution = 10
            data_type = 'int16'
            min_value, max_value = 1, 10000
            fill = 0
            scale = '0.0001'

            if common_name == 'quality':
                data_type = 'Byte'
                max_value = 12
                scale = '1'

            band_defaults = dict(
                name=band_name,
                common_name=common_name,
                collection_id=collection.id,
                min=min_value,
                max=max_value,
                fill=fill,
                scale=scale,
                data_type=data_type,
                mime_type='image/tiff',
                resolution_unit='m',
                resolution_x=resolution,
                resolution_y=resolution,
            )

            band, _ = get_or_create_model(Band, defaults=band_defaults, **where)

    db.session.commit()


def main(as_module=False):
    """Load Brazil Data Cube (bdc_collection_builder) as module."""
    import sys
    cli.main(args=sys.argv[1:], prog_name="python -m bdc_collection_builder" if as_module else None)
