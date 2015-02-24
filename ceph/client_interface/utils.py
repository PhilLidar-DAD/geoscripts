#!/usr/bin/env python
import os, sys

sys.path.append("/home/geonode/geonode-debian-2.4.0-beta22")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)

from geonode.cephgeo.models import CephDataObject, LayerToCephObjectMap

def create_mapping(obj_name, grid_ref):
    """
        size_in_bytes   = models.IntegerField()
        last_modified   = models.DateField()
        file_hash       = models.CharField(max_length=30)
        name            = models.CharField(max_length=100)
        content_type    = models.CharField(max_length=20)
        grid_ref        = models.CharField(max_length=10)
    """
    ceph_obj = CephDataObject(name="Fred Flintstone", shirt_size="L")
