#!/usr/bin/env python
"""Dead man's switch trigger that activates when check-ins stop."""

import time
from datetime import datetime, timezone

from helpers.loghelpers import LOG
from helpers.mailhelpers import sendmail
from validators.validators import (
    valid_amount,
    valid_email,
    valid_phase,
    valid_timestamp,
)

from .trigger import Trigger
from .triggertype import TriggerType


class DeadMansSwitchTrigger(Trigger):
    """Dead man's switch trigger that activates when check-ins stop."""
    def __init__(self, trigger_id):
        super().__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.DEADMANSSWITCH
        self.timeout = None
        self.warning_email = None
        self.phase = 0
        self.activation_time = None

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        if self.timeout is None or self.activation_time is None or self.warning_email is None:
            return False

        email_variables = {'activation_time': datetime.fromtimestamp(self.activation_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

        if self.phase == SwitchPhase.PHASE_1 and int(time.time()) >= int(self.activation_time - (self.timeout * 0.5)):
            # 50% of timeout has passed, send first warning and move to phase 2
            self.phase = SwitchPhase.PHASE_2
            LOG.info(f"Dead Man's Switch {self.id} is now in phase {self.phase}, sending first warning email")
            sendmail(self.warning_email, f"First warning: Dead Man's Switch {self.id} at 50 percent", 'deadmansswitchwarning', email_variables)
            self.save()

        if self.phase == SwitchPhase.PHASE_2 and int(time.time()) >= int(self.activation_time - (self.timeout * 0.25)):
            # 75% of timeout has passed, send second warning and move to phase 3
            self.phase = SwitchPhase.PHASE_3
            LOG.info(f"Dead Man's Switch {self.id} is now in phase {self.phase}, sending second warning email")
            sendmail(self.warning_email, f"Second warning: Dead Man's Switch {self.id} at 75 percent", 'deadmansswitchwarning', email_variables)
            self.save()

        if self.phase == SwitchPhase.PHASE_3 and int(time.time()) >= int(self.activation_time - (self.timeout * 0.1)):
            # 90% of timeout has passed, send final warning and move to phase 4
            self.phase = SwitchPhase.PHASE_4
            LOG.info(f"Dead Man's Switch {self.id} is now in phase {self.phase}, sending final warning email")
            sendmail(self.warning_email, f"Final warning: Dead Man's Switch {self.id} at 90 percent", 'deadmansswitchwarning', email_variables)
            self.save()

        if self.phase == SwitchPhase.PHASE_4 and int(time.time()) >= int(self.activation_time):
            # 90% of timeout has passed, send final warning and move to phase 4
            self.phase = SwitchPhase.PHASE_5
            LOG.info(f"Dead Man's Switch {self.id} is now in phase {self.phase}, activating trigger")
            sendmail(self.warning_email, f"Dead Man's Switch {self.id} activated", 'deadmansswitchactivated', email_variables)
            self.save()

        return self.phase == SwitchPhase.PHASE_5

    def arm(self):
        """Arm."""
        if self.phase == SwitchPhase.PHASE_0:
            self.phase = SwitchPhase.PHASE_1
            self.activation_time = int(time.time()) + self.timeout
            LOG.info("Dead Man's Switch {} has been armed, will activate in {} seconds on {}".format(self.id, self.timeout, datetime.fromtimestamp(self.activation_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
            email_variables = {'activation_time': datetime.fromtimestamp(self.activation_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}
            sendmail(self.warning_email, f"Warning: Dead Man's Switch {self.id} has been armed", 'deadmansswitchwarning', email_variables)
            self.save()

    def configure(self, **config):
        """Configure."""
        super().configure(**config)

        if 'timeout' in config and valid_amount(config['timeout']):
            self.timeout = config['timeout']

        if 'warning_email' in config and valid_email(config['warning_email']):
            self.warning_email = config['warning_email']

        if 'phase' in config and valid_phase(config['phase']):
            self.phase = config['phase']

        if 'activation_time' in config and valid_timestamp(config['activation_time']):
            self.activation_time = config['activation_time']

        if 'reset' in config and config['reset'] is True:
            self.triggered = False
            self.status = 'Active'

            # Reset a Dead Man's Switch trigger if needed
            if self.activation_time is not None and self.timeout is not None and self.phase >= 1:
                self.activation_time = int(time.time()) + self.timeout
                self.phase = 1
                LOG.info(f"Dead Man's Switch {self.id} has been reset, will activate in {self.timeout} seconds on {datetime.fromtimestamp(self.activation_time, tz=timezone.utc)}")

    def json_encodable(self):
        """Json encodable."""
        ret = super().json_encodable()

        ret.update({
            'timeout': self.timeout,
            'warning_email': self.warning_email,
            'phase': self.phase,
            'activation_time': self.activation_time})
        return ret


class SwitchPhase:
    """Enumeration of dead man's switch phases (unarmed, armed, warning sent)."""
    PHASE_0 = 0  # The dead man's switch is not armed yet
    PHASE_1 = 1  # The dead man's switch has been armed
    PHASE_2 = 2  # The dead man's switch has been armed and 1 warning has been sent (50% of timeout has passed)
    PHASE_3 = 3  # The dead man's switch has been armed and 2 warnings has been sent (75% of timeout has passed)
    PHASE_4 = 4  # The dead man's switch has been armed and 3 warnings has been sent (90% of timeout has passed)
    PHASE_5 = 5  # The dead man's switch has been activated
