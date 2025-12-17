// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from ros_control_interfaces:msg/Joystick.idl
// generated code does not contain a copyright notice

#ifndef ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__STRUCT_HPP_
#define ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'positions'
// Member 'velocities'
#include "ros_control_interfaces/msg/detail/motor_command__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__ros_control_interfaces__msg__Joystick __attribute__((deprecated))
#else
# define DEPRECATED__ros_control_interfaces__msg__Joystick __declspec(deprecated)
#endif

namespace ros_control_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Joystick_
{
  using Type = Joystick_<ContainerAllocator>;

  explicit Joystick_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit Joystick_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _positions_type =
    std::vector<ros_control_interfaces::msg::MotorCommand_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<ros_control_interfaces::msg::MotorCommand_<ContainerAllocator>>>;
  _positions_type positions;
  using _velocities_type =
    std::vector<ros_control_interfaces::msg::MotorCommand_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<ros_control_interfaces::msg::MotorCommand_<ContainerAllocator>>>;
  _velocities_type velocities;

  // setters for named parameter idiom
  Type & set__positions(
    const std::vector<ros_control_interfaces::msg::MotorCommand_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<ros_control_interfaces::msg::MotorCommand_<ContainerAllocator>>> & _arg)
  {
    this->positions = _arg;
    return *this;
  }
  Type & set__velocities(
    const std::vector<ros_control_interfaces::msg::MotorCommand_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<ros_control_interfaces::msg::MotorCommand_<ContainerAllocator>>> & _arg)
  {
    this->velocities = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    ros_control_interfaces::msg::Joystick_<ContainerAllocator> *;
  using ConstRawPtr =
    const ros_control_interfaces::msg::Joystick_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<ros_control_interfaces::msg::Joystick_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<ros_control_interfaces::msg::Joystick_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      ros_control_interfaces::msg::Joystick_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<ros_control_interfaces::msg::Joystick_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      ros_control_interfaces::msg::Joystick_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<ros_control_interfaces::msg::Joystick_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<ros_control_interfaces::msg::Joystick_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<ros_control_interfaces::msg::Joystick_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__ros_control_interfaces__msg__Joystick
    std::shared_ptr<ros_control_interfaces::msg::Joystick_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__ros_control_interfaces__msg__Joystick
    std::shared_ptr<ros_control_interfaces::msg::Joystick_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Joystick_ & other) const
  {
    if (this->positions != other.positions) {
      return false;
    }
    if (this->velocities != other.velocities) {
      return false;
    }
    return true;
  }
  bool operator!=(const Joystick_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Joystick_

// alias to use template instance with default allocator
using Joystick =
  ros_control_interfaces::msg::Joystick_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace ros_control_interfaces

#endif  // ROS_CONTROL_INTERFACES__MSG__DETAIL__JOYSTICK__STRUCT_HPP_
