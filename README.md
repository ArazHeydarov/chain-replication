# chain-replication
This software is implementation of the chain replication in distributed system.
For the demonstration purposes all nodes can be created locally

### Table of contents
[Usage](#Usage)<br>
[Details](#Details)<br>
[Video](#Video)

## Usage
This software is Python program and requires Python interpreter to run the code.
I'm assuming after cloning the repo to your local computer, you already created a virtual environment and activated it. 
The next step is installing GRPC libraries for Python since all the communication between nodes and 
processes are powered by GRPC
```zsh
pip install -r requirements.txt
```
To control the whole flow we have master which has a static port, 8000. Please, make sure that, port 8000 is empty
or the error will be thrown. 
```zsh
python main.py master
```
After the master is ready for receiving messages we can initialize the nodes. Each node has its own name. 
Nodes are resembling distributed systems.

Example: python main.py node node_1
```zsh
python main.py node {node_name}
```

We continue all the communication trough either of the nodes. Nodes provide a prompt for entering commands. 
## Details
As a software architecture, separate classes are implemented for handling three types of purpose: 
master, nodes, processes.

List of tasks:

Local-store-ps {number_of_processes} :white_check_mark: <br>
Create-chain :white_check_mark:<br>
List-chain :white_check_mark:<br>
Write-operation <“Book”, Price>:   :white_check_mark: (P.s write operation expects the exact same formatting)<br>
List-books: :white_check_mark:<br>
Read-operation:  :white_check_mark:<br>
Time-out: :white_check_mark: (P.s even though the command is still Time-out, 'delay' is more suitable name)<br>
Remove-head: :white_check_mark:<br>
Restore-head: :white_check_mark:<br>

## Video
[![Alt text](https://upload.wikimedia.org/wikipedia/commons/e/e1/Logo_of_YouTube_%282015-2017%29.svg)](https://youtu.be/ozcfhv3fDBg)
