#include <stdio.h>

#include "test_fsm.h"

#define NULL ((void *)0)

static int test_condition_check(test_fsm_t * fsm, void * arg) {
    int check = *(int *)arg > 1;
    printf("check? %d\n", check);
    return check;
}
static void test_action_done(test_fsm_t * fsm, void * arg) {
    printf("(done)\n");
}
static void test_action_enter_A(test_fsm_t * fsm, void * arg) {
    printf("enter A\n");
}
static void test_action_enter_B(test_fsm_t * fsm, void * arg) {
    printf("enter B\n");
}
static void test_action_enter_C(test_fsm_t * fsm, void * arg) {
    printf("enter C\n");
}
static void test_action_enter_D(test_fsm_t * fsm, void * arg) {
    printf("enter D\n");
}
static void test_action_enter_E(test_fsm_t * fsm, void * arg) {
    printf("enter E\n");
}
static void test_action_enter_F(test_fsm_t * fsm, void * arg) {
    printf("enter F\n");
}
static void test_action_exit_A(test_fsm_t * fsm, void * arg) {
    printf("exit A\n");
}
static void test_action_exit_B(test_fsm_t * fsm, void * arg) {
    printf("exit B\n");
}
static void test_action_exit_C(test_fsm_t * fsm, void * arg) {
    printf("exit C\n");
}
static void test_action_exit_D(test_fsm_t * fsm, void * arg) {
    printf("exit D\n");
}
static void test_action_exit_E(test_fsm_t * fsm, void * arg) {
    printf("exit E\n");
}
static void test_action_exit_F(test_fsm_t * fsm, void * arg) {
    printf("exit F\n");
}
static void test_action_jump(test_fsm_t * fsm, void * arg) {
    printf("jump!\n");
}

int main(int argc, char **argv) {
    test_fsm_t fsm;
    test_fsm_cb_t cb = {
        test_condition_check,
        test_action_done,
        test_action_enter_A,
        test_action_enter_B,
        test_action_enter_C,
        test_action_enter_D,
        test_action_enter_E,
        test_action_enter_F,
        test_action_exit_A,
        test_action_exit_B,
        test_action_exit_C,
        test_action_exit_D,
        test_action_exit_E,
        test_action_exit_F,
        test_action_jump,
    };
    printf("+++ init\n");
    test_fsm_init(&fsm, &cb, NULL, &argc);
    printf(">>> inject X\n");
    test_fsm_inject_X(&fsm, &argc);
    printf(">>> inject X\n");
    test_fsm_inject_X(&fsm, &argc);
    printf(">>> inject Z\n");
    test_fsm_inject_Z(&fsm, &argc);
    printf(">>> inject X\n");
    test_fsm_inject_X(&fsm, &argc);
    printf(">>> inject Y\n");
    test_fsm_inject_Y(&fsm, &argc);
    printf(">>> inject Y\n");
    test_fsm_inject_Y(&fsm, &argc);
    return 0;
}
