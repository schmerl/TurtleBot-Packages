 #! /bin/bash
 rm -rf /usr/local/turtlebot-debs
 mkdir -p /usr/local/turtlebot-debs
 cp -a debs/* /usr/local/turtlebot-debs/
 cd /usr/local/turtlebot-debs
 dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
 sed -i -e '1ideb file:/usr/local/turtlebot-debs ./\' /etc/apt/sources.list 
