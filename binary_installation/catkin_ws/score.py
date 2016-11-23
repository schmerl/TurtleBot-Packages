#! /usr/bin/env python

import math;
import re;

# 200 cm * px/cm according to map
MAX_DISTANCE=200*0.185

class ScoreBasedOnLog(object):
  _experiment_start_time = 0.0
  _experiment_end_time = 0.0
  _goal_position= None
  _current_position = None
  
  def __init__(self):
    self._experiment_start_time = 0.0
    self._experiment_end_time = 0.0
    self._goal_position=()
    self._current_position=()

  def processLogFile(self):
    print 'Starting the scoring...getting info from ~/.ros/log/latest/rosout.log\n'

    with open('/home/turtlebot/.ros/log/latest/rosout.log', 'r') as log:
      for line in log:
        self.processStartTime(line)
        self.processEndTime(line)
        #self.processGoalPosition(line)
        if (self._experiment_end_time == 0.0):
          self.processCurrentPosition(line)

  def processStartTime (self, line):
    move_base_match = re.match (r'(\d+\.\d+).* Setting goal.*Position.(\d+\.\d+), (\d+\.\d+).*', line)
    if ((move_base_match is not None) & (self._experiment_start_time == 0.0)):
      self._goal_position=(float(move_base_match.group(2)),float(move_base_match.group(3)))
      self._experiment_start_time = float(move_base_match.group(1))
  
  def processEndTime(self, line):
    move_base_goal_reached = re.match(r'(\d+\.\d+).*Goal reached.*', line)
    if (move_base_goal_reached):
      self._experiment_end_time = float(move_base_goal_reached.group(1))


  def processCurrentPosition(self, line):
    cpos = re.match(r'.*BRASS.*Turtlebot.*(\d+\.\d+),(\d+\.\d+).*', line)
    if (cpos):
      self._current_position=(float(cpos.group(1)),float(cpos.group(2)))

  def scoreAccuracy(self):
    print 'Scoring Goal: {},{}; End pos: {},{}'.format(self._goal_position[0], self._goal_position[1], self._current_position[0], self._current_position[1])
    if ((len(self._goal_position) > 0) & (len(self._current_position) > 0)):
      distance=self.distance(self._goal_position,self._current_position)
      distance_score = (1-distance/MAX_DISTANCE)
      print 'Accuracy score = {}'.format(distance_score)
    else:
      print 'Accuracy score could not be calculated because goal_position or current_position is not set'
      

  def distance(self, loc1, loc2):
    return math.sqrt((loc1[0]-loc2[0])**2 + (loc1[1] - loc2[1])**2);

if __name__ == '__main__':
  scorer = ScoreBasedOnLog()
  scorer.processLogFile()
  scorer.scoreAccuracy()
