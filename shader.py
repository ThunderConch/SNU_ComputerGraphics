from pyglet.graphics.shader import Shader, ShaderProgram

# create vertex and fragment shader sources
vertex_source_default = """
#version 330
layout(location =0) in vec3 vertices;
layout(location =1) in vec4 colors;

out vec4 newColor;

// add a view-projection uniform and multiply it by the vertices
uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;

void main()
{
    gl_Position = projection*view * model * vec4(vertices, 1.0f); // local->world->vp
    newColor = colors;
}
"""

fragment_source_default = """
#version 330
in vec4 newColor;

out vec4 outColor;

void main()
{
    outColor = newColor;
}
"""

vertex_source_no_texture_phong = """#version 330 core
in vec3 vertices;
in vec3 normals;
in vec4 colors;

out vec4 vertex_colors;
out vec3 vertex_normals;
out vec3 vertex_position;

uniform mat4 projection;
uniform mat4 view;

uniform mat4 model;

void main()
{
    vec4 pos = view * model * vec4(vertices, 1.0);
    gl_Position = projection * pos;
    mat3 normal_matrix = transpose(inverse(mat3(model)));

    vertex_position = pos.xyz;
    vertex_colors = colors;
    vertex_normals = normal_matrix * normals;
}
"""
fragment_source_no_texture_phong = """#version 330 core
in vec4 vertex_colors;
in vec3 vertex_normals;
in vec3 vertex_position;

out vec4 final_colors;

uniform vec3 light_position;
uniform vec3 camera_position;

uniform float ambient_intensity;
uniform float light_intensity;

void main()
{
    vec3 l = normalize(light_position - vertex_position);
    vec3 v = camera_position - vertex_position;
    float d2_inv = 1/(length(v)*length(v));
    v = normalize(v);

    vec3 n = normalize(vertex_normals);
    vec3 r = normalize(reflect(-l, n));
    
    float ambient_strength = 0.2;
    vec3 ambient = ambient_strength * ambient_intensity * vertex_colors.rgb;
    
    float diffuse_strength = 0.5;
    vec3 diffuse = diffuse_strength * light_intensity * d2_inv * vertex_colors.rgb * max(dot(n, l), 0.0);
    
    float specular_strength = 0.8;
    vec3 specular = specular_strength * light_intensity * d2_inv * vertex_colors.rgb * pow(max(dot(r, v), 0.0), 4.0);

    final_colors = vec4(ambient + diffuse + specular, 1.0);
}
"""

vertex_source_no_texture_gouraud = """#version 330 core
in vec3 vertices;
in vec3 normals;
in vec4 colors;

out vec4 vertex_colors;

uniform vec3 light_position;
uniform vec3 camera_position;

uniform float ambient_intensity;
uniform float light_intensity;

uniform mat4 projection;
uniform mat4 view;

uniform mat4 model;

void main()
{
    vec4 v_pos = view * model * vec4(vertices, 1.0);
    gl_Position = projection * v_pos;
    
    vec3 n = normalize(transpose(inverse(mat3(model))) * normals);
    vec3 l = normalize(light_position - v_pos.xyz);
    
    vec3 v = camera_position - v_pos.xyz;
    float d2_inv = 1/(length(v)*length(v));
    v = normalize(v);
    
    vec3 r = normalize(reflect(-l, n));
    
    float ambient_strength = 0.2;
    vec3 ambient = ambient_strength * ambient_intensity * colors.rgb;
    
    float diffuse_strength = 0.5;
    vec3 diffuse = diffuse_strength * light_intensity * d2_inv * colors.rgb * max(dot(n, l), 0.0);
    
    float specular_strength = 0.8;
    vec3 specular = specular_strength * light_intensity * d2_inv * colors.rgb * pow(max(dot(r, v), 0.0), 4.0);
    
    vertex_colors = vec4(ambient + diffuse + specular, 1.0);
}   
"""

fragment_source_no_texture_gouraud = """#version 330 core
in vec4 vertex_colors;
out vec4 final_colors;

void main()
{
    final_colors = vertex_colors;
}
"""

vertex_source_texture = """#version 330 core
in vec3 vertices;
in vec3 normals;
in vec2 tex_coords;

out vec3 vertex_normals;
out vec2 texture_coords;
out vec3 vertex_position;

uniform mat4 projection;
uniform mat4 view;

uniform mat4 model;

void main()
{
    vec4 pos = view * model * vec4(vertices, 1.0);
    gl_Position = projection * pos;
    mat3 normal_matrix = transpose(inverse(mat3(model)));

    vertex_position = pos.xyz;
    texture_coords = tex_coords;
    vertex_normals = normal_matrix * normals;
}
"""
fragment_source_texture = """#version 330 core
in vec4 vertex_colors;
in vec3 vertex_normals;
in vec2 texture_coords;
in vec3 vertex_position;
out vec4 final_colors;

uniform float ambient_intensity;
uniform float light_intensity;

uniform sampler2D our_texture;

void main()
{
    float l = dot(normalize(-vertex_position), normalize(vertex_normals));
    final_colors = (texture(our_texture, texture_coords) * vertex_colors) * l * 1.2;
}
"""


def create_program(vs_source, fs_source):
    # compile the vertex and fragment sources to a shader program
    vert_shader = Shader(vs_source, 'vertex')
    frag_shader = Shader(fs_source, 'fragment')
    return ShaderProgram(vert_shader, frag_shader)