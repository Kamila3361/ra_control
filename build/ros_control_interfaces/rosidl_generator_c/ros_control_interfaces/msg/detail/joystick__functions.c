// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from ros_control_interfaces:msg/Joystick.idl
// generated code does not contain a copyright notice
#include "ros_control_interfaces/msg/detail/joystick__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `positions`
// Member `velocities`
#include "ros_control_interfaces/msg/detail/motor_command__functions.h"

bool
ros_control_interfaces__msg__Joystick__init(ros_control_interfaces__msg__Joystick * msg)
{
  if (!msg) {
    return false;
  }
  // positions
  if (!ros_control_interfaces__msg__MotorCommand__Sequence__init(&msg->positions, 0)) {
    ros_control_interfaces__msg__Joystick__fini(msg);
    return false;
  }
  // velocities
  if (!ros_control_interfaces__msg__MotorCommand__Sequence__init(&msg->velocities, 0)) {
    ros_control_interfaces__msg__Joystick__fini(msg);
    return false;
  }
  return true;
}

void
ros_control_interfaces__msg__Joystick__fini(ros_control_interfaces__msg__Joystick * msg)
{
  if (!msg) {
    return;
  }
  // positions
  ros_control_interfaces__msg__MotorCommand__Sequence__fini(&msg->positions);
  // velocities
  ros_control_interfaces__msg__MotorCommand__Sequence__fini(&msg->velocities);
}

bool
ros_control_interfaces__msg__Joystick__are_equal(const ros_control_interfaces__msg__Joystick * lhs, const ros_control_interfaces__msg__Joystick * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // positions
  if (!ros_control_interfaces__msg__MotorCommand__Sequence__are_equal(
      &(lhs->positions), &(rhs->positions)))
  {
    return false;
  }
  // velocities
  if (!ros_control_interfaces__msg__MotorCommand__Sequence__are_equal(
      &(lhs->velocities), &(rhs->velocities)))
  {
    return false;
  }
  return true;
}

bool
ros_control_interfaces__msg__Joystick__copy(
  const ros_control_interfaces__msg__Joystick * input,
  ros_control_interfaces__msg__Joystick * output)
{
  if (!input || !output) {
    return false;
  }
  // positions
  if (!ros_control_interfaces__msg__MotorCommand__Sequence__copy(
      &(input->positions), &(output->positions)))
  {
    return false;
  }
  // velocities
  if (!ros_control_interfaces__msg__MotorCommand__Sequence__copy(
      &(input->velocities), &(output->velocities)))
  {
    return false;
  }
  return true;
}

ros_control_interfaces__msg__Joystick *
ros_control_interfaces__msg__Joystick__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  ros_control_interfaces__msg__Joystick * msg = (ros_control_interfaces__msg__Joystick *)allocator.allocate(sizeof(ros_control_interfaces__msg__Joystick), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(ros_control_interfaces__msg__Joystick));
  bool success = ros_control_interfaces__msg__Joystick__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
ros_control_interfaces__msg__Joystick__destroy(ros_control_interfaces__msg__Joystick * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    ros_control_interfaces__msg__Joystick__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
ros_control_interfaces__msg__Joystick__Sequence__init(ros_control_interfaces__msg__Joystick__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  ros_control_interfaces__msg__Joystick * data = NULL;

  if (size) {
    data = (ros_control_interfaces__msg__Joystick *)allocator.zero_allocate(size, sizeof(ros_control_interfaces__msg__Joystick), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = ros_control_interfaces__msg__Joystick__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        ros_control_interfaces__msg__Joystick__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
ros_control_interfaces__msg__Joystick__Sequence__fini(ros_control_interfaces__msg__Joystick__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      ros_control_interfaces__msg__Joystick__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

ros_control_interfaces__msg__Joystick__Sequence *
ros_control_interfaces__msg__Joystick__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  ros_control_interfaces__msg__Joystick__Sequence * array = (ros_control_interfaces__msg__Joystick__Sequence *)allocator.allocate(sizeof(ros_control_interfaces__msg__Joystick__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = ros_control_interfaces__msg__Joystick__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
ros_control_interfaces__msg__Joystick__Sequence__destroy(ros_control_interfaces__msg__Joystick__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    ros_control_interfaces__msg__Joystick__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
ros_control_interfaces__msg__Joystick__Sequence__are_equal(const ros_control_interfaces__msg__Joystick__Sequence * lhs, const ros_control_interfaces__msg__Joystick__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!ros_control_interfaces__msg__Joystick__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
ros_control_interfaces__msg__Joystick__Sequence__copy(
  const ros_control_interfaces__msg__Joystick__Sequence * input,
  ros_control_interfaces__msg__Joystick__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(ros_control_interfaces__msg__Joystick);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    ros_control_interfaces__msg__Joystick * data =
      (ros_control_interfaces__msg__Joystick *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!ros_control_interfaces__msg__Joystick__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          ros_control_interfaces__msg__Joystick__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!ros_control_interfaces__msg__Joystick__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
