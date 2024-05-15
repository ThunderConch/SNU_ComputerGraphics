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

vertex_source_no_texture = """#version 330 core
in vec3 vertices;
in vec3 normals;
in vec4 colors;

out vec4 vertex_colors;
out vec3 vertex_normals;
out vec3 vertex_position;
out vec3 light_position;
out vec3 camera_position;

uniform vec3 light_src;
uniform vec3 cam_pos;
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
    light_position = light_src;
    camera_position = cam_pos;
}
"""
fragment_source_no_texture = """#version 330 core
in vec4 vertex_colors;
in vec3 vertex_normals;
in vec3 vertex_position;
in vec3 light_position;
in vec3 camera_position;
out vec4 final_colors;

void main()
{
    vec3 l = normalize(vertex_position - light_position);
    vec3 v = vertex_position - camera_position;
    float d = length(v);
    v = normalize(v);

    vec3 n = normalize(vertex_normals);
    vec3 r = reflect(-l, n);

    float i = 0.2 + 1000.0 * (1/(d*d)) * (0.5*max(dot(n, l), 0.0) + 0.8 * pow(dot(r, v), 4.0));

    final_colors = vertex_colors * i;
}
"""

vertex_source_texture = """#version 330 core
in vec3 vertices;
in vec3 normals;
in vec2 tex_coords;
in vec4 colors;

out vec4 vertex_colors;
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
    vertex_colors = colors;
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