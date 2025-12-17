// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from ros_control_interfaces:msg/Joystick.idl
// generated code does not contain a copyright notice

#ifndef ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__STRUCT_H_
#define ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'positions'
// Member 'velocities'
#include "ros_control_interfaces/msg/detail/motor_command__struct.h"

/// Struct defined in msg/Joystick in the package ros_control_interfaces.
typedef struct ros_control_interfaces__msg__Joystick
{
  /// List of motors with goal positions
  ros_control_interfaces__msg__MotorCommand__Sequence positions;
  /// List of motors with goal velocities
  ros_control_interfaces__msg__MotorCommand__Sequence velocities;
} ros_control_interfaces__msg__Joystick;

// Struct for a sequence of ros_control_interfaces__msg__Joystick.
typedef struct ros_control_interfaces__msg__Joystick__Sequence
{
  ros_control_interfaces__msg__Joystick * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} ros_control_interfaces__msg__Joystick__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__STRUCT_H_
