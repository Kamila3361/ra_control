// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from ros_control_interfaces:msg/Joystick.idl
// generated code does not contain a copyright notice

#ifndef ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__BUILDER_HPP_
#define ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "ros_control_interfaces/msg/detail/joystick__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace ros_control_interfaces
{

namespace msg
{

namespace builder
{

class Init_Joystick_velocities
{
public:
  explicit Init_Joystick_velocities(::ros_control_interfaces::msg::Joystick & msg)
  : msg_(msg)
  {}
  ::ros_control_interfaces::msg::Joystick velocities(::ros_control_interfaces::msg::Joystick::_velocities_type arg)
  {
    msg_.velocities = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ros_control_interfaces::msg::Joystick msg_;
};

class Init_Joystick_positions
{
public:
  Init_Joystick_positions()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Joystick_velocities positions(::ros_control_interfaces::msg::Joystick::_positions_type arg)
  {
    msg_.positions = std::move(arg);
    return Init_Joystick_velocities(msg_);
  }

private:
  ::ros_control_interfaces::msg::Joystick msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::ros_control_interfaces::msg::Joystick>()
{
  return ros_control_interfaces::msg::builder::Init_Joystick_positions();
}

}  // namespace ros_control_interfaces

#endif  // ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__BUILDER_HPP_
