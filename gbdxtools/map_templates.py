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
                  mapboxgl: 'https://api.tiles.mapbox.com/mapbox-gl-js/v0.52.0/mapbox-gl'
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
                    includeSnapshotLinks: true,
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
                map.addControl(new mapboxgl.NavigationControl());
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

                var buttonContainer = document.getElementById("$map_id").getElementsByClassName('mapboxgl-ctrl-top-left')[0],
                    downloadControl = document.createElement('div');
                downloadControl.className = 'map-dload mapboxgl-ctrl mapboxgl-ctrl-group ctrl-group-horizontal'; 
                downloadControl.id = 'download-controls';
                buttonContainer.appendChild(downloadControl);
                document.getElementById("$map_id").getElementsByClassName('map-dload')[0].innerHTML = '<button class="mapboxgl-ctrl-icon screencap-icon"><a class="download-btn" href="#" title="Download map as .png" id="btn-download-map-$map_id" class="$map_id-dload-link" download="map.png">...</a></button>';
                var mapButton = document.getElementById("btn-download-map-$map_id") //.getElementsByClassName('$map_id-dload-link')[0];
                mapButton.addEventListener('click', function (e) {
                    var mapCanvas = map.getCanvas();
                    mapButton.href = mapCanvas.toDataURL('image/png');
                });
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
           <style>
            #$map_id .mapboxgl-ctrl-icon.screencap-icon .download-btn {background-image: url('data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB2ZXJzaW9uPSIxLjEi%0D%0AIGlkPSJhdHRyYWN0aW9uLTE1IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdp%0D%0AZHRoPSIxNXB4IiBoZWlnaHQ9IjE1cHgiIHZpZXdCb3g9IjAgMCAxNSAxNSI+CiAgPHBhdGggaWQ9%0D%0AInJlY3Q3MTQzIiBkPSJNNiwyQzUuNDQ2LDIsNS4yNDc4LDIuNTA0NSw1LDNMNC41LDRoLTJDMS42%0D%0ANjksNCwxLDQuNjY5LDEsNS41djVDMSwxMS4zMzEsMS42NjksMTIsMi41LDEyaDEwJiN4QTsmI3g5%0D%0AO2MwLjgzMSwwLDEuNS0wLjY2OSwxLjUtMS41di01QzE0LDQuNjY5LDEzLjMzMSw0LDEyLjUsNGgt%0D%0AMkwxMCwzQzkuNzUsMi41LDkuNTU0LDIsOSwySDZ6IE0yLjUsNUMyLjc3NjEsNSwzLDUuMjIzOSwz%0D%0ALDUuNSYjeEE7JiN4OTtTMi43NzYxLDYsMi41LDZTMiw1Ljc3NjEsMiw1LjVTMi4yMjM5LDUsMi41%0D%0ALDV6IE03LjUsNWMxLjY1NjksMCwzLDEuMzQzMSwzLDNzLTEuMzQzMSwzLTMsM3MtMy0xLjM0MzEt%0D%0AMy0zUzUuODQzMSw1LDcuNSw1eiYjeEE7JiN4OTsgTTcuNSw2LjVDNi42NzE2LDYuNSw2LDcuMTcx%0D%0ANiw2LDhsMCwwYzAsMC44Mjg0LDAuNjcxNiwxLjUsMS41LDEuNWwwLDBDOC4zMjg0LDkuNSw5LDgu%0D%0AODI4NCw5LDhsMCwwQzksNy4xNzE2LDguMzI4NCw2LjUsNy41LDYuNSYjeEE7JiN4OTtMNy41LDYu%0D%0ANXoiLz4KPC9zdmc+'); background-position: center;  background-repeat: no-repeat; cursor: default; padding: 5px; }
            #$map_id .mapboxgl-ctrl.mapboxgl-ctrl-group.ctrl-group-horizontal { height: 30px; }
            #$map_id .mapboxgl-ctrl.mapboxgl-ctrl-group.ctrl-group-horizontal > button { min-width: 30px; width: auto; height: 30px; display: inline-block !important; box-sizing: none; border-top: none; border-left: 1px solid #ddd; border-right: 1px solid #ddd;     vertical-align: top; }
            #$map_id .mapboxgl-ctrl.mapboxgl-ctrl-group.ctrl-group-horizontal > button > a { color: #6e6e6e; text-decoration: none; font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif; }
            #$map_id .mapboxgl-ctrl.mapboxgl-ctrl-group.ctrl-group-horizontal > button:first-child,
            #$map_id .mapboxgl-ctrl.mapboxgl-ctrl-group.ctrl-group-horizontal > button:last-child { border: none; }
            #$map_id .mapboxgl-ctrl.mapboxgl-ctrl-group.ctrl-group-horizontal > button:not(:first-child) { padding: 0 4px 0 4px; }
           <style>
        ''').substitute({"map_id": self.map_id})))

        display(Javascript(self.template))
