# EncoderStamped.msg
# Encoder readings from differential drive robot

std_msgs/Header header

int32 left_encoder   # Left wheel encoder ticks
int32 right_encoder  # Right wheel encoder ticks
int32 left_velocity  # Left wheel velocity in 0.01 [rev/min]
int32 right_velocity # Right wheel velocity in 0.01 [rev/min]