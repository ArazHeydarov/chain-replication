import sys

from classes.master import Master
from classes.node import Node
from classes.process import Process


if len(sys.argv) > 1:
    if sys.argv[1] == 'master':
        master = Master()
        master.start_server()

    if sys.argv[1] == 'node':
        node = Node(name=sys.argv[2])
        while True:
            print(f"{node.name} prompt: ", end='')
            prompt = input()
            node.execute_command(command=prompt)

    if sys.argv[1] == 'process':
        process = Process(name=sys.argv[2])
        process.start_server()
