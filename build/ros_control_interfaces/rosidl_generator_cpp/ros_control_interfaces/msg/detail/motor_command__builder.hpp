// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from ros_control_interfaces:msg/MotorCommand.idl
// generated code does not contain a copyright notice

#ifndef ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__BUILDER_HPP_
#define ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "ros_control_interfaces/msg/detail/motor_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace ros_control_interfaces
{

namespace msg
{

namespace builder
{

class Init_MotorCommand_value
{
public:
  explicit Init_MotorCommand_value(::ros_control_interfaces::msg::MotorCommand & msg)
  : msg_(msg)
  {}
  ::ros_control_interfaces::msg::MotorCommand value(::ros_control_interfaces::msg::MotorCommand::_value_type arg)
  {
    msg_.value = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ros_control_interfaces::msg::MotorCommand msg_;
};

class Init_MotorCommand_name
{
public:
  Init_MotorCommand_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MotorCommand_value name(::ros_control_interfaces::msg::MotorCommand::_name_type arg)
  {
    msg_.name = std::move(arg);
    return Init_MotorCommand_value(msg_);
  }

private:
  ::ros_control_interfaces::msg::MotorCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::ros_control_interfaces::msg::MotorCommand>()
{
  return ros_control_interfaces::msg::builder::Init_MotorCommand_name();
}

}  // namespace ros_control_interfaces

#endif  // ROS_CONTROL_INTERFACES__MSG__DETAIL__MOTOR_COMMAND__BUILDER_HPP_
