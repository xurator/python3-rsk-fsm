"""A Python implementation of test FSM"""

# pylint: disable=invalid-name

STATE_A = 0
STATE_A_B = 1
STATE_A_C = 2
STATE_D = 3
STATE_D_E = 4
STATE_D_F = 5

def initial_transition(fsm, arg):
    """Transition into the initial state"""
    fsm.state = STATE_A
    fsm.callbacks.action_enter_A(fsm, arg)
    fsm.state = STATE_A_B
    fsm.callbacks.action_enter_B(fsm, arg)

def handle_X_in_A_B(fsm, arg):
    """Handle event X in state /A/B"""
    fsm.callbacks.action_exit_B(fsm, arg)
    fsm.state = STATE_A_B
    fsm.callbacks.action_jump(fsm, arg)
    fsm.state = STATE_A_C
    fsm.callbacks.action_enter_C(fsm, arg)

def handle_X_in_A_C(fsm, arg):
    """Handle event X in state /A/C"""
    fsm.callbacks.action_exit_C(fsm, arg)
    fsm.state = STATE_A_C
    fsm.callbacks.action_jump(fsm, arg)
    fsm.state = STATE_A_B
    fsm.callbacks.action_enter_B(fsm, arg)

def handle_X_in_D_E(fsm, arg):
    """Handle event X in state /D/E"""
    fsm.callbacks.action_exit_E(fsm, arg)
    fsm.state = STATE_D_E
    fsm.callbacks.action_jump(fsm, arg)
    fsm.state = STATE_D_F
    fsm.callbacks.action_enter_F(fsm, arg)

def handle_X_in_D_F(fsm, arg):
    """Handle event X in state /D/F"""
    fsm.callbacks.action_exit_F(fsm, arg)
    fsm.state = STATE_D_F
    fsm.callbacks.action_jump(fsm, arg)
    fsm.state = STATE_D_E
    fsm.callbacks.action_enter_E(fsm, arg)

TRANSITION_ON_EVENT_X = {
    STATE_A_B: handle_X_in_A_B,
    STATE_A_C: handle_X_in_A_C,
    STATE_D_E: handle_X_in_D_E,
    STATE_D_F: handle_X_in_D_F,
}

def handle_Y_in_A_C(fsm, arg):
    """Handle event Y in state /A/C"""
    fsm.callbacks.action_exit_C(fsm, arg)
    fsm.state = STATE_A_C
    fsm.callbacks.action_jump(fsm, arg)
    fsm.state = STATE_A

def handle_Y_in_D(fsm, arg):
    """Handle event Y in state /D"""
    fsm.callbacks.action_exit_D(fsm, arg)
    fsm.state = STATE_D
    fsm.state = None
    fsm.callbacks.action_done(fsm, arg)

def handle_Y_in_D_E(fsm, arg):
    """Handle event Y in state /D/E"""
    fsm.callbacks.action_exit_E(fsm, arg)
    fsm.state = STATE_D_E
    fsm.callbacks.action_exit_D(fsm, arg)
    fsm.state = STATE_D
    fsm.state = None
    fsm.callbacks.action_done(fsm, arg)

def handle_Y_in_D_F(fsm, arg):
    """Handle event Y in state /D/F"""
    fsm.callbacks.action_exit_F(fsm, arg)
    fsm.state = STATE_D_F
    fsm.callbacks.action_jump(fsm, arg)
    fsm.state = STATE_D

TRANSITION_ON_EVENT_Y = {
    STATE_A_C: handle_Y_in_A_C,
    STATE_D: handle_Y_in_D,
    STATE_D_E: handle_Y_in_D_E,
    STATE_D_F: handle_Y_in_D_F,
}

def handle_Z_in_A(fsm, arg):
    """Handle event Z in state /A"""
    if fsm.callbacks.condition_check(fsm, arg):
        fsm.callbacks.action_exit_A(fsm, arg)
        fsm.state = STATE_A
        fsm.callbacks.action_jump(fsm, arg)
        fsm.state = STATE_D
        fsm.callbacks.action_enter_D(fsm, arg)
        fsm.state = STATE_D_E
        fsm.callbacks.action_enter_E(fsm, arg)
        return
    if not fsm.callbacks.condition_check(fsm, arg):
        fsm.callbacks.action_exit_A(fsm, arg)
        fsm.state = STATE_A
        fsm.callbacks.action_jump(fsm, arg)
        fsm.state = STATE_D
        fsm.callbacks.action_enter_D(fsm, arg)
        fsm.state = STATE_D_F
        fsm.callbacks.action_enter_F(fsm, arg)
        return

def handle_Z_in_A_B(fsm, arg):
    """Handle event Z in state /A/B"""
    if fsm.callbacks.condition_check(fsm, arg):
        fsm.callbacks.action_exit_B(fsm, arg)
        fsm.state = STATE_A_B
        fsm.callbacks.action_exit_A(fsm, arg)
        fsm.state = STATE_A
        fsm.callbacks.action_jump(fsm, arg)
        fsm.state = STATE_D
        fsm.callbacks.action_enter_D(fsm, arg)
        fsm.state = STATE_D_E
        fsm.callbacks.action_enter_E(fsm, arg)
        return
    if not fsm.callbacks.condition_check(fsm, arg):
        fsm.callbacks.action_exit_B(fsm, arg)
        fsm.state = STATE_A_B
        fsm.callbacks.action_exit_A(fsm, arg)
        fsm.state = STATE_A
        fsm.callbacks.action_jump(fsm, arg)
        fsm.state = STATE_D
        fsm.callbacks.action_enter_D(fsm, arg)
        fsm.state = STATE_D_F
        fsm.callbacks.action_enter_F(fsm, arg)
        return

def handle_Z_in_A_C(fsm, arg):
    """Handle event Z in state /A/C"""
    if fsm.callbacks.condition_check(fsm, arg):
        fsm.callbacks.action_exit_C(fsm, arg)
        fsm.state = STATE_A_C
        fsm.callbacks.action_exit_A(fsm, arg)
        fsm.state = STATE_A
        fsm.callbacks.action_jump(fsm, arg)
        fsm.state = STATE_D
        fsm.callbacks.action_enter_D(fsm, arg)
        fsm.state = STATE_D_E
        fsm.callbacks.action_enter_E(fsm, arg)
        return
    if not fsm.callbacks.condition_check(fsm, arg):
        fsm.callbacks.action_exit_C(fsm, arg)
        fsm.state = STATE_A_C
        fsm.callbacks.action_exit_A(fsm, arg)
        fsm.state = STATE_A
        fsm.callbacks.action_jump(fsm, arg)
        fsm.state = STATE_D
        fsm.callbacks.action_enter_D(fsm, arg)
        fsm.state = STATE_D_F
        fsm.callbacks.action_enter_F(fsm, arg)
        return

TRANSITION_ON_EVENT_Z = {
    STATE_A: handle_Z_in_A,
    STATE_A_B: handle_Z_in_A_B,
    STATE_A_C: handle_Z_in_A_C,
}

class Callbacks():
    """Interface for test FSM condition and action callbacks"""
    @staticmethod
    def condition_check(fsm, arg):
        """Callback for test FSM condition check"""
        raise NotImplementedError
    @staticmethod
    def action_done(fsm, arg):
        """Callback for test FSM action done"""
        raise NotImplementedError
    @staticmethod
    def action_enter_A(fsm, arg):
        """Callback for test FSM action enter_A"""
        raise NotImplementedError
    @staticmethod
    def action_enter_B(fsm, arg):
        """Callback for test FSM action enter_B"""
        raise NotImplementedError
    @staticmethod
    def action_enter_C(fsm, arg):
        """Callback for test FSM action enter_C"""
        raise NotImplementedError
    @staticmethod
    def action_enter_D(fsm, arg):
        """Callback for test FSM action enter_D"""
        raise NotImplementedError
    @staticmethod
    def action_enter_E(fsm, arg):
        """Callback for test FSM action enter_E"""
        raise NotImplementedError
    @staticmethod
    def action_enter_F(fsm, arg):
        """Callback for test FSM action enter_F"""
        raise NotImplementedError
    @staticmethod
    def action_exit_A(fsm, arg):
        """Callback for test FSM action exit_A"""
        raise NotImplementedError
    @staticmethod
    def action_exit_B(fsm, arg):
        """Callback for test FSM action exit_B"""
        raise NotImplementedError
    @staticmethod
    def action_exit_C(fsm, arg):
        """Callback for test FSM action exit_C"""
        raise NotImplementedError
    @staticmethod
    def action_exit_D(fsm, arg):
        """Callback for test FSM action exit_D"""
        raise NotImplementedError
    @staticmethod
    def action_exit_E(fsm, arg):
        """Callback for test FSM action exit_E"""
        raise NotImplementedError
    @staticmethod
    def action_exit_F(fsm, arg):
        """Callback for test FSM action exit_F"""
        raise NotImplementedError
    @staticmethod
    def action_jump(fsm, arg):
        """Callback for test FSM action jump"""
        raise NotImplementedError

class Fsm():
    """A class for test FSM instances"""
    def __init__(self, callbacks=None, data=None, arg=None):
        self.state = None
        self.callbacks = self if callbacks is None else callbacks
        self.data = self if data is None else data
        initial_transition(self, arg)
    def inject_X(self, arg=None):
        """Inject event X with event `arg`"""
        try:
            TRANSITION_ON_EVENT_X[self.state](self, arg)
        except KeyError:
            pass
    def inject_Y(self, arg=None):
        """Inject event Y with event `arg`"""
        try:
            TRANSITION_ON_EVENT_Y[self.state](self, arg)
        except KeyError:
            pass
    def inject_Z(self, arg=None):
        """Inject event Z with event `arg`"""
        try:
            TRANSITION_ON_EVENT_Z[self.state](self, arg)
        except KeyError:
            pass
