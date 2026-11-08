x="global"

show() {
    echo "$x"
}

run() {
    local x="local"
    show
}

run  # Prints: local
