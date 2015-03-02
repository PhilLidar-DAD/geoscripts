Usage:

python bulk_upload.py [-e] <directory_containing_tiled_data>

    or

bulk_upload.py [-e] <directory_containing_tiled_data>



NOTES: 
* Wait until a message says "Nothing in queue, consumer is waiting", then
  wait for a few moments before pressing Ctrl+Z to exit
  
* script must be executed inside cephgeo host

* virtualenv where geonode is installed must be present and path should 
  be specified with the --virtualenv / -e optional argument
  - default activate file is found at:
  - [/home/geonode/.virtualenvs/geonode-deb/bin/activate_this.py]
