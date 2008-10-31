
def gen_config(config_name, config_template, opts = None):
    if opts is None:
        opts = {}
    open(config_name,'w').write(config_template % opts)

def gen_config_from_file(config_name, template_file_name, opts = None):
    gen_config(config_name, open(template_file_name).read(), opts)

