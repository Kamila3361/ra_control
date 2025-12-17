// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from ros_control_interfaces:msg/Joystick.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "ros_control_interfaces/msg/detail/joystick__rosidl_typesupport_introspection_c.h"
#include "ros_control_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "ros_control_interfaces/msg/detail/joystick__functions.h"
#include "ros_control_interfaces/msg/detail/joystick__struct.h"


// Include directives for member types
// Member `positions`
// Member `velocities`
#include "ros_control_interfaces/msg/motor_command.h"
// Member `positions`
// Member `velocities`
#include "ros_control_interfaces/msg/detail/motor_command__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  ros_control_interfaces__msg__Joystick__init(message_memory);
}

void ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_fini_function(void * message_memory)
{
  ros_control_interfaces__msg__Joystick__fini(message_memory);
}

size_t ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__size_function__Joystick__positions(
  const void * untyped_member)
{
  const ros_control_interfaces__msg__MotorCommand__Sequence * member =
    (const ros_control_interfaces__msg__MotorCommand__Sequence *)(untyped_member);
  return member->size;
}

const void * ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_const_function__Joystick__positions(
  const void * untyped_member, size_t index)
{
  const ros_control_interfaces__msg__MotorCommand__Sequence * member =
    (const ros_control_interfaces__msg__MotorCommand__Sequence *)(untyped_member);
  return &member->data[index];
}

void * ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_function__Joystick__positions(
  void * untyped_member, size_t index)
{
  ros_control_interfaces__msg__MotorCommand__Sequence * member =
    (ros_control_interfaces__msg__MotorCommand__Sequence *)(untyped_member);
  return &member->data[index];
}

void ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__fetch_function__Joystick__positions(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const ros_control_interfaces__msg__MotorCommand * item =
    ((const ros_control_interfaces__msg__MotorCommand *)
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_const_function__Joystick__positions(untyped_member, index));
  ros_control_interfaces__msg__MotorCommand * value =
    (ros_control_interfaces__msg__MotorCommand *)(untyped_value);
  *value = *item;
}

void ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__assign_function__Joystick__positions(
  void * untyped_member, size_t index, const void * untyped_value)
{
  ros_control_interfaces__msg__MotorCommand * item =
    ((ros_control_interfaces__msg__MotorCommand *)
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_function__Joystick__positions(untyped_member, index));
  const ros_control_interfaces__msg__MotorCommand * value =
    (const ros_control_interfaces__msg__MotorCommand *)(untyped_value);
  *item = *value;
}

bool ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__resize_function__Joystick__positions(
  void * untyped_member, size_t size)
{
  ros_control_interfaces__msg__MotorCommand__Sequence * member =
    (ros_control_interfaces__msg__MotorCommand__Sequence *)(untyped_member);
  ros_control_interfaces__msg__MotorCommand__Sequence__fini(member);
  return ros_control_interfaces__msg__MotorCommand__Sequence__init(member, size);
}

size_t ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__size_function__Joystick__velocities(
  const void * untyped_member)
{
  const ros_control_interfaces__msg__MotorCommand__Sequence * member =
    (const ros_control_interfaces__msg__MotorCommand__Sequence *)(untyped_member);
  return member->size;
}

const void * ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_const_function__Joystick__velocities(
  const void * untyped_member, size_t index)
{
  const ros_control_interfaces__msg__MotorCommand__Sequence * member =
    (const ros_control_interfaces__msg__MotorCommand__Sequence *)(untyped_member);
  return &member->data[index];
}

void * ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_function__Joystick__velocities(
  void * untyped_member, size_t index)
{
  ros_control_interfaces__msg__MotorCommand__Sequence * member =
    (ros_control_interfaces__msg__MotorCommand__Sequence *)(untyped_member);
  return &member->data[index];
}

void ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__fetch_function__Joystick__velocities(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const ros_control_interfaces__msg__MotorCommand * item =
    ((const ros_control_interfaces__msg__MotorCommand *)
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_const_function__Joystick__velocities(untyped_member, index));
  ros_control_interfaces__msg__MotorCommand * value =
    (ros_control_interfaces__msg__MotorCommand *)(untyped_value);
  *value = *item;
}

void ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__assign_function__Joystick__velocities(
  void * untyped_member, size_t index, const void * untyped_value)
{
  ros_control_interfaces__msg__MotorCommand * item =
    ((ros_control_interfaces__msg__MotorCommand *)
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_function__Joystick__velocities(untyped_member, index));
  const ros_control_interfaces__msg__MotorCommand * value =
    (const ros_control_interfaces__msg__MotorCommand *)(untyped_value);
  *item = *value;
}

bool ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__resize_function__Joystick__velocities(
  void * untyped_member, size_t size)
{
  ros_control_interfaces__msg__MotorCommand__Sequence * member =
    (ros_control_interfaces__msg__MotorCommand__Sequence *)(untyped_member);
  ros_control_interfaces__msg__MotorCommand__Sequence__fini(member);
  return ros_control_interfaces__msg__MotorCommand__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_member_array[2] = {
  {
    "positions",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_control_interfaces__msg__Joystick, positions),  // bytes offset in struct
    NULL,  // default value
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__size_function__Joystick__positions,  // size() function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_const_function__Joystick__positions,  // get_const(index) function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_function__Joystick__positions,  // get(index) function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__fetch_function__Joystick__positions,  // fetch(index, &value) function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__assign_function__Joystick__positions,  // assign(index, value) function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__resize_function__Joystick__positions  // resize(index) function pointer
  },
  {
    "velocities",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_control_interfaces__msg__Joystick, velocities),  // bytes offset in struct
    NULL,  // default value
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__size_function__Joystick__velocities,  // size() function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_const_function__Joystick__velocities,  // get_const(index) function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__get_function__Joystick__velocities,  // get(index) function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__fetch_function__Joystick__velocities,  // fetch(index, &value) function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__assign_function__Joystick__velocities,  // assign(index, value) function pointer
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__resize_function__Joystick__velocities  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_members = {
  "ros_control_interfaces__msg",  // message namespace
  "Joystick",  // message name
  2,  // number of fields
  sizeof(ros_control_interfaces__msg__Joystick),
  ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_member_array,  // message members
  ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_init_function,  // function to initialize message memory (memory has to be allocated)
  ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_type_support_handle = {
  0,
  &ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_ros_control_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, ros_control_interfaces, msg, Joystick)() {
  ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, ros_control_interfaces, msg, MotorCommand)();
  ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, ros_control_interfaces, msg, MotorCommand)();
  if (!ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_type_support_handle.typesupport_identifier) {
    ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &ros_control_interfaces__msg__Joystick__rosidl_typesupport_introspection_c__Joystick_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
