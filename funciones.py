import folium
from branca.element import MacroElement
from jinja2 import Template
import pandas as pd

def agregar_titulo(mapa,texto: str) -> None:
        html = f'''
                <div style="position: fixed; 
                        top: 10px; left: 50%; transform: translateX(-50%);
                        width: 600px; height: 50px; 
                        background-color: white; border:2px solid black; z-index:9999; 
                        font-size:20px; font-weight: bold;
                        text-align: center; padding: 10px;
                        border-radius: 20px;">
                        {texto}
                </div>
                '''
        mapa.get_root().html.add_child(folium.Element(html))


def agregar_html(mapa, custom_html: str) -> None:
    mapa.get_root().html.add_child(folium.Element(custom_html))


class BindHTML(MacroElement):
    def __init__(self, layer, html_content):
        super(BindHTML, self).__init__()
        self.layer = layer
        self.html_content = html_content
        self._template = Template("""
            {% macro script(this, kwargs) %}
                var map = {{this._parent.get_name()}};
                var layer = {{this.layer.get_name()}};
                
                // Create the logic to add/remove the HTML
                var addLegend = function() {
                    var el = document.getElementById('legend_id');
                    if (!el) {
                        var new_el = L.DomUtil.create('div', 'legend_div');
                        new_el.id = 'legend_id';
                        new_el.innerHTML = {{this.html_content|tojson}};
                        // Append to the map container so it stays with the map
                        map.getContainer().appendChild(new_el);
                    }
                };

                var removeLegend = function() {
                    var el = document.getElementById('legend_id');
                    if (el) {
                        el.remove();
                    }
                };

                // Listen to Layer Control events
                map.on('overlayadd', function(e) {
                    if (e.layer === layer) {
                        addLegend();
                    }
                });

                map.on('overlayremove', function(e) {
                    if (e.layer === layer) {
                        removeLegend();
                    }
                });

                // Check initial state (if the layer is added by default)
                if (map.hasLayer(layer)) {
                    addLegend();
                }
            {% endmacro %}
        """)

def popup_html(col) -> str:
    if col['websiteUri'] != '#':
        html = f'''
                    <div style="font-family: Arial, sans-serif; padding: 5px; border-radius: 5px; background-color: #fffff; max-width: 250px;">
                    <h3 style="color: #121111; margin-top: 0; margin-bottom: 5px; border-bottom: 2px solid #2b2929; padding-bottom: 3px;">
                        <center>{col['displayName']}</center>
                    </h3>
                    <p style="margin: 3px 0; font-size: 1.1em;">
                        ⭐ <b>Rating:</b> <span style="font-weight: bold;">{col['rating']}</span>
                    </p>
                    <p style="margin: 3px 0; font-size: 1.1em;">
                        📝 <b>Reviews:</b> {col['userRatingCount']}
                    </p>
                    
                    </p>
                    <p style="margin: 3px 0; font-size: 1.1em;">
                        🔗 <a href={col['websiteUri']}>Website / Social Media </a>
                    </p>
                    
                    <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                    <p style="margin: 3px 0; font-size: 0.9em; color: #555;">
                        🏠 <b>Address:</b> {col['formattedAddress']}
                    </p>
                    </div>
        '''
    else:
        html = f'''
                    <div style="font-family: Arial, sans-serif; padding: 5px; border-radius: 5px; background-color: #fffff; max-width: 250px;">
                    <h3 style="color: #121111; margin-top: 0; margin-bottom: 5px; border-bottom: 2px solid #2b2929; padding-bottom: 3px;">
                        <center>{col['displayName']}</center>
                    </h3>
                    <p style="margin: 3px 0; font-size: 1.1em;">
                        ⭐ <b>Rating:</b> <span style="font-weight: bold;">{col['rating']}</span>
                    </p>
                    <p style="margin: 3px 0; font-size: 1.1em;">
                        📝 <b>Reviews:</b> {col['userRatingCount']}
                    </p>
                    <hr style="border-top: 1px solid #ccc; margin: 5px 0;">
                    <p style="margin: 3px 0; font-size: 0.9em; color: #555;">
                        🏠 <b>Address:</b> {col['formattedAddress']}
                    </p>
                    </div>
        '''
    return html

def radio_puntos(rango):
    match rango:
        case '1-50': return 2
        case '51-100': return 6
        case '101-200': return 8
        case '201-300': return 10
        case '301-500': return 12
        case '500+': return 14
        case _: return 0.5

def color_puntos(rating):
    if pd.isna(rating):
        return 'black'
    elif rating == 5:
        return '#2196F3'
    elif rating >= 4:
        return "#388E3C"
    elif rating >= 3:
        return '#FFEB3B'
    elif rating >= 2:
        return "#FF8400"
    else:
        return '#FF3B30'



leyenda_html = '''
<div style="position: fixed; bottom: 5px; right: 5px; width: 200px; background-color: white; border:2px solid black; z-index:9999; font-size:16px;padding: 10px;border-radius: 20px">
    <p style="margin-top: 0; font-weight: bold; font-size: 18px; font-style: italic;text-align: center;">Leyenda</p>
    <p style="font-size: 14px; text-align: center; font-style: italic">Tamaño de los circulos = Numero de Reviews</p>
    <p style="margin: 5px 0; font-weight: bold;">Rating:</p>
    <p style="margin: 3px 0;"><span style="color: #2196F3;">●</span> 5.0 estrellas</p>
    <p style="margin: 3px 0;"><span style="color: #388E3C;">●</span> 4.0 - 4.9 estrellas</p>
    <p style="margin: 3px 0;"><span style="color: #FFEB3B;">●</span> 3.0 - 3.9 estrellas</p>
    <p style="margin: 3px 0;"><span style="color: #FF8400;">●</span> 2.0 - 2.9 estrellas</p>
    <p style="margin: 3px 0;"><span style="color: #FF3B30;">●</span> < 2.0 estrellas</p>
    <p style="margin: 3px 0;"><span style="color: black;">●</span> Sin rating</p>
    </div>
'''