#!/usr/bin/env python

import rospy
import rostopic
from std_msgs.msg import String
from collections import defaultdict
import json
import requests
import rospy
import rostopic
from std_msgs.msg import String
import rosnode
import os
import sys
import rosservice
import xmlrpclib
import subprocess
import re
import roslib; roslib.load_manifest('nodelet')
import rospy
from datetime import datetime
from nodelet.srv import *
from std_msgs.msg import String

currentService = ""
currentReported = []
serviceExpeptions = []
noServiceIntermediator = []
oldnoServiceIntermediator = []

URL = "http://127.0.0.1:8000/data"


def accumulate_action_topics(self, nodes_in, edges_in, node_connections):
    '''takes topic nodes, edges and node connections.
    Returns topic nodes where action topics have been removed,
    edges where the edges to action topics have been removed, and
    a map with the connection to each virtual action topic node'''
    removal_nodes = []
    action_nodes = {}
    # do not manipulate incoming structures
    nodes = copy.copy(nodes_in)
    edges = copy.copy(edges_in)
    for n in nodes:
        if str(n).endswith('/feedback'):
            prefix = str(n)[:-len('/feedback')].strip()
            action_topic_nodes = []
            action_topic_edges_out = set()
            action_topic_edges_in = set()
            for suffix in ['/status', '/result', '/goal', '/cancel', '/feedback']:
                for n2 in nodes:
                    if str(n2).strip() == prefix + suffix:
                        action_topic_nodes.append(n2)
                        if n2 in node_connections:
                            action_topic_edges_out.update(node_connections[n2].outgoing)
                            action_topic_edges_in.update(node_connections[n2].incoming)
            if len(action_topic_nodes) == 5:
                # found action
                removal_nodes.extend(action_topic_nodes)
                for e in action_topic_edges_out:
                    if e in edges:
                        edges.remove(e)
                for e in action_topic_edges_in:
                    if e in edges:
                        edges.remove(e)
                action_nodes[prefix] = {'topics': action_topic_nodes,
                                        'outgoing': action_topic_edges_out,
                                        'incoming': action_topic_edges_in}
    for n in removal_nodes:
        nodes.remove(n)
    return nodes, edges, action_nodes


def response(req):
    sentinel = False
    x =  req._connection_header

    currentService = str(x['service'])  + "_prime"
    client = str(x['callerid'])
    srv = subprocess.Popen("rosservice type " +currentService + " | rossrv show", shell=True, stdout=subprocess.PIPE).stdout.read()
    serviceArguments = []
    serviceArgumentsValues = []
    serviceReturns = []
    serviceReturnsValues = []

    for line in srv.split('\n'):
        if line == '---':
            sentinel = True
            continue
        if sentinel == True and line != '':
            if '/' in line.split(' ')[0]:
                serviceExpeptions.append(currentService)
                continue
            serviceReturns.append(line.split(' ')[-1])
        else:
            if line != '':
                serviceArguments.append(line.split(' ')[-1])

    hasNoArguments =  True
    if str(rosservice.get_service_args(currentService)) != "":
        hasNoArguments = False
        for x in serviceArguments:
            exec ('serviceArgumentsValues.append(req.'+ str(x) +')')

    Response = rospy.ServiceProxy(currentService, rosservice.get_service_class_by_name(currentService))

    toChange = ['.', ':', ' ']
    time = str(datetime.now())
    time = time.translate(None, '-'.join(toChange))


    if hasNoArguments == False:
        exec generateReturn(serviceArgumentsValues)
        for x in serviceReturns:
            if re.match("^[A-Za-z0-9_-]*$", x) and x != '':
                if currentService in serviceExpeptions:
                    serviceReturnsValues.append(currentService)
                    break
                exec('serviceReturnsValues.append(toReturn.'+ str(x) +')')
    else:
        toReturn = Response()
        for x in serviceReturns:
            if re.match("^[A-Za-z0-9_-]*$", x) and x != '':
                if currentService in serviceExpeptions:
                    serviceReturnsValues.append(currentService)
                    break
                exec('serviceReturnsValues.append(toReturn.'+ str(x) +')')

    report = str(generateReportSrviceCalls(currentService,serviceArguments,serviceArgumentsValues,serviceReturns,serviceReturnsValues,client))
    currentReported.append(report)
    return toReturn

def generateReportSrviceCalls(service,serviceArguments, serviceArgumentsValues,serviceReturns,serviceReturnsValues, client):
    x = rosservice.get_service_headers(service,rosservice.get_service_uri(service))
    toReturn = {'srv':str(x['type']), 'client':client, 'server':str(rosservice.get_service_node(service)), 'service_name': service}

    reqSubReport = []
    respSubReport = {}
    for x in range (0,len(serviceArguments)):
        reqSubReport.append(str(serviceArgumentsValues[x]))
    # for x in range (0, len(serviceReturns)):
    #     if service in serviceExpeptions:
    #         respSubReport['ExtendedReport'] = 'ExtendedReport'
    #         break
    #     respSubReport[str(serviceReturns[x])] = str(serviceReturnsValues[x])
    toReturn['req'] = ','.join(reqSubReport)
    #toReturn['resp'] = respSubReport
    return toReturn

def generateReturn(serviceArgumentsValues):
    count = 0
    toExecute = 'toReturn = Response('
    for x in serviceArgumentsValues:
        count = count +1
        if count == len(serviceArgumentsValues):
            toExecute += str(x)+')'
        else:
            toExecute+= str(x)+','
    return toExecute

def newServiceHandler(service):
    primeState = False
    non_prime = "OPERATOR___"
    if service.split('_')[-1] == 'prime':
        primeState = True
        non_prime = non_prime +  service.split('_prime')[0]
        s = rospy.Service(non_prime,rosservice.get_service_class_by_name(str(service)),response)
    else:
        noServiceIntermediator.append(service)
    return 'Passed'

def get_current_services():
    caller_ide = '/handler'
    m = xmlrpclib.ServerProxy(os.environ['ROS_MASTER_URI'])
    code, msg, val = m.getSystemState(caller_ide)
    if(code ==1):
        pubs, subs, srvs = val
    else:
        print "call failed", code, msg
    return srvs


def parse_info_sub(info):
    reached_sub = False
    subscribers = []
    for l in info.splitlines():
        if reached_sub and not l:
            break
        elif reached_sub:
            parts = l.split(' ')
            if len(parts) < 3:
                rospy.loginfo("Something is wrong here!")
                continue
            subscribers.append(parts[2])
        elif l.startswith('Subscribers:'):
            reached_sub = True
    return subscribers


def parse_info_pub(info):
    reached_pub = False
    publishers = []
    for l in info.splitlines():
        if reached_pub and (not l or l.startswith('Subscribers:')):
            break
        elif reached_pub:
            parts = l.split(' ')
            if len(parts) < 3:
                rospy.loginfo("Something is wrong here!")
                continue
            publishers.append(parts[2])
        elif l.startswith('Publishers:'):
            reached_pub = True
    return publishers


def sendPub(new_publish):
    p = {}
    for topic in new_publish.keys():
        p[topic] = list(new_publish[topic])
    y = defaultdict(list)
    for key, values in p.iteritems():
        for value in values:
            y[value].append(key)

    for key in y.keys():
        new_key = key.replace("/", "__")
        y[new_key] = [item.replace("/", "__") for item in y.pop(key)]

    return y



def sendSub(new_publish):
    p = {}
    for topic in new_publish.keys():
        p[topic] = list(new_publish[topic])
    y = defaultdict(list)
    for key, values in p.iteritems():
        for value in values:
            y[value].append(key)

    for key in y.keys():
        new_key = key.replace("/", "__")
        y[new_key] = [item.replace("/", "__") for item in y.pop(key)]

    return y

def send_topics(topics):
    topics_dict = {}
    for topic, typ in topics:
        topics_dict[topic.replace("/", "__")] = typ
    return topics_dict


def send_nodes(nodes):
    x = {"nodes":[]}
    for item in nodes:
        if "nodelet_manager" in item:
            x[item] = rospy.ServiceProxy(item + "/list", NodeletList).call(NodeletListRequest()).nodelets

    flattened = [val for sublist in x.values() for val in sublist] + x.keys()
    for item in nodes:
        if item not in flattened:
            x["nodes"].append(item)

    y = {}
    for key in x.keys():
        new_key = key.replace("/", "__")
        y[new_key] = [item.replace("/", "__") for item in x[key]]

    return y


def arch():
    try:
        rospy.init_node('handler', anonymous=True)

        currentServices = []
        loggerCount = 0
        last_topics = []
        last_nodes = []
        last_publish = {}
        last_publish1 = {}
        currentTopics = []

        loggerCount = 0

        global currentReported
        global serviceExpeptions
        global noServiceIntermediator
        global oldnoServiceIntermediator


        service_dict = {}
        old_service_dict = {}
        length = 0
        updated = False
        oldReported = list()

        while not rospy.is_shutdown():
            new_topics = rospy.get_published_topics()
            new_nodes = rosnode.get_node_names()
            new_publish = {}
            new_publish1 = {}

            inc_topics = [item for item in new_topics if item not in last_topics]
            inc_nodes = [item for item in new_nodes if item not in last_nodes]
            inc_service_dict = {}
            inc_publish = {}
            inc_publish1 = {}
            inc_service_dict = {}
            inc_reported = {}

            for topic, typ in new_topics:
                info = rostopic.get_info_text(topic)
                subscribers = parse_info_sub(info)
                publishers = parse_info_pub(info)
                new_publish[topic] = set(subscribers)
                new_publish1[topic] = set(publishers)

                if (topic not in last_publish.keys()) or set(subscribers) != last_publish[topic]:
                    inc_publish[topic] = set(subscribers)

                if (topic not in last_publish1.keys()) or set(publishers) != last_publish1[topic]:
                    inc_publish1[topic] = set(publishers)


            try:
                for newService, Provider in get_current_services():
                    if not newService in currentServices:
                        currentServices.append(newService)
                        newServiceHandler(newService)
                        service_dict[newService] = [rosservice.get_service_type(newService), rosservice.get_service_args(newService)]
                        if (newService not in old_service_dict.keys()) or service_dict[newService] != old_service_dict[newService]:
                            inc_service_dict[newService] = [rosservice.get_service_type(newService), rosservice.get_service_args(newService)]
            except Exception as e:
                print e
                pass


            if old_service_dict != service_dict:
                old_service_dict = dict(service_dict)
                updated = True

            inc_reported = [item for item in currentReported if item not in oldReported]
            oldReported = list(currentReported)

            if len(inc_reported) !=  0:
                updated = True

            if noServiceIntermediator != oldnoServiceIntermediator:
                oldnoServiceIntermediator = list(noServiceIntermediator)
                print
                print
                print 'Services calls not being reported for these services: ' + str(noServiceIntermediator)

            if inc_topics or inc_nodes or inc_publish or  inc_publish1 != inc_service_dict or inc_reported:
                y = {}

                y["topics"] = send_topics(inc_topics)
                y["nodes"] = send_nodes(inc_nodes)
                y["pub"] = sendPub(inc_publish)
                y["sub"] = sendSub(inc_publish1)
                y["service"] = inc_service_dict
                y["calls"] = inc_reported


                last_nodes = list(new_nodes)
                last_topics = list(new_topics)
                last_publish = dict(new_publish)
                last_publish1 = dict(new_publish1)
                updated = False

                requests.get(URL, data=json.dumps(y))

    except Exception as e:
        print e
        pass

if __name__ == '__main__':
    try:
        arch()
    except rospy.ROSInterruptException:
        print e
        pass