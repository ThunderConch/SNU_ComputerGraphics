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

vertex_source_phong = """#version 330 core
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
fragment_source_phong = """#version 330 core
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
    vec3 specular = specular_strength * light_intensity * d2_inv * vertex_colors.rgb * pow(dot(r, v), 4.0);

    final_colors = vec4(ambient + diffuse + specular, 1.0);
}
"""

vertex_source_gouraud = """#version 330 core
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
    vec3 specular = specular_strength * light_intensity * d2_inv * colors.rgb * pow(dot(r, v), 4.0);
    
    vertex_colors = vec4(ambient + diffuse + specular, 1.0);
}   
"""

fragment_source_gouraud = """#version 330 core
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
in vec3 vertex_normals;
in vec2 texture_coords;
in vec3 vertex_position;
out vec4 final_colors;

uniform vec3 light_position;
uniform vec3 camera_position;

uniform float ambient_intensity;
uniform float light_intensity;

uniform sampler2D ambient_map;
uniform sampler2D diffuse_map;
uniform sampler2D specular_map;
uniform sampler2D roughness_map;

void main()
{
    vec3 l = normalize(light_position - vertex_position);
    vec3 v = camera_position - vertex_position;
    float d2_inv = 1/(length(v)*length(v));
    v = normalize(v);

    vec3 n = normalize(vertex_normals);
    vec3 r = normalize(reflect(-l, n));

    vec3 ambient = texture(ambient_map, texture_coords).xyz * ambient_intensity;

    vec3 diffuse = texture(diffuse_map, texture_coords).xyz * light_intensity * d2_inv * max(dot(n, l), 0.0);

    vec3 roughness = texture(roughness_map, texture_coords).xyz;
    vec3 shininess = 1.0 / (1*roughness + .0);
    vec3 specular = light_intensity * d2_inv * texture(specular_map, texture_coords).xyz * pow(vec3(dot(r, v)), shininess);

    final_colors = vec4(ambient + diffuse + specular, 1.0);
}
"""

vertex_source_normal = """#version 330 core
in vec3 vertices;
in vec3 normals;
in vec3 tangents;
in vec3 bitangents;
in vec2 tex_coords;

out vec3 vertex_normals;
out vec3 vertex_tangents;
out vec3 vertex_bitangents;
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
    vertex_tangents = mat3(model) * tangents;
    vertex_bitangents = mat3(model) * bitangents;
}
"""
fragment_source_normal = """#version 330 core
in vec3 vertex_normals;
in vec3 vertex_tangents;
in vec3 vertex_bitangents;
in vec2 texture_coords;
in vec3 vertex_position;
out vec4 final_colors;

uniform vec3 light_position;
uniform vec3 camera_position;

uniform float ambient_intensity;
uniform float light_intensity;

uniform sampler2D ambient_map;
uniform sampler2D diffuse_map;
uniform sampler2D specular_map;
uniform sampler2D roughness_map;
uniform sampler2D normal_map;

void main()
{
    vec3 l = normalize(light_position - vertex_position);
    vec3 v = camera_position - vertex_position;
    float d2_inv = 1/(length(v)*length(v));
    v = normalize(v);

    vec3 t = normalize(vertex_tangents); 
    vec3 b = normalize(vertex_bitangents);
    vec3 n = normalize(vertex_normals);
    mat3 tbn_matrix = mat3(t, b, n);
    
    vec3 normal = texture(normal_map, texture_coords).xyz * 2.0 - 1.0;
    normal = normalize(tbn_matrix * normal);
    
    vec3 r = normalize(reflect(-l, normal));

    vec3 ambient = texture(ambient_map, texture_coords).xyz * ambient_intensity;

    vec3 diffuse = texture(diffuse_map, texture_coords).xyz * light_intensity * d2_inv * max(dot(normal, l), 0.0);

    vec3 roughness = texture(roughness_map, texture_coords).xyz;
    vec3 shininess = 1.0 / (1*roughness + .0);
    vec3 specular = light_intensity * d2_inv * texture(specular_map, texture_coords).xyz * pow(vec3(dot(r, v)), shininess);

    final_colors = vec4(ambient + diffuse + specular, 1.0);
}
"""


def create_program(vs_source, fs_source):
    # compile the vertex and fragment sources to a shader program
    vert_shader = Shader(vs_source, 'vertex')
    frag_shader = Shader(fs_source, 'fragment')
    return ShaderProgram(vert_shader, frag_shader)