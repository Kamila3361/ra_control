# EncoderStamped.msg
# Encoder readings from differential drive robot

std_msgs/Header header

int32 left_encoder   # Left wheel encoder ticks
int32 right_encoder  # Right wheel encoder ticks
