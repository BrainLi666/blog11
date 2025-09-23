#!/bin/bash

# 设置脚本在任何命令失败时退出
set -e

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "未激活虚拟环境，尝试激活..."
    if [ -d "venv" ]; then
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        elif [ -f "venv/Scripts/activate" ]; then
            source venv/Scripts/activate
        else
            echo "无法找到虚拟环境激活脚本。请手动激活虚拟环境后再运行此脚本。"
            exit 1
        fi
        echo "虚拟环境已激活"
    else
        echo "未找到虚拟环境。请先创建虚拟环境并安装依赖。"
        exit 1
    fi
fi

# 安装依赖
install_deps() {
    echo "正在安装项目依赖..."
    pip install -r requirements.txt
    echo "依赖安装完成！"
}

# 初始化数据库和示例数据
init_data() {
    echo "正在初始化数据库和示例数据..."
    python init_data.py
}

# 启动开发服务器
start_dev() {
    echo "正在启动开发服务器..."
    flask run
}

# 显示帮助信息
show_help() {
    echo "使用方法: ./run.sh [选项]"
    echo "选项:" 
    echo "  --install    安装项目依赖"
    echo "  --init       初始化数据库和示例数据"
    echo "  --dev        启动开发服务器"
    echo "  --all        执行安装、初始化并启动开发服务器"
    echo "  --help       显示帮助信息"
}

# 处理命令行参数
case "$1" in
    --install)
        install_deps
        ;;
    --init)
        init_data
        ;;
    --dev)
        start_dev
        ;;
    --all)
        install_deps
        init_data
        start_dev
        ;;
    --help)
        show_help
        ;;
    *)
        echo "欢迎使用轻量级个人博客系统！"
        echo "请指定一个选项来执行相应操作。例如："
        echo "  ./run.sh --install  # 安装依赖"
        echo "  ./run.sh --init     # 初始化数据"
        echo "  ./run.sh --dev      # 启动开发服务器"
        echo "  ./run.sh --all      # 执行所有操作"
        echo "使用 ./run.sh --help 查看所有选项。"
        ;;
esac