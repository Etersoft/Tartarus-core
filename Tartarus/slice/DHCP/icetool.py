import TaskGen, Task

Task.simple_task_type('slice2cpp', '${SLICE2CPP} ${SRC} --output-dir ${TGT[0].dir(env)}', before='cxx')

@TaskGen.extension('.ice')
def ice_hook(self, node):
    task = self.create_task('slice2cpp')
    task.inputs = [node]
    cpp_node = node.change_ext('.cpp')
    task.outputs = [node.change_ext('.h'), cpp_node]
    ctask = self.create_task('cxx')
    ctask.inputs = [cpp_node]
    ctask.outputs = [cpp_node.change_ext('.o')]
    self.compiled_tasks.append(ctask)
    return ctask

def detect(cfg):
    cfg.find_program('slice2cpp', var='SLICE2CPP')

