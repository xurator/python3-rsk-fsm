typedef struct test_fsm_tag test_fsm_t;
typedef struct test_fsm_cb_tag test_fsm_cb_t;

typedef int (*condition_fp)(test_fsm_t * fsm, void * arg);
typedef void (*action_fp)(test_fsm_t * fsm, void * arg);

struct test_fsm_cb_tag {
	condition_fp condition_check;
	action_fp action_done;
	action_fp action_enter_A;
	action_fp action_enter_B;
	action_fp action_enter_C;
	action_fp action_enter_D;
	action_fp action_enter_E;
	action_fp action_enter_F;
	action_fp action_exit_A;
	action_fp action_exit_B;
	action_fp action_exit_C;
	action_fp action_exit_D;
	action_fp action_exit_E;
	action_fp action_exit_F;
	action_fp action_jump;
};

struct test_fsm_tag {
	test_fsm_cb_t * cb;
	void * data;
	int state;
};

extern void test_fsm_init(test_fsm_t * fsm, test_fsm_cb_t * cb, void * data, void * arg);
extern void test_fsm_inject_X(test_fsm_t * fsm, void * arg);
extern void test_fsm_inject_Y(test_fsm_t * fsm, void * arg);
extern void test_fsm_inject_Z(test_fsm_t * fsm, void * arg);

/* EOF */
