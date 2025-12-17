// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ros_control_interfaces:msg/Joystick.idl
// generated code does not contain a copyright notice

#ifndef ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__TRAITS_HPP_
#define ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "ros_control_interfaces/msg/detail/joystick__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'positions'
// Member 'velocities'
#include "ros_control_interfaces/msg/detail/motor_command__traits.hpp"

namespace ros_control_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Joystick & msg,
  std::ostream & out)
{
  out << "{";
  // member: positions
  {
    if (msg.positions.size() == 0) {
      out << "positions: []";
    } else {
      out << "positions: [";
      size_t pending_items = msg.positions.size();
      for (auto item : msg.positions) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: velocities
  {
    if (msg.velocities.size() == 0) {
      out << "velocities: []";
    } else {
      out << "velocities: [";
      size_t pending_items = msg.velocities.size();
      for (auto item : msg.velocities) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Joystick & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: positions
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.positions.size() == 0) {
      out << "positions: []\n";
    } else {
      out << "positions:\n";
      for (auto item : msg.positions) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: velocities
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.velocities.size() == 0) {
      out << "velocities: []\n";
    } else {
      out << "velocities:\n";
      for (auto item : msg.velocities) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Joystick & msg, bool use_flow_style = false)
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
  const ros_control_interfaces::msg::Joystick & msg,
  std::ostream & out, size_t indentation = 0)
{
  ros_control_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use ros_control_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const ros_control_interfaces::msg::Joystick & msg)
{
  return ros_control_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<ros_control_interfaces::msg::Joystick>()
{
  return "ros_control_interfaces::msg::Joystick";
}

template<>
inline const char * name<ros_control_interfaces::msg::Joystick>()
{
  return "ros_control_interfaces/msg/Joystick";
}

template<>
struct has_fixed_size<ros_control_interfaces::msg::Joystick>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ros_control_interfaces::msg::Joystick>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ros_control_interfaces::msg::Joystick>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__TRAITS_HPP_
