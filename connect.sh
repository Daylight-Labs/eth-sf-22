#!/usr/bin/env bash

set -eou pipefail

####################################################
# Open shell in running ECS Container
#
# Usage:
#
# To open a prod shell:
#
#    ./connect.sh --env=prod
#
# To deploy to staging:
#
#    ./deploy.sh --env=staging
#
# By default, a shell is opened in a running django container.
#
# To open a shell in a running nginx container, set --container=nginx:
#
#     ./connect.sh --env=prod --container=nginx
#
# To use a specific AWS_PROFILE to connect, use the --profile argument:
#
#     ./connect.sh --profile=skyline
####################################################

# If this script is not being run in a container, use docker-compose to execute this script instead...
if command -v docker-compose &> /dev/null; then
    docker-compose run --rm ecs-shell ./connect.sh "$@"
    exit
fi

######################################
# Functions for printing text in color
######################################
print_in_cyan() {
    printf "\x1B[36m%b\x1B[0m" "$*"
}

print_in_red() {
    printf "\x1B[31m%b\x1B[0m" "$*"
}

show_help() {
    printf "./connect.sh\n\n"
    printf "Connect to a running ECS container for the API\n\n"
    printf "Arguments\n\n"
    printf "  --env:        environment to connect to\n"
    printf "  --container:  container to connect to (defaults to django)\n"
    printf "\nExample:\n\n"
    printf "  ./connect.sh --env=prod\n\n"
}

################################
# Add the command-line arguments
################################
while (($#))
do
case "$1" in
    # Add support for --env <environment>
    --env)
        export ENVIRONMENT="$2"
        shift # past argument
        shift # past value
        ;;

    # Add support for --env=<environment>
    --env=*)
        export ENVIRONMENT="${1#*=}"
        shift
        ;;

    # Add support for --container <environment>
    --container)
        export CONTAINER="$2"
        shift # past argument
        shift # past value
        ;;
    --container=*)
        export CONTAINER="${1#*=}"
        shift
        ;;

    --profile)
        export AWS_PROFILE="$2"
        shift # past argument
        shift # past value
        ;;
    --profile=*)
        export AWS_PROFILE="${1#*=}"
        shift
        ;;

    --help|help|help)
        show_help
        exit 0
        ;;

    *)
        print_in_red "\n${1} is not a valid command line option\n\n"
        show_help
        exit 1
        ;;
esac
done

if [ -z "${ENVIRONMENT:-}" ]; then
    print_in_red "Environment must be specified, e.g. --env=prod\n\n"
    show_help
    exit 1
fi

export CONTAINER=django
export AWS_DEFAULT_REGION=us-west-2

# Get arn of a running task for the ECS service
export TASK_ARN="$(aws ecs list-tasks --cluster "${ENVIRONMENT}"-webservices --service-name "${ENVIRONMENT}"-web-app-api --desired-status RUNNING --query 'taskArns[0]' --output=text)"

print_in_cyan "Connecting to ${ENVIRONMENT} ${CONTAINER} container...\n"
aws ecs execute-command \
    --interactive \
    --container=$CONTAINER \
    --cluster ${ENVIRONMENT}-webservices \
    --task $TASK_ARN \
    --command "bash"
