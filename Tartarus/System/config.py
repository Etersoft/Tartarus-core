
def gen_config(config_name, config_template, opts = []):
    open(config_name,'w').write(config_template % opts)

def gen_config_from_file(config_name, template_file_name, opts = []):
    genconfig(config_name, open(template_file_name).read(), opts)
