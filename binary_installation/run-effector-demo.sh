source /opt/ros/indigo/setup.bash
java -jar AcmeProject.jar > acmeProject.out &
python data.py > py.out &
cd rainbow_effector
roslaunch turtlebot_bringup minimal.launch > minimal.out &
sleep 30s
roslaunch turtlebot_navigation amcl_demo.launch > navigation.out &
sleep 30s
rosrun dynamic_reconfigure dynparam set /move_base recovery_behavior_enabled False
rosrun dynamic_reconfigure dynparam set /move_base clearing_rotation_allowed False
rosrun dynamic_reconfigure dynparam set /move_base shutdown_costmaps True