# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  #config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "private_network", ip: "192.168.33.10"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end

  config.vm.provision "shell", inline: <<-SHELL
    sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
    sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net --recv-key 0xB01FA116
    sudo apt-get update
    sudo apt-get install python-rosdep python-rosinstall-generator python-wstool python-rosinstall build-essential -y
    sudo rosdep init
    rosdep update
    mkdir ~/ros_catkin_ws
    cd ~/ros_catkin_ws
    rosinstall_generator desktop_full --rosdistro indigo --deps --wet-only --tar > indigo-desktop-full-wet.rosinstall
    wstool init -j8 src indigo-desktop-full-wet.rosinstall
    rosdep install --from-paths src --ignore-src --rosdistro indigo -y
    ./src/catkin/bin/catkin_make_isolated --install -DCMAKE_BUILD_TYPE=Release

    mkdir ~/rocon
    cd ~/rocon
    wstool init -j5 src https://raw.github.com/robotics-in-concert/rocon/indigo/rocon.rosinstall
    source /opt/ros/indigo/setup.bash
    rosdep install --from-paths src --ignore-src --rosdistro indigo -y
    ~/ros_catkin_ws/src/catkin/bin/catkin_make

    mkdir ~/kobuki
    cd ~/kobuki
    wstool init src -j5 https://raw.github.com/yujinrobot/yujin_tools/master/rosinstalls/indigo/kobuki.rosinstall
    source ~/rocon/devel/setup.bash
    rosdep install --from-paths src --ignore-src --rosdistro indigo -y
    ~/ros_catkin_ws/src/catkin/bin/catkin_make

    mkdir ~/turtlebot
    cd ~/turtlebot
    wstool init src -j5 https://raw.github.com/yujinrobot/yujin_tools/master/rosinstalls/indigo/turtlebot.rosinstall
    source ~/kobuki/devel/setup.bash
    rosdep install --from-paths src --ignore-src --rosdistro indigo -y
    ~/ros_catkin_ws/src/catkin/bin/catkin_make

  SHELL

end
