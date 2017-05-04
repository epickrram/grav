function check_command_contains_java() {
    COMMAND_CONTAINS_JAVA=$(grep java /proc/"$PID"/comm || true)
    export COMMAND_CONTAINS_JAVA
}