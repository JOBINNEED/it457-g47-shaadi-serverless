# Shared settings for the stack scripts. Needs AWS CLI v2 signed in to account 705029438856.
REGION="${AWS_REGION:-ap-south-1}"
API_URL="${API_URL:-https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com}"
SERVING_FUNCTIONS=(shaadi-demo shaadi-ping shaadi-interest-api shaadi-moderate)
ALL_FUNCTIONS=("${SERVING_FUNCTIONS[@]}" shaadi-loadgen)
