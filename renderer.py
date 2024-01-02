class Triangle:
    def __init__(self,app,vertex):
        self.app = app
        self.ctx = app.ctx
        vertex_data = vertex
        self.vbo = self.ctx.buffer(vertex_data)
        self.vertex_shader = self.get_shader_programs("shaders/vertex_shader.vert")
        self.fragment_shader = self.get_shader_programs("shaders/fragment_shader.frag")
        self.shader = self.ctx.program(vertex_shader=self.vertex_shader,fragment_shader=self.fragment_shader)
        self.vao = self.ctx.vertex_array(self.shader, [(self.vbo,"3f","in_position")])
    def get_shader_programs(self,file):
        with open(file) as f:
            shader = f.read()
        return shader
    def render(self):
        self.vao.render()
    def destroy(self):
        self.vbo.release()
        self.shader.release()
        self.vao.release()
class Cube:
    def __init__(self,app,vertex):
        self.app = app
        self.ctx = app.ctx
        vertex_data = vertex
        self.vbo = self.ctx.buffer(vertex_data)
        self.vertex_shader = self.get_shader_programs("shaders/vertex_shader.vert")
        self.fragment_shader = self.get_shader_programs("shaders/fragment_shader.frag")
        self.shader = self.ctx.program(vertex_shader=self.vertex_shader,fragment_shader=self.fragment_shader)
        self.vao = self.ctx.vertex_array(self.shader, [(self.vbo,"3f","in_position")])
    def get_shader_programs(self,file):
        with open(file) as f:
            shader = f.read()
        return shader
    def render(self):
        self.vao.render()
    def destroy(self):
        self.vbo.release()
        self.shader.release()
        self.vao.release()
class camera:
    def __init__(self,fov):
        pass
class light:
    def __init__(self):
        pass