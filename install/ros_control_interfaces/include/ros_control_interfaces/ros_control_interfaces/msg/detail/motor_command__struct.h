// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from ros_control_interfaces:msg/MotorCommand.idl
// generated code does not contain a copyright notice

#ifndef ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__STRUCT_H_
#define ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'name'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/MotorCommand in the package ros_control_interfaces.
typedef struct ros_control_interfaces__msg__MotorCommand
{
  /// Motor name (e.g., "left_arm", "right_wheel")
  rosidl_runtime_c__String name;
  /// Position or velocity value
  int32_t value;
} ros_control_interfaces__msg__MotorCommand;

// Struct for a sequence of ros_control_interfaces__msg__MotorCommand.
typedef struct ros_control_interfaces__msg__MotorCommand__Sequence
{
  ros_control_interfaces__msg__MotorCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} ros_control_interfaces__msg__MotorCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__STRUCT_H_
