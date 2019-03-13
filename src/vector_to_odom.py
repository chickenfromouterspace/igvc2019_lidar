#!/usr/bin/env python

import math
from math import sin, cos, pi

import rospy
import tf
import tf2_ros
import tf2_geometry_msgs
from nav_msgs.msg import Odometry
from std_msgs.msg import Header
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3, Vector3Stamped

class RPY:
        def __init__(self, rpy_topic="imu/rpy"):
            # Subscribe to the laser scan topic
            rpy_sub = rospy.Subscriber(rpy_topic, Vector3Stamped, self.on_rpy)

        def on_rpy(self, rpy):
            self.vector = rpy.vector
            # first, we'll publish the transform over tf
            odom_broadcaster.sendTransform(
                (self.vector.x, self.vector.y, 0.),
                odom_quat,
                current_time,
                "base_link",
                "odom"
            )
            print self.vector            

if __name__ == '__main__':

    rospy.init_node('odometry_publisher')

    odom_pub = rospy.Publisher("odom", Odometry, queue_size=50)
    odom_broadcaster = tf.TransformBroadcaster()
    rpy = RPY("imu/rpy")

    x = 0.0
    y = 0.0
    th = 0.0

    vx = 0.1
    vy = -0.1
    vth = 0.1

    current_time = rospy.Time.now()
    last_time = rospy.Time.now()

    r = rospy.Rate(1.0)
    while not rospy.is_shutdown():
        current_time = rospy.Time.now()

        # compute odometry in a typical way given the velocities of the robot
        dt = (current_time - last_time).to_sec()
        delta_x = (vx * cos(th) - vy * sin(th)) * dt
        delta_y = (vx * sin(th) + vy * cos(th)) * dt
        delta_th = vth * dt

        x += delta_x
        y += delta_y
        th += delta_th

        # since all odometry is 6DOF we'll need a quaternion created from yaw
        odom_quat = tf.transformations.quaternion_from_euler(0, 0, th)


        # next, we'll publish the odometry message over ROS
        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = "odom"

        # set the position
        odom.pose.pose = Pose(Point(x, y, 0.), Quaternion(*odom_quat))

        # set the velocity
        odom.child_frame_id = "base_link"
        odom.twist.twist = Twist(Vector3(vx, vy, 0), Vector3(0, 0, vth))

        # publish the message
        odom_pub.publish(odom)

        last_time = current_time
        r.sleep()

    rospy.spin()