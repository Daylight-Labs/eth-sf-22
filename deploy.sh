#!/usr/bin/env bash

set -eou pipefail

####################################################
# Usage:
#
# To deploy to prod:
#
#    ./deploy.sh --env=prod
#
# To deploy to staging:
#
#    ./deploy.sh --env=staging
####################################################

######################################
# Functions for printing text in color
######################################
print_in_cyan() {
    printf "\x1B[36m%b\x1B[0m" "$*"
}

print_in_yellow() {
    printf "\x1B[33m%b\x1B[0m" "$*"
}

print_in_green() {
    printf "\x1B[32m%b\x1B[0m" "$*"
}

print_in_red() {
    printf "\x1B[31m%b\x1B[0m" "$*"
}

show_help() {
    printf "./deploy.sh\n\n"
    printf "Deploy the API\n\n"
    printf "Arguments\n\n"
    printf "  --env:  environment to deploy the service to\n"
    printf "\nExample:\n\n"
    printf "  ./deploy.sh --env=prod\n\n"
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


    -h|--help|help)
        show_help
        exit 0
        ;;

    *)
        print_in_red "\n${1} is not a valid command line option\n\n"
        show_help
        exit 1
esac
done


# Warn about deploying a non-master branch to production
CURRENT_BRANCH="$(git branch --show-current)"
if [ "$ENVIRONMENT" == "prod" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    print_in_yellow "WARNING! You are not on the master branch, you are on branch: $CURRENT_BRANCH.\n"
    read -p "Continue? (Y/N): " -n 1 -r

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi


# Warn if branch is not up-to-date with the remote
git fetch -v --dry-run | grep -q -v 'Already up-to-date.' && BRANCH_BEHIND=true
if [ "$ENVIRONMENT" == "prod" ] && [ BRANCH_BEHIND = true ]; then
    print_in_yellow "WARNING! You are not up to date with current branch."
    read -p "Continue? (Y/N): " -n 1 -r

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Login to aws ECR (container repo)
aws --region us-west-2 ecr get-login-password | docker login --username AWS --password-stdin 440023943937.dkr.ecr.us-west-2.amazonaws.com


DATE=`date -u +"%Y-%m-%dT%H-%M-%S"`
TAGS=( $DATE latest )

for TAG in "${TAGS[@]}"
do
    export NGINX_IMAGE="440023943937.dkr.ecr.us-west-2.amazonaws.com/${ENVIRONMENT}-background-network-api-nginx:${TAG}"
    export DJANGO_IMAGE="440023943937.dkr.ecr.us-west-2.amazonaws.com/${ENVIRONMENT}-background-network-api-django:${TAG}"

    # Generate static files for mounting into the nginx image.
    # TODO: Maybe don't store static files in nginx image? Need to handle rollbacks gracefully first
    docker-compose run --rm django python manage.py collectstatic --noinput

    # Build the docker images
    BUILD_TARGET=main docker-compose build nginx django

    # Push docker image with tag of current date
    docker-compose push nginx django
done

# Redeploy
aws ecs update-service \
    --force-new-deployment \
    --service $ENVIRONMENT-web-app-api \
    --cluster $ENVIRONMENT-webservices
