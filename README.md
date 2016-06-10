# TurtleBot-Packages

On Ubuntu 14.04 (Trusty64)

1. Install Ansible from here http://docs.ansible.com/ansible/intro_installation.html

$ sudo apt-get install software-properties-common
$ sudo apt-add-repository ppa:ansible/ansible
$ sudo apt-get update
$ sudo apt-get install ansible

2. Install git

$ sudo apt-get install git

3. Clone this repository

$ git clone https://github.com/anuragkanungo/TurtleBot-Packages.git

4. Go to directory

$ cd TurtleBot-Packages

5. Install TurtleBot using Ansible

$ sudo ansible-playbook turtle.yml
