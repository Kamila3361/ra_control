// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ros_control_interfaces:msg/MotorCommand.idl
// generated code does not contain a copyright notice

#ifndef ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__TRAITS_HPP_
#define ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "ros_control_interfaces/msg/detail/motor_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace ros_control_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const MotorCommand & msg,
  std::ostream & out)
{
  out << "{";
  // member: name
  {
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << ", ";
  }

  // member: value
  {
    out << "value: ";
    rosidl_generator_traits::value_to_yaml(msg.value, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MotorCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << "\n";
  }

  // member: value
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "value: ";
    rosidl_generator_traits::value_to_yaml(msg.value, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MotorCommand & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace ros_control_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use ros_control_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const ros_control_interfaces::msg::MotorCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  ros_control_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use ros_control_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const ros_control_interfaces::msg::MotorCommand & msg)
{
  return ros_control_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<ros_control_interfaces::msg::MotorCommand>()
{
  return "ros_control_interfaces::msg::MotorCommand";
}

template<>
inline const char * name<ros_control_interfaces::msg::MotorCommand>()
{
  return "ros_control_interfaces/msg/MotorCommand";
}

template<>
struct has_fixed_size<ros_control_interfaces::msg::MotorCommand>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ros_control_interfaces::msg::MotorCommand>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ros_control_interfaces::msg::MotorCommand>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__TRAITS_HPP_
