##
# Copyright (C) 2022 Tomas "trosos" Tintera
#
# Permission to use, copy, modify, and/or distribute this
# software for any purpose with or without fee is hereby
# granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS
# ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH
# THE USE OR PERFORMANCE OF THIS SOFTWARE.
##

class Subcommand(object):
    def __init__(self):
        self.commands = {}

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
            width = max(len(cmd) for cmd in self.commands) + 2
            failcb(
                "Usage: {} COMMAND [--help | [--] ARG...]\n\n"
                "Available COMMANDs:\n{}"
                .format(
                    argv[0],
                    "\n".join(
                        "   {{:<{}}}{{}}".format(width).format(cmd, fn.__doc__)
                        for cmd, fn in sorted(self.commands.items())
                    )
                )
            )
