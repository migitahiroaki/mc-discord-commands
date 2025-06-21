from typing import Literal, TypedDict
from venv import logger
from boto3 import client  # type: ignore
from logging import getLogger

logger = getLogger(__name__)


class InstanceStateChange(TypedDict):
    current_state_name: str
    previous_state_name: str


class Ec2Instance:
    """SDK Wrapper"""

    def __init__(self, instance_id: str, region_name: str):
        self.client = client("ec2", region_name=region_name)
        self.instance_id = instance_id

    def _change_instance_state(
        self, action: Literal["start", "stop"]
    ) -> InstanceStateChange:
        """Change the state of the EC2 instance and return the state change information."""
        if action == "start":
            instances = self.client.start_instances(InstanceIds=[self.instance_id])[
                "StartingInstances"
            ]
        elif action == "stop":
            instances = self.client.stop_instances(InstanceIds=[self.instance_id])[
                "StoppingInstances"
            ]
        else:
            raise ValueError("Unsupported action")
        if len(instances) != 1:
            logger.error(instances)
            raise ValueError("Instance ID is not unique")
        instance = instances[0]
        return InstanceStateChange(
            current_state_name=f'{instance.get("CurrentState", {}).get("Name")}',
            previous_state_name=f'{instance.get("PreviousState", {}).get("Name")}',
        )

    def start(self) -> InstanceStateChange:
        """Start the EC2 instance and return the state change information."""
        return self._change_instance_state("start")

    def stop(self) -> InstanceStateChange:
        """Stop the EC2 instance and return the state change information."""
        return self._change_instance_state("stop")
