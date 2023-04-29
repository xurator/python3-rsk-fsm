#include "test_fsm.h"

typedef enum state_tag state_e;
typedef enum event_tag event_e;

enum state_tag {
	INVALID_STATE = -1,
	STATE_A = 0,
	STATE_A_B = 1,
	STATE_A_C = 2,
	STATE_D = 3,
	STATE_D_E = 4,
	STATE_D_F = 5,
	NUM_STATE = 6
};

enum event_tag {
	INVALID_EVENT = -1,
	EVENT_X = 0,
	EVENT_Y = 1,
	EVENT_Z = 2,
	NUM_EVENT = 3
};

typedef void (*inject_fp)(test_fsm_t * fsm, void * arg);

static void not_handled(test_fsm_t * fsm, void * arg) {
	/* empty */
}

static void handle_X_in_A_B(test_fsm_t * fsm, void * arg) {
	fsm->cb->action_exit_B(fsm, arg);
	fsm->state = STATE_A_B;
	fsm->cb->action_jump(fsm, arg);
	fsm->state = STATE_A_C;
	fsm->cb->action_enter_C(fsm, arg);
}
static void handle_X_in_A_C(test_fsm_t * fsm, void * arg) {
	fsm->cb->action_exit_C(fsm, arg);
	fsm->state = STATE_A_C;
	fsm->cb->action_jump(fsm, arg);
	fsm->state = STATE_A_B;
	fsm->cb->action_enter_B(fsm, arg);
}
static void handle_X_in_D_E(test_fsm_t * fsm, void * arg) {
	fsm->cb->action_exit_E(fsm, arg);
	fsm->state = STATE_D_E;
	fsm->cb->action_jump(fsm, arg);
	fsm->state = STATE_D_F;
	fsm->cb->action_enter_F(fsm, arg);
}
static void handle_X_in_D_F(test_fsm_t * fsm, void * arg) {
	fsm->cb->action_exit_F(fsm, arg);
	fsm->state = STATE_D_F;
	fsm->cb->action_jump(fsm, arg);
	fsm->state = STATE_D_E;
	fsm->cb->action_enter_E(fsm, arg);
}
static void handle_Y_in_A_C(test_fsm_t * fsm, void * arg) {
	fsm->cb->action_exit_C(fsm, arg);
	fsm->state = STATE_A_C;
	fsm->cb->action_jump(fsm, arg);
	fsm->state = STATE_A;
}
static void handle_Y_in_D(test_fsm_t * fsm, void * arg) {
	fsm->cb->action_exit_D(fsm, arg);
	fsm->state = STATE_D;
	fsm->state = INVALID_STATE;
	fsm->cb->action_done(fsm, arg);
}
static void handle_Y_in_D_E(test_fsm_t * fsm, void * arg) {
	fsm->cb->action_exit_E(fsm, arg);
	fsm->state = STATE_D_E;
	fsm->cb->action_exit_D(fsm, arg);
	fsm->state = STATE_D;
	fsm->state = INVALID_STATE;
	fsm->cb->action_done(fsm, arg);
}
static void handle_Y_in_D_F(test_fsm_t * fsm, void * arg) {
	fsm->cb->action_exit_F(fsm, arg);
	fsm->state = STATE_D_F;
	fsm->cb->action_jump(fsm, arg);
	fsm->state = STATE_D;
}
static void handle_Z_in_A(test_fsm_t * fsm, void * arg) {
	if (fsm->cb->condition_check(fsm, arg)) {
		fsm->cb->action_exit_A(fsm, arg);
		fsm->state = STATE_A;
		fsm->cb->action_jump(fsm, arg);
		fsm->state = STATE_D;
		fsm->cb->action_enter_D(fsm, arg);
		fsm->state = STATE_D_E;
		fsm->cb->action_enter_E(fsm, arg);
		return;
	}
	if (!(fsm->cb->condition_check(fsm, arg))) {
		fsm->cb->action_exit_A(fsm, arg);
		fsm->state = STATE_A;
		fsm->cb->action_jump(fsm, arg);
		fsm->state = STATE_D;
		fsm->cb->action_enter_D(fsm, arg);
		fsm->state = STATE_D_F;
		fsm->cb->action_enter_F(fsm, arg);
		return;
	}
}
static void handle_Z_in_A_B(test_fsm_t * fsm, void * arg) {
	if (fsm->cb->condition_check(fsm, arg)) {
		fsm->cb->action_exit_B(fsm, arg);
		fsm->state = STATE_A_B;
		fsm->cb->action_exit_A(fsm, arg);
		fsm->state = STATE_A;
		fsm->cb->action_jump(fsm, arg);
		fsm->state = STATE_D;
		fsm->cb->action_enter_D(fsm, arg);
		fsm->state = STATE_D_E;
		fsm->cb->action_enter_E(fsm, arg);
		return;
	}
	if (!(fsm->cb->condition_check(fsm, arg))) {
		fsm->cb->action_exit_B(fsm, arg);
		fsm->state = STATE_A_B;
		fsm->cb->action_exit_A(fsm, arg);
		fsm->state = STATE_A;
		fsm->cb->action_jump(fsm, arg);
		fsm->state = STATE_D;
		fsm->cb->action_enter_D(fsm, arg);
		fsm->state = STATE_D_F;
		fsm->cb->action_enter_F(fsm, arg);
		return;
	}
}
static void handle_Z_in_A_C(test_fsm_t * fsm, void * arg) {
	if (fsm->cb->condition_check(fsm, arg)) {
		fsm->cb->action_exit_C(fsm, arg);
		fsm->state = STATE_A_C;
		fsm->cb->action_exit_A(fsm, arg);
		fsm->state = STATE_A;
		fsm->cb->action_jump(fsm, arg);
		fsm->state = STATE_D;
		fsm->cb->action_enter_D(fsm, arg);
		fsm->state = STATE_D_E;
		fsm->cb->action_enter_E(fsm, arg);
		return;
	}
	if (!(fsm->cb->condition_check(fsm, arg))) {
		fsm->cb->action_exit_C(fsm, arg);
		fsm->state = STATE_A_C;
		fsm->cb->action_exit_A(fsm, arg);
		fsm->state = STATE_A;
		fsm->cb->action_jump(fsm, arg);
		fsm->state = STATE_D;
		fsm->cb->action_enter_D(fsm, arg);
		fsm->state = STATE_D_F;
		fsm->cb->action_enter_F(fsm, arg);
		return;
	}
}

static inject_fp transition_on_event_X[NUM_STATE] = {
	not_handled,
	handle_X_in_A_B,
	handle_X_in_A_C,
	not_handled,
	handle_X_in_D_E,
	handle_X_in_D_F,
};
static inject_fp transition_on_event_Y[NUM_STATE] = {
	not_handled,
	not_handled,
	handle_Y_in_A_C,
	handle_Y_in_D,
	handle_Y_in_D_E,
	handle_Y_in_D_F,
};
static inject_fp transition_on_event_Z[NUM_STATE] = {
	handle_Z_in_A,
	handle_Z_in_A_B,
	handle_Z_in_A_C,
	not_handled,
	not_handled,
	not_handled,
};

void test_fsm_init(test_fsm_t * fsm, test_fsm_cb_t * cb, void * data, void * arg) {
	fsm->cb = cb;
	fsm->data = data;
	fsm->state = STATE_A;
	fsm->cb->action_enter_A(fsm, arg);
	fsm->state = STATE_A_B;
	fsm->cb->action_enter_B(fsm, arg);
}
void test_fsm_inject_X(test_fsm_t * fsm, void * arg) {
	if ((0 <= fsm->state) && (fsm->state < NUM_STATE)) {
		transition_on_event_X[fsm->state](fsm, arg);
	}
}
void test_fsm_inject_Y(test_fsm_t * fsm, void * arg) {
	if ((0 <= fsm->state) && (fsm->state < NUM_STATE)) {
		transition_on_event_Y[fsm->state](fsm, arg);
	}
}
void test_fsm_inject_Z(test_fsm_t * fsm, void * arg) {
	if ((0 <= fsm->state) && (fsm->state < NUM_STATE)) {
		transition_on_event_Z[fsm->state](fsm, arg);
	}
}

/* EOF */
