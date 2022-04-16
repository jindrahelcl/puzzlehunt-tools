class Subcommand(object):
    commands = {}

    def __call__(self, name):
        def reg_command(fn):
            self.commands[name] = fn
            return fn
        return reg_command

    def run(self, argv, failcb):
        name = argv[1] if len(argv) >= 2 else None
        command = self.commands.get(name)
        if command:
            command(argv)
        else:
            failcb(
                "Usage: {} COMMAND [ARGS...]\n\n"
                "Available COMMANDs:\n   {}"
                .format(argv[0], "\n   ".join(sorted(self.commands)))
            )
