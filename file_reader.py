

def read_config_file(file = 'info_files/config.txt'):
    config = {}
    with open(file) as f:
        while True:
            read = f.readline()
            if(read == ''):
                break
            read = read.removesuffix('\n').split('=')
            config[read[0]] = read[1]
            # print(f'{read}')
        # print(config)
        return config