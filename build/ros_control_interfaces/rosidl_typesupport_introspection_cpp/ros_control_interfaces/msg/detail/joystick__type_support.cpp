// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from ros_control_interfaces:msg/Joystick.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "ros_control_interfaces/msg/detail/joystick__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace ros_control_interfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void Joystick_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) ros_control_interfaces::msg::Joystick(_init);
}

void Joystick_fini_function(void * message_memory)
{
  auto typed_message = static_cast<ros_control_interfaces::msg::Joystick *>(message_memory);
  typed_message->~Joystick();
}

size_t size_function__Joystick__positions(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<ros_control_interfaces::msg::MotorCommand> *>(untyped_member);
  return member->size();
}

const void * get_const_function__Joystick__positions(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<ros_control_interfaces::msg::MotorCommand> *>(untyped_member);
  return &member[index];
}

void * get_function__Joystick__positions(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<ros_control_interfaces::msg::MotorCommand> *>(untyped_member);
  return &member[index];
}

void fetch_function__Joystick__positions(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const ros_control_interfaces::msg::MotorCommand *>(
    get_const_function__Joystick__positions(untyped_member, index));
  auto & value = *reinterpret_cast<ros_control_interfaces::msg::MotorCommand *>(untyped_value);
  value = item;
}

void assign_function__Joystick__positions(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<ros_control_interfaces::msg::MotorCommand *>(
    get_function__Joystick__positions(untyped_member, index));
  const auto & value = *reinterpret_cast<const ros_control_interfaces::msg::MotorCommand *>(untyped_value);
  item = value;
}

void resize_function__Joystick__positions(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<ros_control_interfaces::msg::MotorCommand> *>(untyped_member);
  member->resize(size);
}

size_t size_function__Joystick__velocities(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<ros_control_interfaces::msg::MotorCommand> *>(untyped_member);
  return member->size();
}

const void * get_const_function__Joystick__velocities(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<ros_control_interfaces::msg::MotorCommand> *>(untyped_member);
  return &member[index];
}

void * get_function__Joystick__velocities(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<ros_control_interfaces::msg::MotorCommand> *>(untyped_member);
  return &member[index];
}

void fetch_function__Joystick__velocities(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const ros_control_interfaces::msg::MotorCommand *>(
    get_const_function__Joystick__velocities(untyped_member, index));
  auto & value = *reinterpret_cast<ros_control_interfaces::msg::MotorCommand *>(untyped_value);
  value = item;
}

void assign_function__Joystick__velocities(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<ros_control_interfaces::msg::MotorCommand *>(
    get_function__Joystick__velocities(untyped_member, index));
  const auto & value = *reinterpret_cast<const ros_control_interfaces::msg::MotorCommand *>(untyped_value);
  item = value;
}

void resize_function__Joystick__velocities(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<ros_control_interfaces::msg::MotorCommand> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember Joystick_message_member_array[2] = {
  {
    "positions",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<ros_control_interfaces::msg::MotorCommand>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_control_interfaces::msg::Joystick, positions),  // bytes offset in struct
    nullptr,  // default value
    size_function__Joystick__positions,  // size() function pointer
    get_const_function__Joystick__positions,  // get_const(index) function pointer
    get_function__Joystick__positions,  // get(index) function pointer
    fetch_function__Joystick__positions,  // fetch(index, &value) function pointer
    assign_function__Joystick__positions,  // assign(index, value) function pointer
    resize_function__Joystick__positions  // resize(index) function pointer
  },
  {
    "velocities",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<ros_control_interfaces::msg::MotorCommand>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_control_interfaces::msg::Joystick, velocities),  // bytes offset in struct
    nullptr,  // default value
    size_function__Joystick__velocities,  // size() function pointer
    get_const_function__Joystick__velocities,  // get_const(index) function pointer
    get_function__Joystick__velocities,  // get(index) function pointer
    fetch_function__Joystick__velocities,  // fetch(index, &value) function pointer
    assign_function__Joystick__velocities,  // assign(index, value) function pointer
    resize_function__Joystick__velocities  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers Joystick_message_members = {
  "ros_control_interfaces::msg",  // message namespace
  "Joystick",  // message name
  2,  // number of fields
  sizeof(ros_control_interfaces::msg::Joystick),
  Joystick_message_member_array,  // message members
  Joystick_init_function,  // function to initialize message memory (memory has to be allocated)
  Joystick_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t Joystick_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Joystick_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace ros_control_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<ros_control_interfaces::msg::Joystick>()
{
  return &::ros_control_interfaces::msg::rosidl_typesupport_introspection_cpp::Joystick_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, ros_control_interfaces, msg, Joystick)() {
  return &::ros_control_interfaces::msg::rosidl_typesupport_introspection_cpp::Joystick_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
