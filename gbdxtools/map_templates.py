from string import Template

class BaseTemplate(object): 
    
    def __init__(self, map_id, **kwargs):
        self.map_id = map_id 
        self.params = kwargs

    @property
    def template(self):
        return Template("""
            require.config({
              paths: {
                  mapboxgl: 'https://api.tiles.mapbox.com/mapbox-gl-js/v0.52.0/mapbox-gl',
              }
            });

            require(['mapboxgl'], function(mapboxgl){
                mapboxgl.accessToken = "$mbkey";
                var layers = $layers;
                
                // will be an object with an 'id' field and a 'data' field
                var datasource = $datasource;
                var imageLayer = $image_layer;

                var map = new mapboxgl.Map({
                    container: '$map_id',
                    style: 'mapbox://styles/mapbox/satellite-v9',
                    center: [$lon, $lat],
                    zoom: $zoom,
                    preserveDrawingBuffer: true,
                    transformRequest: function( url, resourceType ) {
                      if (resourceType == 'Tile' && url.startsWith('https://vector.geobigdata')) {
                        return {
                            url: url,
                            headers: { 'Authorization': 'Bearer $token' }
                        }
                      }
                    }
                });
                map.on('load', function(e) {
                    try {
                        console.log('DATASOURCE', datasource);
                        map.addSource(datasource.id, datasource.data);

                        if (imageLayer) {
                          console.log('IMAGELAYER', imageLayer)
                          map.addLayer(imageLayer);
                        }
                        
                        for (var i=0; i < layers.length; i++) {
                          console.log('LAYER', layers[i])
                          map.addLayer(layers[i]);
                        }
                    } catch (err) {
                        console.log(err);
                    }

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
        """).substitute(dict(map_id=self.map_id, **self.params))

    def inject(self):
        try:
            from IPython.display import HTML, display, Javascript
        except:
            print("IPython is required to produce maps.")
            return
        display(HTML(Template('''
           <div id="$map_id"/>
           <link href='https://api.tiles.mapbox.com/mapbox-gl-js/v0.52.0/mapbox-gl.css' rel='stylesheet' />
           <style>body{margin:0;padding:0;}#$map_id{position:relative;top:0;bottom:0;width:100%;height:400px;}</style>
           <style>.mapboxgl-popup-content table tr{border: 1px solid #efefef;} .mapboxgl-popup-content table, td, tr{border: none;}
           .mapboxgl-popup-content table {width: 100%; table-layout: fixed; text-align: left;} .mapboxgl-popup-content td:first-of-type{width: 33%;}
           .mapboxgl-popup-content {width: 400px !important;} .mapboxgl-popup-content td:last-of-type{overflow-x: scroll;}<style>
        ''').substitute({"map_id": self.map_id})))

        display(Javascript(self.template))
