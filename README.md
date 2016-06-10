# TurtleBot-Packages

On Ubuntu 14.04 (Trusty64)

## Install Ansible from here http://docs.ansible.com/ansible/intro_installation.html

$ sudo apt-get install software-properties-common
$ sudo apt-add-repository ppa:ansible/ansible
$ sudo apt-get update
$ sudo apt-get install ansible

## Install git

$ sudo apt-get install git

## Clone this repository

$ git clone https://github.com/anuragkanungo/TurtleBot-Packages.git

## Go to directory

$ cd TurtleBot-Packages

## Install TurtleBot using Ansible

$ sudo ansible-playbook turtle.yml
