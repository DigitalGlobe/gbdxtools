from string import Template


class BaseTemplate(object): 
    
    def __new__(self, **kwargs):
        return Template("""
            require.config({
              paths: {
                  mapboxgl: 'https://api.tiles.mapbox.com/mapbox-gl-js/v0.52.0/mapbox-gl',
              }
            });

            require(['mapboxgl'], function(mapboxgl){
                mapboxgl.accessToken = "$mbkey";
                var layers = $layers;

                var map = new mapboxgl.Map({
                    container: '$map_id',
                    style: 'mapbox://styles/mapbox/satellite-v9',
                    center: [$lon, $lat],
                    zoom: $zoom,
                    preserveDrawingBuffer: true
                });
                map.on('load', function(e) {
                    try {
                        for (var i=0; i < layers.length; i++) {
                          console.log('LAYER', layers[i])
                          map.addLayer(layers[i]);
                        }
                    } catch (err) {
                        console.log(err);
                    }
                });

                map.on('load', function(e){
                    setTimeout( function() {
                        var mapCanvas = map.getCanvas();
                        var thumbCanvas=document.createElement('canvas');
                        var thumbContext=thumbCanvas.getContext('2d');
                        var height = mapCanvas.scrollHeight;
                        var width = mapCanvas.scrollWidth;
                        thumbCanvas.width=width/2.0;
                        thumbCanvas.height=height/2.0;
                        thumbContext.drawImage(mapCanvas, 0, 0, width*2, height*2, 0, 0, width/2, height/2)
                        var dataURL = thumbCanvas.toDataURL();
                        var imageData = dataURL.substring(dataURL.indexOf(',')+1)
                        var cell = Jupyter.notebook.get_selected_cell();
                        cell.metadata.GBDX = cell.metadata.GBDX || {};
                        cell.metadata.GBDX.static_thumbnail = cell.metadata.GBDX.static_thumbnail || {};
                        cell.metadata.GBDX.static_thumbnail.data = cell.metadata.GBDX.static_thumbnail.data || {};
                        cell.metadata.GBDX.static_thumbnail.data["image/png"] = imageData;
                    }, 5000);
                })
            });
        """).substitute(kwargs)
