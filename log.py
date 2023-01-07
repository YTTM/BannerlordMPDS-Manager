class Log:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(self.filename, 'w')

    def __call__(self, message1=None, message2=None, level='INFO'):
        if message1 is None:
            return
        if message2 is None:
            print(f'[{level:.4}] {message1}')
            self.file.write(f'[{level:.5}] {message1}' + '\n')
        else:
            print(f'[{level:.4}] {message1:20} {message2}')
            self.file.write(f'[{level:.5}] {message1:20} {message2}' + '\n')
