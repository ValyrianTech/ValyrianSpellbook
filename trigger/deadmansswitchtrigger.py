#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime

from trigger import Trigger
from triggertype import TriggerType
from mailhelpers import sendmail


class DeadMansSwitchTrigger(Trigger):
    def __init__(self, trigger_id):
        super(DeadMansSwitchTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.DEADMANSSWITCH

    def conditions_fulfilled(self):
        if self.timeout is None or self.activation_time is None or self.warning_email is None:
            return False

        if self.phase == SwitchPhase.PHASE_1 and int(time.time()) >= int(self.activation_time - (self.timeout * 0.5)):
            # 50% of timeout has passed, send first warning and move to phase 2
            self.phase = SwitchPhase.PHASE_2
            logging.getLogger('Spellbook').info("Dead Man's Switch %s is now in phase %s, sending first warning email" % (self.id, self.phase))
            sendmail(self.warning_email, "First warning: Dead Man's Switch %s at 50 percent" % self.id, 'deadmansswitchwarning')
            self.save()

        if self.phase == SwitchPhase.PHASE_2 and int(time.time()) >= int(self.activation_time - (self.timeout * 0.25)):
            # 75% of timeout has passed, send second warning and move to phase 3
            self.phase = SwitchPhase.PHASE_3
            logging.getLogger('Spellbook').info("Dead Man's Switch %s is now in phase %s, sending second warning email" % (self.id, self.phase))
            sendmail(self.warning_email, "Second warning: Dead Man's Switch %s at 75 percent" % self.id, 'deadmansswitchwarning')
            self.save()

        if self.phase == SwitchPhase.PHASE_3 and int(time.time()) >= int(self.activation_time - (self.timeout * 0.1)):
            # 90% of timeout has passed, send final warning and move to phase 4
            self.phase = SwitchPhase.PHASE_4
            logging.getLogger('Spellbook').info("Dead Man's Switch %s is now in phase %s, sending final warning email" % (self.id, self.phase))
            sendmail(self.warning_email, "Final warning: Dead Man's Switch %s at 90 percent" % self.id, 'deadmansswitchwarning')
            self.save()

        if self.phase == SwitchPhase.PHASE_4 and int(time.time()) >= int(self.activation_time):
            # 90% of timeout has passed, send final warning and move to phase 4
            self.phase = SwitchPhase.PHASE_5
            logging.getLogger('Spellbook').info("Dead Man's Switch %s is now in phase %s, activating trigger" % (self.id, self.phase))
            sendmail(self.warning_email, "Dead Man's Switch %s activated" % self.id, 'deadmansswitchactivated')
            self.save()

        return self.phase == SwitchPhase.PHASE_5

    def arm(self):
        if self.phase == SwitchPhase.PHASE_0:
            self.phase = SwitchPhase.PHASE_1
            self.activation_time = int(time.time()) + self.timeout
            logging.getLogger('Spellbook').info("Dead Man's Switch %s has been armed, will activate in %s seconds on %s" % (self.id, self.timeout, datetime.fromtimestamp(self.activation_time)))
            sendmail(self.warning_email, "Warning: Dead Man's Switch %s has been armed" % self.id, 'deadmansswitchwarning')
            self.save()


class SwitchPhase(object):
    PHASE_0 = 0  # The dead man's switch is not armed yet
    PHASE_1 = 1  # The dead man's switch has been armed
    PHASE_2 = 2  # The dead man's switch has been armed and 1 warning has been sent (50% of timeout has passed)
    PHASE_3 = 3  # The dead man's switch has been armed and 2 warnings has been sent (75% of timeout has passed)
    PHASE_4 = 4  # The dead man's switch has been armed and 3 warnings has been sent (90% of timeout has passed)
    PHASE_5 = 5  # The dead man's switch has been activated


