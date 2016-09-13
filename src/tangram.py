
def getScene(url):
    return """
import:
    - https://mapzen.com/carto/refill-style/3/refill-style.yaml
    - https://tangrams.github.io/blocks/lines/chevron.yaml
    - https://tangrams.github.io/blocks/geometry/dynamic-width.yaml

sources:
    routes:
        type: GeoJSON
        url: """ +url + """

scene:
    background:
        color: white
        
layers:
    routelayer:
        data: { source: routes}
        path:
            filter: { $geometry: line }
            draw:
                lines:
                    color: white
                    order: 300000
                    width: 25px
                    cap: round
                ants:
                    color: black
                    order: 300001
                    width: 15px
        stops:
            filter: { $geometry: point }
            draw:
                points:
                    color: black
                    order: 30002
                    size: 25px
                    style: point_dot
styles:
    dots:
        mix: [space-tile, tiling-tile, shapes-circle]
        base: polygons
        shaders:
            defines:
                PATTERN_SCALE: 50.0
                DOT_SIZE: .1
                COLOR1: vec3(1.00,1.00,1.00)
                COLOR2: color.rgb
            blocks:
                color: |
                    vec2 st = getTileCoords();
                    st = tile(st,PATTERN_SCALE);
                    float dot_size = DOT_SIZE;
                    float b = circle(st, dot_size);
                filter: |
                    color.rgb = mix(COLOR1, COLOR2, b);
    ants:
        base: lines
        mix: [lines-chevron]
        blend: overlay
        shaders:
            defines:
                CHEVRON_COLOR: color.rgb
                CHEVRON_ALPHA: 1.0
                CHEVRON_BACKGROUND_COLOR: vec3(1.)
                CHEVRON_BACKGROUND_ALPHA: 1.0
                CHEVRON_SIZE: 1.
                CHEVRON_SCALE: 1.
                
    scale-buildings:
        base: lines
        mix: [geometry-dynamic-width]
        shaders:
            defines:
                WIDTH_MIN: .5
                WIDTH_MAX: 2.
                WIDTH_Z_SCALE: 0.007
            blocks:
                position: |
                    // scale buildings based on zoom
                    float zoom = u_map_position.z;
                    float min = .1;       // minimum building scale
                    float midpoint = 16.; // middle of zoom range
                    float inspeed = .1;   // number of zooms to scale buildings up
                    float outspeed = 2.;  // number of zooms to scale buildings back down
                    float e = 0.;

                    if (zoom >= midpoint) {
                        e = (zoom - midpoint) / (outspeed * .2);
                    } else {
                        e = abs(zoom - midpoint) / inspeed;
                    }
                    position.z *= ((1. - min) / (1. + (exp(e)))) + min;
                    
    point_dot:
        base: points
        texcoord: true
        blend: overlay
        shaders:
            blocks:
                color: |
                    vec2 st = v_texcoords.xy-.5;
                    float r = dot(st,st)*2.;
                    color = vec4(0.);
                    color.a = step(.1, 1.-r);
                    color.rgb += step(.1, r);
                    color.rgb += step(.5, r)-step(.2, r);
    """